"""L3: Fig. 4a and 4b from the sequences we generated with the two released checkpoints.

Also reports how often our generated sequence is identical to the one the authors
deposited, per checkpoint and per organism, which is the sharper check of the release.

Usage: compare_l3.py runs/out/generated_primary.csv [more.csv ...]
"""
import csv
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze_sourcedata import codons, jaccard, seq_similarity  # noqa: E402

PUBLISHED = {"C1": 0.74, "C2": 69.26}
BAND = {"C1": 0.03, "C2": 2.0}


def report(path):
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    by = {}
    for r in rows:
        by.setdefault((r["organism"], r["protein"]), {})[r["checkpoint"]] = r
    print(f"\n==== {os.path.basename(path)} ====")
    print(f"rows={len(rows)} pairs={len(by)}")

    tok = sorted({r["organism_token"] for r in rows if r["organism"] == "Escherichia coli"})
    print(f"E. coli organism token(s): {tok}")

    ident = {}
    for r in rows:
        k = (r["checkpoint"], r["organism"])
        ident.setdefault(k, []).append(int(r["same_as_authors"]))
    print("sequences identical to the authors' deposited ones:")
    for k in sorted(ident):
        v = ident[k]
        print(f"   {k[0]:5s} {k[1]:26s} {sum(v):3d}/{len(v):3d}")

    out = []
    for (org, prot), d in sorted(by.items()):
        if "base" not in d or "fine" not in d or not d["base"]["dna"] or not d["fine"]["dna"]:
            continue
        cb, cf = codons(d["base"]["dna"]), codons(d["fine"]["dna"])
        ab, af = codons(d["base"]["authors_dna"]), codons(d["fine"]["authors_dna"])
        out.append({
            "organism": org, "protein": prot,
            "jaccard_ours": jaccard(cb, cf), "similarity_ours": seq_similarity(cb, cf),
            "jaccard_authors_seqs": jaccard(ab, af), "similarity_authors_seqs": seq_similarity(ab, af),
            "base_identical": d["base"]["same_as_authors"], "fine_identical": d["fine"]["same_as_authors"],
            "seconds_base": d["base"]["seconds"], "seconds_fine": d["fine"]["seconds"],
        })
    csv_out = path.replace(".csv", "_metrics.csv")
    with open(csv_out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)

    for cid, col in (("C1", "jaccard_ours"), ("C2", "similarity_ours")):
        v = np.array([r[col] for r in out if r[col] is not None])
        delta = v.mean() - PUBLISHED[cid]
        verdict = "INSIDE" if abs(delta) <= BAND[cid] else "OUTSIDE"
        print(f"{cid} n={len(v)} ours mean={v.mean():.4f} sd={v.std(ddof=1):.4f} "
              f"published={PUBLISHED[cid]} delta={delta:+.4f} band=+/-{BAND[cid]} -> {verdict}")
        per_org = {}
        for r in out:
            if r[col] is not None:
                per_org.setdefault(r["organism"], []).append(r[col])
        for org in sorted(per_org):
            a = np.array(per_org[org])
            print(f"     {org:26s} n={len(a):3d} mean={a.mean():.4f}")

    t = np.array([float(r["seconds_base"]) + float(r["seconds_fine"]) for r in out])
    print(f"inference time: {t.sum() / 60:.1f} min over {len(t)} pairs, "
          f"mean {t.mean():.1f} s per pair, max {t.max():.1f} s")
    print(f"wrote {csv_out}")


if __name__ == "__main__":
    for p in sys.argv[1:]:
        report(p)
