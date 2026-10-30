"""Builds the data behind the public scoreboard from this repository.

Reads the results table and the Open Tables list in README.md, the status tables in FOLLOWUP.md,
the date of each report, and the package checks of drift_watch.py, and writes one JSON file per
table to scoreboard/. Re-run it after each new report, each answer from authors, or each week.

Usage: python -I scoreboard.py
No dependencies. The package checks need access to pypi.org.
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

TOOLS = Path(__file__).parent
ROOT = TOOLS.parent
OUT = ROOT / "scoreboard"
sys.path.insert(0, str(TOOLS))
import drift_watch  # noqa: E402

# Broad area of each field as the README names it
AREAS = {
	"protein structure": "Biology", "cell biology": "Biology", "genomics": "Biology",
	"protein fitness": "Biology", "protein design": "Biology", "cell imaging": "Biology",
	"plant genomics": "Biology", "cosmology": "Physics", "particle physics": "Physics",
	"materials / chemistry": "Materials and chemistry", "materials": "Materials and chemistry",
}

# The main thing each rerun found, in one category, read from the report
MAIN_ISSUE = {
	"2026-gilchrist-foldmason": "Reference data offline or deleted",
	"2024-dimitrov-liana-slidetags": "Code differs from the Methods",
	"2022-brout-pantheonplus": "Settings behind one result not published",
	"2022-qu-particle-transformer": "New dependency release breaks results",
	"2023-li-miniprot": "Test lists or evaluation commands not published",
	"2025-ko-matgl": "Numbers differ, cause unknown",
	"2023-notin-proteingym": "Code differs from the Methods",
	"2025-dauparas-ligandmpnn": "Code differs from the Methods",
	"2024-madhavacheril-act-dr6": "New dependency release breaks the code",
	"2023-deng-chgnet": "Test split not published",
	"2025-stringer-cellpose3": "Test data not released",
	"2025-zhai-plantcad": "More compute than one home GPU",
}


def table_rows(text, header_start):
	"""Rows of the markdown table whose header line starts with header_start."""
	lines = text.splitlines()
	start = next(i for i, line in enumerate(lines) if line.startswith(header_start))
	rows = []
	for line in lines[start + 2:]:
		if not line.startswith("|"):
			break
		rows.append([cell.strip() for cell in line.strip().strip("|").split("|")])
	return rows


def plain(markdown):
	"""Markdown cell -> plain text."""
	return re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", markdown).replace("**", "").replace("`", "")


def papers(readme):
	out = []
	for paper, field, verdict, found in table_rows(readme, "| Paper | Field |"):
		match = re.match(r"\[([^\]]+)\]\(reports/([^/]+)/REPORT\.md\),\s*(.+?)\s+(\d{4})(?:\s|$)", paper)
		name, folder, venue, year = match.groups()
		report = (ROOT / "reports" / folder / "REPORT.md").read_text(encoding="utf-8")
		date = re.search(r"^- Date:\s*(\d{4}-\d{2}-\d{2})", report, re.M)
		out.append({
			"paper": name,
			"report": folder,
			"report_url": f"https://github.com/paper-rerun/paper-rerun/blob/main/reports/{folder}/REPORT.md",
			"venue": venue,
			"year": int(year),
			"field": field,
			"area": AREAS.get(field, "Other"),
			"verdict": verdict,
			"main_issue": MAIN_ISSUE.get(folder, ""),
			"finding": plain(found),
			"rerun_date": date.group(1) if date else "",
		})
	return out


def datasets(readme):
	out = []
	section = readme.split("## Open Tables datasets", 1)[1].split("\n## ", 1)[0]
	group = ""
	for line in section.splitlines():
		if line.endswith(":") and not line.startswith("-"):
			group = "Crop trials" if line.startswith("Crop") else "Other fields"
		match = re.match(r"- \[([^\]]+)\]\((https://github\.com/paper-rerun/[^)]+)\): ([\d,]+) ", line)
		if match:
			out.append({"dataset": match.group(1), "url": match.group(2), "group": group,
				"records": int(match.group(3).replace(",", ""))})
	return out


def followup(text):
	out = []
	for kind, header in (("Pull request", "| Paper | Repository | Change |"), ("Issue", "| Paper | Repository | What we ask |")):
		for paper, repo, ask, status in table_rows(text, header):
			out.append({"kind": kind, "paper": plain(paper), "repository": plain(repo), "ask": plain(ask),
				"status": "ready" if status == "ready" else ("posted" if status.startswith("[") or "github.com" in status else status)})
	return out


def drift():
	config = json.loads(drift_watch.CONFIG_FILE.read_text(encoding="utf-8"))
	out = []
	for entry in config["packages"]:
		try:
			status, today = drift_watch.check_package(entry)
		except Exception as error:
			status, today = "error", f"check failed: {error}"
		out.append({"report": entry["report"], "package": entry["package"], "finding": entry["finding"],
			"today": today, "status": status})
	return out


def main():
	OUT.mkdir(exist_ok=True)
	readme = (ROOT / "README.md").read_text(encoding="utf-8")
	tables = {
		"papers": papers(readme),
		"datasets": datasets(readme),
		"followup": followup((ROOT / "FOLLOWUP.md").read_text(encoding="utf-8")),
		"drift": drift(),
	}
	for name, rows in tables.items():
		(OUT / f"{name}.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
		print(f"{name}: {len(rows)} rows")
	stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
	(OUT / "built.json").write_text(json.dumps([{"built_at": stamp}]) + "\n", encoding="utf-8")


if __name__ == "__main__":
	main()
