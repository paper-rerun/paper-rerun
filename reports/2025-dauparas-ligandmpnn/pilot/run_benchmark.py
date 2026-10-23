#!/usr/bin/env python3
"""
Drives the authors' run.py over the three PDB test splits and saves per-design stats.

Nothing in repo/ is touched. We only call run.py the way the README documents, with
the settings the paper states: ten sequences per protein, sampling temperature 0.1.
Structures are chunked through --pdb_path_multi so the checkpoint loads ~20 times
instead of 474; a chunk that dies is retried one PDB at a time so a single bad file
cannot take the rest down with it.
"""
import argparse
import json
import os
import subprocess
import sys
import time

ROOT = "/mnt/e/Ciencia/artigos/2025-dauparas-ligandmpnn"
REPO = os.path.join(ROOT, "repo")
PY = os.path.join(ROOT, ".venv/bin/python")
PDBS = os.path.join(ROOT, "pdbs")

# label -> (model_type, checkpoint flag, checkpoint)
MODELS = {
    # Paper's LigandMPNN baseline: 0.1 A noise, 25 context atoms. This is the checkpoint the
    # authors label "publication_version" in get_model_params.sh
    "ligand_mpnn": (
        "ligand_mpnn",
        "--checkpoint_ligand_mpnn",
        "model_params/publication_version_ligandmpnn_v_32_010_25.pt",
    ),
    # The paper's ProteinMPNN comparator was retrained on the LigandMPNN dataset with no
    # context atoms, so it shares LigandMPNN's 32 edges. That is this checkpoint.
    "protein_mpnn_32": ("protein_mpnn", "--checkpoint_protein_mpnn", "model_params/proteinmpnn_v_32_010.pt"),
    # Original published ProteinMPNN, 48 edges, for reference
    "protein_mpnn_48": ("protein_mpnn", "--checkpoint_protein_mpnn", "model_params/proteinmpnn_v_48_010.pt"),
    # Same LigandMPNN weights with the ligand context switched off: isolates the context gain
    "ligand_mpnn_nocontext": (
        "ligand_mpnn",
        "--checkpoint_ligand_mpnn",
        "model_params/publication_version_ligandmpnn_v_32_010_25.pt",
    ),
}


def run_chunk(label, ids, out_folder, batch_size, number_of_batches, timeout):
    multi = {os.path.join(PDBS, f"{i}.pdb"): "" for i in ids}
    multi_path = os.path.join(out_folder, "_multi.json")
    os.makedirs(out_folder, exist_ok=True)
    with open(multi_path, "w") as f:
        json.dump(multi, f)

    model_type, flag, ckpt = MODELS[label]
    cmd = [
        PY, "run.py",
        "--model_type", model_type,
        flag, ckpt,
        "--pdb_path_multi", multi_path,
        "--out_folder", out_folder,
        "--seed", "111",
        "--batch_size", str(batch_size),
        "--number_of_batches", str(number_of_batches),
        "--temperature", "0.1",
        "--save_stats", "1",
        "--verbose", "0",
    ]
    if label == "ligand_mpnn_nocontext":
        cmd += ["--ligand_mpnn_use_atom_context", "0"]
    p = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=timeout)
    return p


def ordered_ids():
    """Work order: the two small splits whole, then the small-molecule split shuffled.

    The GPU is shared with four other papers and we may get cut off mid-run. This order
    means a cutoff leaves the nucleotide and metal splits complete and the small-molecule
    split as a random sample (seed 0) rather than an alphabetical slice, which would be
    biased - the ids sort by deposition era.
    """
    import random

    def load(name):
        with open(os.path.join(REPO, "training", name)) as f:
            return json.load(f)

    have = lambda ids: [i for i in ids if os.path.exists(os.path.join(PDBS, f"{i}.pdb"))]
    nuc, met, sm = have(load("test_nucleotide.json")), have(load("test_metal.json")), have(load("test_small_molecule.json"))
    random.Random(0).shuffle(sm)
    out, seen = [], set()
    for i in nuc + met + sm:
        if i not in seen:  # a few ids sit in two splits
            seen.add(i)
            out.append(i)
    return out


def done_ids(out_folder, ids):
    stats = os.path.join(out_folder, "stats")
    return {i for i in ids if os.path.exists(os.path.join(stats, f"{i}.pt"))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model_type", required=True, choices=list(MODELS), help="label, not run.py's model_type")
    ap.add_argument("--chunk", type=int, default=20)
    ap.add_argument("--limit", type=int, default=0, help="debug: only first N ids")
    args = ap.parse_args()

    ids = ordered_ids()
    if args.limit:
        ids = ids[: args.limit]

    # The GPU is shared with four other papers, so a CPU run into its own tree can go in
    # parallel without the lock. Same settings, different device.
    out_root = os.environ.get("LMPNN_OUT_ROOT", os.path.join(ROOT, "outputs"))
    out_folder = os.path.join(out_root, args.model_type)
    os.makedirs(out_folder, exist_ok=True)

    todo = [i for i in ids if i not in done_ids(out_folder, ids)]
    print(f"{args.model_type}: {len(ids)} structures, {len(todo)} to do", flush=True)

    failed = []
    t0 = time.time()
    for k in range(0, len(todo), args.chunk):
        chunk = todo[k : k + args.chunk]
        p = run_chunk(args.model_type, chunk, out_folder, 10, 1, timeout=3600)
        got = done_ids(out_folder, chunk)
        missing = [i for i in chunk if i not in got]
        if p.returncode != 0 or missing:
            with open(os.path.join(out_folder, "chunk_errors.log"), "a") as f:
                f.write(f"\n=== chunk {k} rc={p.returncode} missing={len(missing)} ===\n")
                f.write((p.stderr or "")[-4000:])
            # One bad structure should not cost the chunk. Retry the leftovers alone,
            # and drop to batch 1 x 10 so an 8 GB card can still get through the big ones.
            for i in missing:
                ok = False
                for bs, nb in ((10, 1), (1, 10)):
                    try:
                        q = run_chunk(args.model_type, [i], out_folder, bs, nb, timeout=1800)
                    except subprocess.TimeoutExpired:
                        continue
                    if i in done_ids(out_folder, [i]):
                        ok = True
                        break
                if not ok:
                    failed.append((i, (q.stderr or "")[-600:]))
                    print(f"  FAIL {i}", flush=True)
        n = len(done_ids(out_folder, ids))
        print(f"  {n}/{len(ids)} done, {time.time()-t0:.0f}s", flush=True)

    with open(os.path.join(out_folder, "failed.json"), "w") as f:
        json.dump(failed, f, indent=1)
    print(f"finished: {len(done_ids(out_folder, ids))}/{len(ids)}, {len(failed)} failed, {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
