"""Run one MACE-OFF23 model over the released SPICE test file and dump per-config errors.

Writes one CSV row per configuration: index, config_type, n_atoms, abs energy error
per atom, sum of |force component error|, sum of |force vector error|, and the
reference force diagnostics the A2 alternative needs. All aggregation happens in
compare.py, so the heavy run is done once per model and never again.
"""
import argparse
import csv
import os
import time

import numpy as np
import torch
from ase.io import iread

# Keep the machine usable: the user is working on this PC.
torch.set_num_threads(int(os.environ.get("OMP_NUM_THREADS", "6")))

from mace import data
from mace.tools import torch_geometric, utils


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--xyz", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--batch-size", type=int, default=4)
    ap.add_argument("--max-atoms-per-batch", type=int, default=400)
    ap.add_argument("--resume", action="store_true",
                    help="append to an existing output and skip the configs already in it")
    args = ap.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cuda":
        # At most half of the 8 GB card, the user is on this machine.
        torch.cuda.set_per_process_memory_fraction(0.5)
    torch.set_default_dtype(torch.float64)

    model = torch.load(args.model, map_location=device)
    model = model.to(device).double()
    model.eval()
    for p in model.parameters():
        p.requires_grad = False

    z_table = utils.AtomicNumberTable([int(z) for z in model.atomic_numbers])
    r_max = float(model.r_max)

    # Resume: the large model takes hours, and an OOM half way through should not
    # cost the whole run.
    done_until = -1
    if args.resume and os.path.exists(args.out):
        with open(args.out, newline="") as old:
            for row in csv.reader(old):
                if row and row[0].isdigit():
                    done_until = max(done_until, int(row[0]))
        print(f"resuming after index {done_until}", flush=True)
        fh = open(args.out, "a", newline="")
        w = csv.writer(fh)
    else:
        fh = open(args.out, "w", newline="")
        w = csv.writer(fh)
        w.writerow([
            "index", "config_type", "n_atoms",
            "abs_e_err_per_atom_eV", "sum_abs_f_comp_err_eV_A", "sum_abs_f_vec_err_eV_A",
            "ref_max_abs_f_eV_A", "ref_sum_f_norm_eV_A",
        ])

    t0 = time.time()
    index = 0
    batch_atoms, batch_meta = [], []

    cpu_model = [None]  # last resort for a configuration that will not fit in half the card

    def run_one_on_cpu(atoms, meta):
        if cpu_model[0] is None:
            m = torch.load(args.model, map_location="cpu")
            cpu_model[0] = m.to("cpu").double().eval()
        run_batch([atoms], [meta], dev="cpu", mdl=cpu_model[0])

    def flush(batch_atoms, batch_meta):
        """Score a batch. On a CUDA OOM, fall back to one config at a time, then to the CPU.

        Nothing is ever skipped: the test set has to stay complete.
        """
        if not batch_atoms:
            return
        try:
            run_batch(batch_atoms, batch_meta)
        except RuntimeError as exc:
            # A TorchScript module wraps the CUDA OOM in a plain RuntimeError, so
            # the message is the only reliable test.
            if "out of memory" not in str(exc).lower():
                raise
            torch.cuda.empty_cache()
            if len(batch_atoms) == 1:
                print(f"OOM on a single config (index {batch_meta[0][0]}, "
                      f"{batch_meta[0][2]} atoms), running it on the CPU", flush=True)
                run_one_on_cpu(batch_atoms[0], batch_meta[0])
            else:
                print(f"OOM on a batch of {len(batch_atoms)}, splitting", flush=True)
                for a, m in zip(list(batch_atoms), list(batch_meta)):
                    flush([a], [m])
        batch_atoms.clear()
        batch_meta.clear()

    def run_batch(batch_atoms, batch_meta, dev=None, mdl=None):
        dev = dev or device
        mdl = mdl or model
        confs = [
            data.Configuration(
                atomic_numbers=a.get_atomic_numbers(),
                positions=a.get_positions(),
                energy=0.0,
                forces=np.zeros_like(a.get_positions()),
                pbc=tuple(a.get_pbc()),
                cell=np.array(a.get_cell()),
            )
            for a in batch_atoms
        ]
        dataset = [data.AtomicData.from_config(c, z_table=z_table, cutoff=r_max) for c in confs]
        loader = torch_geometric.dataloader.DataLoader(
            dataset=dataset, batch_size=len(dataset), shuffle=False, drop_last=False
        )
        for batch in loader:
            batch = batch.to(dev)
            out = mdl(batch.to_dict(), compute_force=True, training=False)
            e_pred = out["energy"].detach().cpu().numpy()
            f_pred = out["forces"].detach().cpu().numpy()
            off = 0
            for k, (idx, ctype, nat, e_ref, f_ref) in enumerate(batch_meta):
                fp = f_pred[off:off + nat]
                off += nat
                df = fp - f_ref
                w.writerow([
                    idx, ctype, nat,
                    abs(e_pred[k] - e_ref) / nat,
                    np.abs(df).sum(),
                    np.linalg.norm(df, axis=1).sum(),
                    np.abs(f_ref).max(),
                    np.linalg.norm(f_ref.sum(axis=0)),
                ])

    for atoms in iread(args.xyz, index=":", format="extxyz"):
        if index <= done_until:
            index += 1
            continue
        nat = len(atoms)
        # ASE moves energy/forces of an extxyz frame into a SinglePointCalculator
        # and drops them from info/arrays, so take whichever place they landed in.
        if "energy" in atoms.info:
            e_ref = float(atoms.info["energy"])
        else:
            e_ref = float(atoms.calc.results["energy"])
        if "forces" in atoms.arrays:
            f_ref = np.array(atoms.arrays["forces"], dtype=float)
        else:
            f_ref = np.array(atoms.calc.results["forces"], dtype=float)
        batch_atoms.append(atoms)
        batch_meta.append((index, atoms.info.get("config_type", "?"), nat, e_ref, f_ref))
        index += 1
        # Cap by atom count as well, because water clusters reach 150 atoms
        # while PubChem monomers are 3.
        if len(batch_atoms) >= args.batch_size or sum(m[2] for m in batch_meta) >= args.max_atoms_per_batch:
            flush(batch_atoms, batch_meta)
        if index % 2000 == 0:
            print(f"{index} configs, {time.time() - t0:.0f} s", flush=True)
            fh.flush()
            if device == "cuda":
                # Half the card is a tight budget; fragmentation is what killed
                # the first large run.
                torch.cuda.empty_cache()
    flush(batch_atoms, batch_meta)
    fh.close()
    print(f"done: {index} configs in {time.time() - t0:.0f} s -> {args.out}", flush=True)


if __name__ == "__main__":
    main()
