"""Builds the queue of papers worth reproducing.

Starts from science repos on GitHub, finds the paper DOI in the README or CITATION.cff,
pulls citations from OpenAlex and counts reproduction issues. Writes ranking.csv and TOP.md.

Usage: python -I garimpo.py [max_repos_for_issue_check] [max_topics] [--country BR] [--min-stars 80]
  --country    keep only papers with at least one author at an institution in that country
               (ISO code, as OpenAlex gives it). Repos from smaller groups have fewer stars,
               so pair it with a lower --min-stars, e.g. --country BR --min-stars 10.
  --min-stars  GitHub stars a repo needs to enter the candidate list (default 80).
Needs: gh logged in. No other dependencies.
"""

import argparse
import csv
import json
import math
import re
import subprocess
import time
import urllib.parse
import urllib.request
from pathlib import Path

OUTPUT_FOLDER = Path(__file__).parent
CACHE_FILE = OUTPUT_FOLDER / "cache.json"

SCIENCE_TOPICS = [
	"bioinformatics", "computational-biology", "genomics", "single-cell", "protein-design",
	"protein-structure", "drug-discovery", "cheminformatics", "medical-imaging", "neuroscience",
	"microscopy", "plant-science", "agriculture", "ecology", "materials-science",
	"interatomic-potentials", "molecular-dynamics", "quantum-chemistry", "computational-physics",
	"astrophysics", "cosmology", "climate", "weather-forecasting", "epidemiology",
]

# Areas closest to health, food, energy and climate get a small bonus
WELFARE_TOPICS = {
	"drug-discovery", "medical-imaging", "epidemiology", "genomics", "plant-science",
	"agriculture", "materials-science", "interatomic-potentials", "climate", "weather-forecasting",
}

# Repos we already reproduced in the pilot
ALREADY_DONE = {
	"dauparas/ligandmpnn", "cedergrouphub/chgnet", "mouseland/cellpose",
	"actcollaboration/act_dr6_lenslike", "plantcad/plantcad", "kuleshov-group/plantcaduceus",
}

DOI_PATTERN = re.compile(r"10\.\d{4,9}/[^\s\"'<>()\[\]{},;]+", re.IGNORECASE)
SKIP_DOI_PREFIXES = ("10.5281/zenodo", "10.5281/", "10.6084/m9.figshare")
# Both words required: plain "reproduce" hits every "steps to reproduce" bug report.
# GitHub stems the words, so this also catches "reproduction" and "reproducing".
# Quoted phrases joined with OR returned 0 even for LigandMPNN #71, so they're out
REPRODUCTION_QUERY = "reproduce paper"
CITATION_HEADING_PATTERN = re.compile(r"(^#+\s*cit|^\s*@(article|inproceedings|misc)|please cite|if you use)", re.IGNORECASE | re.MULTILINE)
CURRENT_YEAR = 2026
PAPER_FIELDS = "id,doi,title,cited_by_count,publication_year,counts_by_year,type,primary_location,sustainable_development_goals,authorships"

# A wrong result costs most where papers feed decisions about health, food, water, energy and
# climate. OpenAlex tags each paper with UN Sustainable Development Goals and a score from 0 to 1
STAKES_GOALS = {2: "Zero hunger", 3: "Good health", 6: "Clean water", 7: "Clean energy", 13: "Climate action"}
# The bonus goes up to 20% for a paper OpenAlex links strongly to those goals; a repo topic in
# WELFARE_TOPICS alone still counts as a score of 0.5, which is the old flat 10%
MAX_STAKES_BONUS = 0.2
WELFARE_TOPIC_STAKES = 0.5


def run_gh(arguments):
	result = subprocess.run(["gh", "api", *arguments], capture_output=True, text=True, encoding="utf-8")
	if result.returncode != 0:
		return None
	return result.stdout


def gh_search(endpoint, query, per_page):
	output = run_gh(["-X", "GET", f"search/{endpoint}", "-f", f"q={query}", "-f", f"per_page={per_page}"])
	# Search API allows 30 calls per minute
	time.sleep(2.1)
	if output is None:
		return None
	return json.loads(output)


def fetch_openalex_work(doi):
	url = "https://api.openalex.org/works/doi:" + urllib.parse.quote(doi) + "?select=" + PAPER_FIELDS
	try:
		with urllib.request.urlopen(url, timeout=30) as response:
			return json.loads(response.read().decode("utf-8"))
	except Exception:
		return None


def find_candidate_repos(topics, min_stars):
	repos_by_name = {}
	for topic in topics:
		query = f"topic:{topic} created:>2022-01-01 stars:>{min_stars}"
		search_result = gh_search("repositories", query, 50)
		if not search_result:
			continue
		for repo in search_result.get("items", []):
			full_name = repo["full_name"]
			if full_name.lower() in ALREADY_DONE:
				continue
			# Curated link lists cite dozens of papers that are not theirs
			description = (repo.get("description") or "").lower()
			if "awesome" in full_name.lower() or "curated list" in description or "list of papers" in description:
				continue
			entry = repos_by_name.setdefault(full_name, {
				"repo": full_name,
				"stars": repo["stargazers_count"],
				"forks": repo["forks_count"],
				"pushed_at": repo["pushed_at"][:10],
				"topics": set(),
			})
			entry["topics"].add(topic)
	return list(repos_by_name.values())


def find_paper_doi(full_name):
	# The repo's own paper is in CITATION.cff or in the README citation section.
	# DOIs elsewhere in the README are usually other people's work (datasets, baselines)
	citation_file = run_gh([f"repos/{full_name}/contents/CITATION.cff", "-H", "Accept: application/vnd.github.raw"]) or ""
	readme = run_gh([f"repos/{full_name}/readme", "-H", "Accept: application/vnd.github.raw"]) or ""
	citation_heading = CITATION_HEADING_PATTERN.search(readme)
	readme_citation_section = readme[citation_heading.start():] if citation_heading else ""
	texts = [citation_file, readme_citation_section, readme]
	found_dois = []
	for text in texts:
		for match in DOI_PATTERN.findall(text):
			doi = match.rstrip(".").lower()
			if doi.startswith(SKIP_DOI_PREFIXES) or doi in found_dois:
				continue
			found_dois.append(doi)
	return found_dois


def normalize(text):
	return re.sub(r"[^a-z0-9]", "", text.lower())


def search_openalex_by_title(name):
	url = "https://api.openalex.org/works?filter=title.search:" + urllib.parse.quote(name) + ",from_publication_date:2021-01-01&sort=cited_by_count:desc&per_page=5&select=" + PAPER_FIELDS
	try:
		with urllib.request.urlopen(url, timeout=30) as response:
			return json.loads(response.read().decode("utf-8")).get("results", [])
	except Exception:
		return []


def pick_paper(full_name, dois):
	# The repo's paper has the tool name in its title. Without that check, a README citing
	# AutoDock Vina or ESM gets credited with their citations
	repo_short_name = normalize(full_name.split("/")[1])
	if len(repo_short_name) < 4:
		return None
	for doi in dois[:8]:
		work = fetch_openalex_work(doi)
		if not work or work.get("publication_year", 0) < 2021:
			continue
		if repo_short_name in normalize(work.get("title") or ""):
			work["doi"] = doi
			return work
	# Fallback: look the name up in OpenAlex titles. Only titles that start with the name
	# ("DiffDock: ..."), since short names like "mint" match unrelated papers anywhere else
	for work in search_openalex_by_title(full_name.split("/")[1]):
		if normalize(work.get("title") or "").startswith(repo_short_name) and work.get("doi"):
			work["doi"] = work["doi"].replace("https://doi.org/", "")
			return work
	return None


def recent_citations(work):
	counts = {item["year"]: item["cited_by_count"] for item in work.get("counts_by_year", [])}
	return counts.get(CURRENT_YEAR - 1, 0) + counts.get(CURRENT_YEAR, 0)


def count_reproduction_issues(full_name):
	all_issues = gh_search("issues", f"repo:{full_name} is:issue {REPRODUCTION_QUERY}", 1)
	unanswered = gh_search("issues", f"repo:{full_name} is:issue comments:0 {REPRODUCTION_QUERY}", 1)
	total_count = all_issues["total_count"] if all_issues else 0
	unanswered_count = unanswered["total_count"] if unanswered else 0
	return total_count, unanswered_count


def scale_log(value, max_value):
	if max_value <= 0:
		return 0.0
	return math.log1p(value) / math.log1p(max_value)


def stakes(paper):
	"""Strongest link (0 to 1) to the goals in STAKES_GOALS, and their names."""
	best, names = 0.0, []
	for goal in paper.get("sustainable_development_goals") or []:
		number = int(str(goal.get("id", "")).rstrip("/").rsplit("/", 1)[-1] or 0)
		if number in STAKES_GOALS:
			best = max(best, float(goal.get("score") or 0))
			names.append(STAKES_GOALS[number])
	return best, names


def author_countries(paper):
	countries = set()
	for authorship in paper.get("authorships") or []:
		countries.update(authorship.get("countries") or [])
		countries.update(i["country_code"] for i in authorship.get("institutions") or [] if i.get("country_code"))
	return countries


def parse_arguments():
	parser = argparse.ArgumentParser(description="Build the ranked queue of papers worth reproducing.")
	parser.add_argument("max_repos_for_issue_check", nargs="?", type=int, default=80)
	# Limits topics, for a quick test run
	parser.add_argument("max_topics", nargs="?", type=int, default=len(SCIENCE_TOPICS))
	parser.add_argument("--country", help="keep only papers with an author at an institution in this country (ISO code)")
	parser.add_argument("--min-stars", type=int, default=80)
	return parser.parse_args()


def main():
	arguments = parse_arguments()
	max_repos_for_issue_check = arguments.max_repos_for_issue_check
	country = arguments.country.upper() if arguments.country else None
	cache = json.loads(CACHE_FILE.read_text(encoding="utf-8")) if CACHE_FILE.exists() else {}

	repos = find_candidate_repos(SCIENCE_TOPICS[:arguments.max_topics], arguments.min_stars)
	print(f"{len(repos)} candidate repos")

	# Attach the paper behind each repo, skipping repos with no peer-reviewed-looking paper
	candidates = []
	for repo in repos:
		full_name = repo["repo"]
		if full_name not in cache:
			paper = pick_paper(full_name, find_paper_doi(full_name))
			cache[full_name] = {"paper": paper}
			CACHE_FILE.write_text(json.dumps(cache), encoding="utf-8")
		paper = cache[full_name]["paper"]
		if not paper:
			continue
		# Papers cached before goals and authorships were requested get them now
		if "authorships" not in paper:
			refreshed = fetch_openalex_work(paper["doi"])
			if refreshed:
				paper.update({"sustainable_development_goals": refreshed.get("sustainable_development_goals"), "authorships": refreshed.get("authorships")})
				CACHE_FILE.write_text(json.dumps(cache), encoding="utf-8")
		if country and country not in author_countries(paper):
			continue
		# Under 20 recent citations nobody is building on it yet (and it was letting library papers in)
		if recent_citations(paper) < 20:
			continue
		repo["paper"] = paper
		candidates.append(repo)
	print(f"{len(candidates)} with a paper found" + (f" and an author in {country}" if country else ""))

	# Preliminary score without issues, to spend the slow issue search on the best ones
	max_recent_citations = max((recent_citations(c["paper"]) for c in candidates), default=1)
	max_stars = max((c["stars"] for c in candidates), default=1)
	for candidate in candidates:
		candidate["impact"] = scale_log(recent_citations(candidate["paper"]), max_recent_citations)
		is_alive = candidate["pushed_at"] >= f"{CURRENT_YEAR - 1}-10-01"
		candidate["usage"] = scale_log(candidate["stars"] + 2 * candidate["forks"], max_stars * 3) * (1.0 if is_alive else 0.5)
	candidates.sort(key=lambda c: 0.4 * c["impact"] + 0.3 * c["usage"], reverse=True)

	for candidate in candidates[:max_repos_for_issue_check]:
		full_name = candidate["repo"]
		if "issues" not in cache[full_name]:
			cache[full_name]["issues"] = count_reproduction_issues(full_name)
			CACHE_FILE.write_text(json.dumps(cache), encoding="utf-8")
		candidate["repro_issues"], candidate["repro_unanswered"] = cache[full_name]["issues"]

	# Final score: impact 40%, usage 30%, doubt 30%, then a stakes bonus of up to 20%
	checked = candidates[:max_repos_for_issue_check]
	max_doubt = max((c["repro_issues"] + 2 * c["repro_unanswered"] for c in checked), default=1)
	for candidate in checked:
		doubt = scale_log(candidate["repro_issues"] + 2 * candidate["repro_unanswered"], max_doubt)
		goal_score, candidate["stakes_goals"] = stakes(candidate["paper"])
		topic_score = WELFARE_TOPIC_STAKES if candidate["topics"] & WELFARE_TOPICS else 0.0
		candidate["stakes"] = round(max(goal_score, topic_score), 3)
		bonus = 1 + MAX_STAKES_BONUS * candidate["stakes"]
		candidate["score"] = round((0.4 * candidate["impact"] + 0.3 * candidate["usage"] + 0.3 * doubt) * bonus, 3)
	checked.sort(key=lambda c: c["score"], reverse=True)

	with open(OUTPUT_FOLDER / "ranking.csv", "w", newline="", encoding="utf-8") as csv_file:
		writer = csv.writer(csv_file)
		writer.writerow(["score", "repo", "stars", "pushed_at", "recent_citations", "total_citations", "repro_issues", "repro_unanswered", "stakes", "stakes_goals", "author_countries", "year", "venue", "doi", "title", "topics"])
		for c in checked:
			paper = c["paper"]
			venue = ((paper.get("primary_location") or {}).get("source") or {}).get("display_name", "")
			writer.writerow([c["score"], c["repo"], c["stars"], c["pushed_at"], recent_citations(paper), paper["cited_by_count"],
				c["repro_issues"], c["repro_unanswered"], c["stakes"], "; ".join(c["stakes_goals"]), " ".join(sorted(author_countries(paper))),
				paper["publication_year"], venue, paper["doi"], paper["title"], " ".join(sorted(c["topics"]))])

	title = "# Fila de candidatos" + (f" com autores em {country}" if country else "")
	lines = [title, "", "| # | Nota | Repo | Citações (ano+atual) | Issues de reprodução (sem resposta) | Metas da ONU | Artigo |", "|---|---|---|---|---|---|---|"]
	for position, c in enumerate(checked[:30], start=1):
		paper = c["paper"]
		goals = ", ".join(c["stakes_goals"]) or "-"
		lines.append(f"| {position} | {c['score']} | {c['repo']} | {recent_citations(paper)} | {c['repro_issues']} ({c['repro_unanswered']}) | {goals} | {paper['title'][:80]} ({paper['publication_year']}) |")
	(OUTPUT_FOLDER / "TOP.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
	print("wrote ranking.csv and TOP.md")


if __name__ == "__main__":
	main()
