"""C5: regenerate the 52 x 5 benchmark sequences with the published base and
fine-tuned weights, CPU only, then recompute the Fig. 4a / 4b base-vs-fine-tuned
means with the same metric code used for C1 and C2.

Inference follows claims.json fixed_definitions.generation_for_C5: the 'protein
sequence only' route of the Methods, deterministic (no sampling), through the
authors' own published entry point predict_dna_sequence.
"""
import json
import os
import statistics
import sys

os.environ.setdefault("OMP_NUM_THREADS", "4")
os.environ.setdefault("MKL_NUM_THREADS", "4")
os.environ.setdefault("MPLBACKEND", "Agg")

import torch  # noqa: E402

torch.set_num_threads(4)

import openpyxl  # noqa: E402
from transformers import AutoTokenizer, BigBirdForMaskedLM  # noqa: E402
from CodonTransformer.CodonPrediction import predict_dna_sequence  # noqa: E402
from CodonTransformer.CodonUtils import ORGANISM2ID  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from recount import codons, jaccard, similarity, sheet_rows  # noqa: E402

WB = sys.argv[1]
OUT = sys.argv[2]

ORGS = [
    "Escherichia coli",
    "Saccharomyces cerevisiae",
    "Arabidopsis thaliana",
    "Mus musculus",
    "Homo sapiens",
]

REPOS = {
    "finetuned": "adibvafa/CodonTransformer",
    "base": "adibvafa/CodonTransformer-base",
}


def pick_organism(label):
    """Unique ORGANISM2ID key containing the binomial; prefer a 'general' variant."""
    cands = [k for k in ORGANISM2ID if label.lower() in k.lower()]
    if not cands:
        raise SystemExit(f"no ORGANISM2ID entry for {label!r}")
    gen = [c for c in cands if "general" in c.lower()]
    chosen = sorted(gen)[0] if gen else sorted(cands)[0]
    return chosen, sorted(cands)


def main():
    wb = openpyxl.load_workbook(WB, read_only=True, data_only=True)
    rows = [r for r in sheet_rows(wb, "DNA sequences, CSI, CIS-element") if r["organism"] in ORGS]
    print(f"{len(rows)} benchmark rows", flush=True)

    org_map = {}
    for o in ORGS:
        chosen, cands = pick_organism(o)
        org_map[o] = chosen
        print(f"organism {o!r} -> {chosen!r}  (candidates: {cands})", flush=True)

    out = {"organism_mapping": org_map, "sequences": {}, "model_revisions": {}}

    # The base repo ships only config.json, generation_config.json and model.safetensors:
    # no tokenizer. The tokenizer is shared between the two models, so it comes from the
    # fine-tuned repo for both. Recorded in the report as a reproducibility note.
    tok = AutoTokenizer.from_pretrained(REPOS["finetuned"])

    for tag, repo in REPOS.items():
        model = BigBirdForMaskedLM.from_pretrained(repo)
        model.eval()
        out["tokenizer_repo"] = REPOS["finetuned"]
        out["model_revisions"][tag] = {
            "repo": repo,
            "n_params": sum(p.numel() for p in model.parameters()),
        }
        for i, r in enumerate(rows):
            prot = str(r["protein sequence"]).strip().replace("*", "")
            with torch.no_grad():
                pred = predict_dna_sequence(
                    protein=prot,
                    organism=org_map[r["organism"]],
                    device=torch.device("cpu"),
                    tokenizer=tok,
                    model=model,
                    attention_type="original_full",
                    deterministic=True,
                )
            dna = pred.predicted_dna if hasattr(pred, "predicted_dna") else pred[0].predicted_dna
            key = f"{r['organism']}||{str(r['protein']).strip()}"
            out["sequences"].setdefault(key, {})[tag] = dna
            if i % 20 == 0:
                print(f"  {tag} {i}/{len(rows)}", flush=True)
        del model
        with open(OUT + ".partial", "w", encoding="utf-8") as fh:
            json.dump(out, fh)

    # metrics on my own sequences, same code as C1/C2
    jac, sim, skipped = [], [], []
    for key, d in out["sequences"].items():
        if "base" not in d or "finetuned" not in d:
            skipped.append(key)
            continue
        cb, cf = codons(d["base"]), codons(d["finetuned"])
        jac.append(jaccard(cb, cf))
        if len(cb) == len(cf):
            sim.append(similarity(cb, cf))
        else:
            skipped.append(f"{key} length {len(cb)} vs {len(cf)}")

    # also: how often my regenerated sequence equals the one in the Source Data
    exact = {"base": 0, "finetuned": 0, "n": 0}
    percodon = {"base": [], "finetuned": []}
    for r in rows:
        key = f"{r['organism']}||{str(r['protein']).strip()}"
        d = out["sequences"].get(key, {})
        exact["n"] += 1
        for tag, col in (("base", "pretrain_transformer_dna"), ("finetuned", "finetune_transformer_dna")):
            mine, theirs = d.get(tag), str(r[col]).strip().upper()
            if mine is None:
                continue
            mine = mine.strip().upper()
            if mine == theirs:
                exact[tag] += 1
            cm, ct = codons(mine), codons(theirs)
            if len(cm) == len(ct):
                percodon[tag].append(similarity(cm, ct))

    out["C5"] = {
        "jaccard": {"n": len(jac), "mean": statistics.fmean(jac), "sd": statistics.stdev(jac)},
        "sequence_similarity": {"n": len(sim), "mean": statistics.fmean(sim), "sd": statistics.stdev(sim)},
        "skipped": skipped,
    }
    out["agreement_with_source_data"] = {
        "n_rows": exact["n"],
        "exact_matches": {k: exact[k] for k in ("base", "finetuned")},
        "mean_codon_identity_vs_source_data": {
            k: (statistics.fmean(v) if v else None) for k, v in percodon.items()
        },
        "n_compared": {k: len(v) for k, v in percodon.items()},
    }

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2)
    print(json.dumps(out["C5"]["jaccard"]), json.dumps(out["C5"]["sequence_similarity"]))
    print(json.dumps(out["agreement_with_source_data"]))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
