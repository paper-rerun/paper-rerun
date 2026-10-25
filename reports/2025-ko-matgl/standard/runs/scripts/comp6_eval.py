"""COMP6 single-point evaluation for the MatGL ANI-1x-Subset potentials (matgl 1.3.0).

Writes one .npz per (model, file) with every conformation's reference and predicted
energy (eV) and forces (eV/A). Scoring lives in score.py. Restartable: finished
(model, file) pairs are skipped.

Usage:
  python comp6_eval.py run   --model M3GNet --h5 <file> --out <dir> [--mode batch|calc] [--device cuda]
  python comp6_eval.py check --model M3GNet --h5 <file> --out <dir> [--n 50]
  python comp6_eval.py units --out <dir>
"""
import argparse
import json
import os
import sys
import time

import dgl
import h5py
import numpy as np
import torch
from ase import Atoms

import matgl
from matgl.ext.ase import Atoms2Graph, PESCalculator

HARTREE_TO_EV = 27.211386245988  # CODATA 2018
ROOT = "/mnt/e/Ciencia/noturno/2025-ko-matgl"
MODEL_DIRS = {
    "M3GNet": f"{ROOT}/data/matgl/pretrained_models/M3GNet-ANI-1x-Subset-PES",
    "SO3Net": f"{ROOT}/data/matgl/pretrained_models/SO3Net-ANI-1x-Subset-PES",
    "TensorNet": f"{ROOT}/data/matgl/pretrained_models/TensorNet-ANI-1x-Subset-PES",
}
ALLOWED_ELEMENTS = {"H", "C", "N", "O"}
MAX_ATOMS_PER_BATCH = 4000


def load_potential(model_name, device):
    # Load from the local v1.3.0 checkout, the by-name download URL is dead (issue #680)
    potential = matgl.load_model(MODEL_DIRS[model_name])
    potential = potential.to(device)
    potential.eval()
    return potential


def read_conformations(h5_path):
    """Yield (molecule_key, species list, coordinates[n_conf, n_atoms, 3], energies_Ha[n_conf], forces_Ha_per_A)."""
    with h5py.File(h5_path, "r") as h5_file:
        molecule_keys = []

        def collect(name, obj):
            if isinstance(obj, h5py.Group) and "coordinates" in obj:
                molecule_keys.append(name)

        h5_file.visititems(collect)
        for molecule_key in molecule_keys:
            group = h5_file[molecule_key]
            species = [s.decode() if isinstance(s, bytes) else str(s) for s in group["species"][()]]
            yield (
                molecule_key,
                species,
                group["coordinates"][()],
                group["energies"][()],
                group["forces"][()],
            )


def predict_batch(potential, converter, atoms_list, device):
    """One batched Potential call over many molecules. Returns energies (B,) and list of force arrays."""
    graphs = []
    states = []
    for atoms in atoms_list:
        graph, _, state_attr = converter.get_graph(atoms)
        graphs.append(graph)
        states.append(state_attr)
    batched_graph = dgl.batch(graphs).to(device)
    # Non-periodic molecules: matgl uses an identity lattice and cartesian coords as "frac_coords"
    lattice = torch.eye(3, dtype=matgl.float_th).unsqueeze(0).repeat(len(atoms_list), 1, 1).to(device)
    state_tensor = torch.tensor(np.stack(states), dtype=matgl.float_th).to(device)
    result = potential(batched_graph, lattice, state_tensor)
    energies = result[0].detach().reshape(-1).cpu().numpy().astype(np.float64)
    forces = result[1].detach().cpu().numpy()
    split_points = np.cumsum([len(a) for a in atoms_list])[:-1]
    return energies, np.split(forces, split_points)


def predict_calc(calculator, atoms):
    atoms.calc = calculator
    energy = atoms.get_potential_energy()
    forces = atoms.get_forces()
    return float(energy), np.array(forces)


def out_path(out_dir, model_name, h5_path):
    return os.path.join(out_dir, f"{model_name}__{os.path.basename(h5_path).replace('.h5', '')}.npz")


def run(model_name, h5_path, out_dir, mode, device):
    target = out_path(out_dir, model_name, h5_path)
    if os.path.exists(target):
        print(f"skip {target}", flush=True)
        return
    potential = load_potential(model_name, device)
    converter = Atoms2Graph(potential.model.element_types, potential.model.cutoff)
    calculator = PESCalculator(potential) if mode == "calc" else None

    molecule_index, conformation_index, n_atoms_list = [], [], []
    energy_ref, energy_pred = [], []
    forces_ref_all, forces_pred_all, excluded = [], [], []
    molecule_names = []
    start_time = time.time()

    pending_atoms, pending_meta = [], []

    def flush():
        if not pending_atoms:
            return
        energies, forces = predict_batch(potential, converter, pending_atoms, device)
        for (mol_i, conf_i, e_ref, f_ref), e_pred, f_pred in zip(pending_meta, energies, forces):
            molecule_index.append(mol_i)
            conformation_index.append(conf_i)
            n_atoms_list.append(len(f_ref))
            energy_ref.append(e_ref)
            energy_pred.append(e_pred)
            forces_ref_all.append(f_ref)
            forces_pred_all.append(f_pred.astype(np.float32))
        pending_atoms.clear()
        pending_meta.clear()

    for mol_i, (molecule_key, species, coords, energies_ha, forces_ha) in enumerate(read_conformations(h5_path)):
        molecule_names.append(molecule_key)
        for conf_i in range(coords.shape[0]):
            e_ref = float(energies_ha[conf_i]) * HARTREE_TO_EV
            # COMP6 "forces" are energy gradients in Ha/A: units check gave slope -0.93 and -0.998 (runs/out/units_check.json)
            f_ref = -forces_ha[conf_i].astype(np.float64) * HARTREE_TO_EV
            # D-FILTER: only drop unknown elements or non-finite references
            if not set(species) <= ALLOWED_ELEMENTS or not np.isfinite(e_ref) or not np.isfinite(f_ref).all():
                excluded.append(f"{molecule_key}/{conf_i}")
                continue
            atoms = Atoms(symbols=species, positions=coords[conf_i].astype(np.float64), pbc=False)
            if mode == "calc":
                e_pred, f_pred = predict_calc(calculator, atoms)
                molecule_index.append(mol_i)
                conformation_index.append(conf_i)
                n_atoms_list.append(len(species))
                energy_ref.append(e_ref)
                energy_pred.append(e_pred)
                forces_ref_all.append(f_ref)
                forces_pred_all.append(f_pred.astype(np.float32))
            else:
                if sum(len(a) for a in pending_atoms) + len(atoms) > MAX_ATOMS_PER_BATCH:
                    flush()
                pending_atoms.append(atoms)
                pending_meta.append((mol_i, conf_i, e_ref, f_ref))
    flush()

    tmp_target = target + ".tmp.npz"
    np.savez_compressed(
        tmp_target,
        molecule_names=np.array(molecule_names),
        molecule_index=np.array(molecule_index),
        conformation_index=np.array(conformation_index),
        n_atoms=np.array(n_atoms_list),
        energy_ref_eV=np.array(energy_ref),
        energy_pred_eV=np.array(energy_pred),
        forces_ref_eV_per_A=np.concatenate(forces_ref_all).astype(np.float32),
        forces_pred_eV_per_A=np.concatenate(forces_pred_all),
        excluded=np.array(excluded),
        meta=json.dumps({"model": model_name, "h5": h5_path, "mode": mode, "device": device,
                         "seconds": time.time() - start_time, "matgl": matgl.__version__,
                         "torch": torch.__version__, "dgl": dgl.__version__}),
    )
    os.replace(tmp_target, target)
    print(f"done {target} confs={len(energy_ref)} excluded={len(excluded)} {time.time() - start_time:.0f}s", flush=True)


def check(model_name, h5_path, out_dir, n_sample, device):
    """D-SCORING: batched path must agree with PESCalculator on >= 50 conformations per file."""
    potential = load_potential(model_name, device)
    converter = Atoms2Graph(potential.model.element_types, potential.model.cutoff)
    calculator = PESCalculator(potential)
    all_atoms = []
    for molecule_key, species, coords, _, _ in read_conformations(h5_path):
        for conf_i in range(coords.shape[0]):
            all_atoms.append(Atoms(symbols=species, positions=coords[conf_i].astype(np.float64), pbc=False))
    # Fixed spread over the file, no randomness
    picks = np.linspace(0, len(all_atoms) - 1, n_sample).round().astype(int)
    sample = [all_atoms[i] for i in picks]
    calc_results = [predict_calc(calculator, a.copy()) for a in sample]
    batch_energies, batch_forces = predict_batch(potential, converter, sample, device)
    energy_diff = np.abs(np.array([c[0] for c in calc_results]) - batch_energies)
    force_diff = max(np.abs(c[1] - f).max() for c, f in zip(calc_results, batch_forces))
    report = {"model": model_name, "file": os.path.basename(h5_path), "n": int(n_sample),
              "max_abs_dE_eV": float(energy_diff.max()), "max_abs_dF_eV_per_A": float(force_diff),
              "max_abs_E_eV": float(np.abs(batch_energies).max()),
              "pass_1e-4": bool(energy_diff.max() <= 1e-4 and force_diff <= 1e-4)}
    print(json.dumps(report), flush=True)
    with open(os.path.join(out_dir, "check_batch_vs_calc.jsonl"), "a") as handle:
        handle.write(json.dumps(report) + "\n")


def units(out_dir, device):
    """D-UNITS: slope of predicted vs reference force components on two molecules (M3GNet)."""
    potential = load_potential("M3GNet", device)
    calculator = PESCalculator(potential)
    lines = []
    for h5_path in [f"{ROOT}/data/COMP6/COMP6v1/s66x8/s66x8_wb97x6-31gd.h5",
                    f"{ROOT}/data/COMP6/COMP6v1/ANI-MD/ani_md_bench.h5"]:
        molecule_key, species, coords, energies_ha, forces_ha = next(read_conformations(h5_path))
        pred, ref, e_pairs = [], [], []
        for conf_i in range(min(8, coords.shape[0])):
            atoms = Atoms(symbols=species, positions=coords[conf_i].astype(np.float64), pbc=False)
            e_pred, f_pred = predict_calc(calculator, atoms)
            pred.append(f_pred.ravel())
            ref.append(forces_ha[conf_i].ravel() * HARTREE_TO_EV)
            e_pairs.append((e_pred, energies_ha[conf_i] * HARTREE_TO_EV, len(species)))
        pred = np.concatenate(pred)
        ref = np.concatenate(ref)
        slope = float(np.dot(pred, ref) / np.dot(ref, ref))
        corr = float(np.corrcoef(pred, ref)[0, 1])
        e_per_atom = [abs(p - r) / n * 1000 for p, r, n in e_pairs]
        line = {"file": os.path.basename(h5_path), "molecule": molecule_key, "n_confs": len(e_pairs),
                "force_slope_pred_vs_ref_HaA_to_eV": slope, "force_corr": corr,
                "energy_abs_err_meV_per_atom": e_per_atom,
                "example_E_pred_eV": e_pairs[0][0], "example_E_ref_eV": e_pairs[0][1]}
        print(json.dumps(line), flush=True)
        lines.append(line)
    with open(os.path.join(out_dir, "units_check.json"), "w") as handle:
        json.dump(lines, handle, indent=1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["run", "check", "units"])
    parser.add_argument("--model", default="M3GNet")
    parser.add_argument("--h5")
    parser.add_argument("--out", required=True)
    parser.add_argument("--mode", default="batch", choices=["batch", "calc"])
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--n", type=int, default=50)
    parser.add_argument("--max-atoms", type=int, default=MAX_ATOMS_PER_BATCH)
    args = parser.parse_args()
    MAX_ATOMS_PER_BATCH = args.max_atoms
    os.makedirs(args.out, exist_ok=True)
    if args.device == "cuda" and not (args.action == "run" and args.mode == "batch"):
        # PESCalculator does not move graphs to the model device, so make cuda the default
        torch.set_default_device("cuda")
    if args.action == "run":
        run(args.model, args.h5, args.out, args.mode, args.device)
    elif args.action == "check":
        check(args.model, args.h5, args.out, args.n, args.device)
    else:
        units(args.out, args.device)
    sys.exit(0)
