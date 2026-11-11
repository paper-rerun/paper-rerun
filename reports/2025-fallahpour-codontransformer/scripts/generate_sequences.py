"""L3: regenerate the Fig. 4 benchmark DNA with the two released checkpoints, on CPU.

One row per (organism, protein, checkpoint). Deterministic decoding, 4 threads,
resumable: a row already in the output CSV is skipped. The authors' inference path
is used as published (CodonTransformer.CodonPrediction.predict_dna_sequence).

Usage: generate_sequences.py <out.csv> [--ecoli-token "Escherichia coli general"]
"""
import csv
import os
import re
import sys
import time

import openpyxl
import torch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.join(ROOT, "data", "repo")
WEIGHTS = os.path.join(ROOT, "data", "weights")
WB = os.path.join(ROOT, "data", "sourcedata", "unzipped", "Source Data",
                  "Fig. 4, Supplementary Fig. 19f-h, 20, 21, 22 and 25.xlsx")

sys.path.insert(0, REPO)  # the authors' package, run from its clone
from CodonTransformer.CodonPrediction import predict_dna_sequence  # noqa: E402
from transformers import AutoTokenizer, BigBirdForMaskedLM  # noqa: E402

torch.set_num_threads(4)
DEVICE = torch.device("cpu")

CHECKPOINTS = {
    "fine": os.path.join(WEIGHTS, "CodonTransformer"),
    "base": os.path.join(WEIGHTS, "CodonTransformer-base"),
}


def benchmark_rows():
    wb = openpyxl.load_workbook(WB, read_only=True, data_only=True)
    ws = wb["DNA sequences, CSI, CIS-element"]
    it = ws.iter_rows(values_only=True)
    head = [str(h) for h in next(it)]
    rows = []
    for raw in it:
        r = dict(zip(head, raw))
        if not r.get("protein"):
            continue
        rows.append({
            "organism": r["organism"],
            "protein": r["protein"],
            "protein_seq": re.sub(r"\s+", "", str(r["protein sequence"])),
            "authors_fine": r["finetune_transformer_dna"],
            "authors_base": r["pretrain_transformer_dna"],
        })
    wb.close()
    # Pre-registered order: organism alphabetical, protein in Source Data row order
    rows.sort(key=lambda r: r["organism"])
    return rows


def main():
    out_path = sys.argv[1]
    ecoli_token = "Escherichia coli general"
    if "--ecoli-token" in sys.argv:
        ecoli_token = sys.argv[sys.argv.index("--ecoli-token") + 1]

    rows = benchmark_rows()
    if "--only-organism" in sys.argv:
        only = sys.argv[sys.argv.index("--only-organism") + 1]
        rows = [r for r in rows if r["organism"] == only]
    print(f"{len(rows)} benchmark rows, E. coli token {ecoli_token!r}", flush=True)

    done = set()
    if os.path.exists(out_path):
        with open(out_path, newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                done.add((r["organism"], r["protein"], r["checkpoint"]))
        print(f"resuming: {len(done)} rows already done", flush=True)

    fields = ["organism", "protein", "checkpoint", "organism_token", "n_aa",
              "dna", "authors_dna", "same_as_authors", "seconds"]
    new_file = not os.path.exists(out_path)
    fh = open(out_path, "a", newline="", encoding="utf-8")
    writer = csv.DictWriter(fh, fieldnames=fields)
    if new_file:
        writer.writeheader()

    tokenizer = AutoTokenizer.from_pretrained(CHECKPOINTS["fine"])
    t_start = time.time()
    for name, path in CHECKPOINTS.items():
        if all((r["organism"], r["protein"], name) in done for r in rows):
            print(f"checkpoint {name}: already complete", flush=True)
            continue
        model = BigBirdForMaskedLM.from_pretrained(path).to(DEVICE).eval()
        for i, r in enumerate(rows):
            key = (r["organism"], r["protein"], name)
            if key in done:
                continue
            org = ecoli_token if r["organism"] == "Escherichia coli" else r["organism"]
            t0 = time.time()
            try:
                with torch.no_grad():
                    pred = predict_dna_sequence(
                        protein=r["protein_seq"],
                        organism=org,
                        device=DEVICE,
                        tokenizer=tokenizer,
                        model=model,
                        attention_type="original_full",
                        deterministic=True,
                    )
                dna = pred.predicted_dna
            except Exception as exc:  # one long protein must not kill the run
                print(f"  FAILED {name} {r['organism']} / {r['protein']} "
                      f"({len(r['protein_seq'])} aa): {type(exc).__name__}: {exc}", flush=True)
                dna = ""
            dt = time.time() - t0
            authors = str(r["authors_fine"] if name == "fine" else r["authors_base"]).upper()
            writer.writerow({
                "organism": r["organism"], "protein": r["protein"], "checkpoint": name,
                "organism_token": org, "n_aa": len(r["protein_seq"]),
                "dna": dna, "authors_dna": authors,
                "same_as_authors": int(dna.upper() == authors),
                "seconds": round(dt, 3),
            })
            fh.flush()
            if i % 20 == 0:
                print(f"  {name} {i + 1}/{len(rows)} {r['organism']} / {r['protein']} "
                      f"{dt:.1f}s elapsed={time.time() - t_start:.0f}s", flush=True)
            if time.time() - t_start > 3 * 3600:
                print("STOP: 3 h budget reached, see the fallback in claims.json", flush=True)
                fh.close()
                return 2
        del model
    fh.close()
    print(f"done in {time.time() - t_start:.0f}s", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
