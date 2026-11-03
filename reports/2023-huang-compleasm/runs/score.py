"""Grades the compleasm Table 1 claims from runs/<tag>/summary.txt with the pre-registered definitions."""
import json
import re
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TAGS = {"scer": "scer", "cele": "cele", "atha": "atha", "dmel": "dmel", "mmus": "mmus", "hsap": "hsap", "zmay": "zmay"}


def read_summary(path):
	counts = {}
	for line in path.read_text().splitlines():
		match = re.match(r"^([SDFIMN]):(?:[\d.]+%, )?(\d+)$", line.strip())
		if match:
			counts[match.group(1)] = int(match.group(2))
	return counts


def round1(value):
	return float(Decimal(repr(value)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))


def main(run_root):
	claims = json.loads((ROOT / "claims.json").read_text(encoding="utf-8"))["claims"]
	rows = []
	for claim in claims:
		claim_id = claim["id"]
		_, genome, tool, quantity = claim_id.split(".")
		if tool != "compleasm":
			continue
		summary = run_root / TAGS[genome] / "summary.txt"
		if not summary.exists():
			rows.append({"id": claim_id, "paper": claim["paper_value"], "ours": None, "status": "not run"})
			continue
		counts = read_summary(summary)
		total = counts["N"]
		# Pre-registered metrics: C = S + D, F = Fragmented + Interspaced, M as printed
		numerators = {"S": counts["S"], "D": counts["D"], "C": counts["S"] + counts["D"],
			"F": counts["F"] + counts["I"], "M": counts["M"]}
		if quantity == "N":
			ours = total
			status = "exact" if ours == claim["paper_value"] else "MISMATCH"
			rows.append({"id": claim_id, "paper": claim["paper_value"], "ours": ours, "count": ours, "diff": ours - claim["paper_value"], "status": status})
			continue
		ours = 100.0 * numerators[quantity] / total
		diff = ours - claim["paper_value"]
		if round1(ours) == claim["paper_value"]:
			status = "exact"
		elif abs(diff) <= 0.3 + 1e-9:
			status = "within 0.3"
		elif abs(diff) <= 1.0 + 1e-9:
			status = "close, outside tolerance"
		else:
			status = "OUTSIDE"
		rows.append({"id": claim_id, "paper": claim["paper_value"], "ours": round(ours, 4), "ours_1dp": round1(ours),
			"count": numerators[quantity], "N": total, "diff": round(diff, 4), "status": status,
			"F_only": counts["F"], "I_only": counts["I"]})
	for row in rows:
		print("\t".join(str(row.get(key, "")) for key in ["id", "paper", "ours", "ours_1dp", "count", "N", "diff", "status"]))
	return rows


if __name__ == "__main__":
	run_root = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "runs"
	out_rows = main(run_root)
	out_name = sys.argv[2] if len(sys.argv) > 2 else "scores.json"
	(run_root / out_name).write_text(json.dumps(out_rows, indent=1))
