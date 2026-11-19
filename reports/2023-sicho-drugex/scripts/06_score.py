"""Scores our two runs against the frozen claims and prints the verdict table.

Reads claims.json, checks its hash against claims.sha256 first, and refuses to score if the
file moved after it was frozen.

Usage: 06_score.py <claims.json> <claims.sha256> <full_c27.json> <full_c31.json> <out.json>
"""
import hashlib
import json
import sys

CLAIMS, SHA, C27, C31, OUT = sys.argv[1:6]

digest = hashlib.sha256(open(CLAIMS, "rb").read()).hexdigest()
frozen = open(SHA, encoding="utf-8").read().split()[0]
if digest != frozen:
	sys.exit("claims.json changed after freezing: %s now, %s frozen" % (digest, frozen))

claims = json.load(open(CLAIMS, encoding="utf-8"))
runs = {
	"ChEMBL 27 LSTM RNN": json.load(open(C27, encoding="utf-8")),
	"ChEMBL 31 GRU RNN": json.load(open(C31, encoding="utf-8")),
}
KEY = {"validity": "frozen_validity", "uniqueness": "frozen_uniqueness"}

lines = ["| claim | model | metric | ours | published | band | |",
	"|---|---|---|---|---|---|---|"]
results = []
for claim in claims["claims"]:
	got = runs[claim["model"]][KEY[claim["metric"]]]
	delta = got - claim["published"]
	inside = abs(delta) <= claim["band"]
	results.append({"id": claim["id"], "model": claim["model"], "metric": claim["metric"],
		"ours": got, "published": claim["published"], "delta": delta,
		"band": claim["band"], "inside": inside})
	lines.append("| %s | %s | %s | %.4f | %.4f | %+.4f | %.5f | %s |" % (
		claim["id"], claim["model"], claim["metric"], got, claim["published"], delta,
		claim["band"], "ok" if inside else "**fails**"))

passed = sum(r["inside"] for r in results)
verdict = ("Reproduced" if passed == len(results)
	else "Not reproduced" if passed == 0 else "Partially reproduced")
summary = {"claims_inside_band": passed, "claims_total": len(results),
	"verdict": verdict, "claims_hash_checked": digest, "results": results,
	"secondary": {name: {k: v for k, v in run.items() if k.startswith("secondary")}
		for name, run in runs.items()}}
open(OUT, "w", encoding="utf-8", newline="\n").write(json.dumps(summary, indent=1))
print("\n".join(lines))
print("\n%s: %d of %d inside the frozen band" % (verdict, passed, len(results)))
print(json.dumps(summary["secondary"], indent=1))
