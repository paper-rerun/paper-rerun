"""Checks whether problems found in our reruns are still live today.

A rerun records what broke: a dependency whose new release changes results or stops the code,
or a data file that moved or went offline. This script re-checks each of those against PyPI and
the data servers, so a report can say "still true on <date>" instead of only "true when we ran it".

For each package it asks PyPI which release a new user gets from the authors' own install
instruction, and whether that release falls in the range we found broken. For each URL it checks
whether the server still answers the way the report says.

Usage: python -I drift_watch.py [--out DRIFT.md]
Reads drift_watch.json next to this file. No dependencies.
"""

import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

CONFIG_FILE = Path(__file__).parent / "drift_watch.json"
REPORTS_URL = "https://github.com/paper-rerun/paper-rerun/blob/main/reports"
USER_AGENT = "paper-rerun-drift-watch/1.0 (+https://github.com/paper-rerun/paper-rerun)"
TIMEOUT_SECONDS = 30


def parse_version(text):
	"""Release numbers only (1.3.6 -> (1, 3, 6)); None for pre-releases and dev builds."""
	match = re.fullmatch(r"v?(\d+(?:\.\d+)*)(?:\.post\d+)?", text.strip())
	if not match:
		return None
	numbers = [int(n) for n in match.group(1).split(".")]
	while len(numbers) > 1 and numbers[-1] == 0:
		numbers.pop()
	return tuple(numbers)


def satisfies(version, spec):
	"""spec is a comma-separated list like '>=0.4,<0.5'. An empty spec accepts everything."""
	for clause in filter(None, (c.strip() for c in spec.split(","))):
		match = re.fullmatch(r"(>=|<=|==|!=|>|<)\s*(\S+)", clause)
		if not match:
			raise ValueError(f"cannot read version clause: {clause!r}")
		operator, bound = match.group(1), parse_version(match.group(2))
		checks = {
			">=": version >= bound, "<=": version <= bound, ">": version > bound,
			"<": version < bound, "==": version == bound, "!=": version != bound,
		}
		if not checks[operator]:
			return False
	return True


def fetch_json(url):
	request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
	with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
		return json.load(response)


def check_package(entry):
	data = fetch_json(f"https://pypi.org/pypi/{entry['package']}/json")
	released = []
	for text, files in data["releases"].items():
		version = parse_version(text)
		if version is not None and files and not all(f.get("yanked") for f in files):
			released.append((version, text))
	candidates = [r for r in released if satisfies(r[0], entry.get("install_spec", ""))]
	if not candidates:
		return "error", "no release matches the install instruction"
	version, text = max(candidates)
	newest_tested = max(parse_version(v) for v in entry["tested"].values())
	if satisfies(version, entry["bad_range"]):
		status = "still broken" if version <= newest_tested else "still in broken range, untested"
	else:
		status = "fixed or avoided"
	return status, f"installs {entry['package']} {text}"


def check_url(entry):
	request = urllib.request.Request(entry["url"], method="HEAD", headers={"User-Agent": USER_AGENT})
	try:
		with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
			answer = str(response.status)
	except urllib.error.HTTPError as error:
		answer = str(error.code)
	except (urllib.error.URLError, TimeoutError, OSError) as error:
		answer = "no answer"
		if getattr(error, "reason", None):
			answer += f" ({error.reason})"
	status = "still broken" if answer.split()[0] in entry["broken_if"] else "changed, re-check"
	return status, f"server answers {answer}"


def main():
	out_path = None
	if "--out" in sys.argv:
		out_path = Path(sys.argv[sys.argv.index("--out") + 1])
	config = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
	today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

	lines = [
		f"# Drift watch, {today}",
		"",
		"Problems found in our reruns, checked again today against PyPI and the data servers.",
		"",
		"| Report | What we found | Today | Status |",
		"|---|---|---|---|",
	]
	for entry in config["packages"] + config["urls"]:
		try:
			status, today_text = check_package(entry) if "package" in entry else check_url(entry)
		except Exception as error:  # one bad entry should not hide the others
			status, today_text = "error", f"check failed: {error}"
		report = f"[{entry['report']}]({REPORTS_URL}/{entry['report']}/REPORT.md)"
		lines.append(f"| {report} | {entry['finding']} | {today_text} | {status} |")
		print(f"{status:32} {entry['report']}: {today_text}")

	if out_path:
		out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
	main()
