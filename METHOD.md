# How we work

## Choosing papers

We start from code, because without public code there is nothing to re-run. A script searches GitHub for science repositories created since 2022, finds the paper behind each one, and ranks them by three things:

- **Impact (40%)**: citations in the last year and the current one, so it reflects who is using the work now.
- **Use (30%)**: stars, forks, and whether the repository is still maintained.
- **Doubt (30%)**: issues where people ask about reproducing the paper's results, with extra weight on those nobody answered.

A wrong result costs most where papers feed decisions, so papers on health, food, water, energy and climate get a bonus of up to 20%. Its size comes from how strongly OpenAlex links the paper to the matching UN Sustainable Development Goals (hunger, health, water, energy, climate); a repository tagged with one of those topics gets at least 10%. The top of the list then goes through triage before anything runs.

The same search can be limited to one country: `--country BR` keeps only papers with at least one author at a Brazilian institution. Groups outside the largest labs have fewer stars, so this goes with a lower cutoff, for example `--country BR --min-stars 10`.

## Standard mode

Most papers go through a lighter version of the full pipeline below:

1. **Triage**, as in step 1 below.
2. **Pre-registration.** One agent writes the claims, every definition (with quotes from the paper) and the tolerances to `claims.json`, then records its SHA-256 hash. Nothing has been computed on our side at that point. Where the paper is ambiguous, the authors' own per-item results decide, never ours.
3. **Reproduction.** A single agent builds the environment from the versions the authors used and runs the full test set. It cannot edit `claims.json`; alternatives it thinks matter go in a separate section and never change the verdict.
4. **Adversarial review.** Another agent checks that the hash still matches and attacks the report.
5. **Revision** and **human approval**, as in steps 8 and 9 below.

We picked this after running ProteinGym both ways. Both runs reached the same numbers and the same findings. The full pipeline cost about twice as much and added a blind second computation. The lighter mode without a separate pre-registration step had written its definitions after computing three models. That is the gap step 2 closes. The full pipeline is kept for very widely used papers, and for any paper the standard mode finds does not reproduce.

## The full pipeline

A paper is split by **claim**: a number the paper reports, with its conditions and tolerance. Each claim is computed and checked on its own.

1. **Triage.** We check that the code and license are usable, that the test set was published (ids or seed), that every dataset actually downloads, that no independent reproduction exists yet, and how long the full computation would take. Papers that fail are dropped, with the reason recorded.
2. **Claims map.** One agent lists the claims and fixes every definition the computation needs (cutoffs, test sets, how results are averaged), quoting the paper. This happens before anything runs, so no definition can be picked after seeing a result. A second agent checks the list against the paper.
3. **Environment.** One agent builds the software environment once and freezes it, starting from the versions the authors used. In our pilot, the latest version of some package broke the code in 3 of 5 papers.
4. **Execution.** Separate agents compute each group of claims with the authors' code and released weights or data.
5. **Blind recomputation.** A different agent rebuilds the environment from the frozen lockfile and recomputes every claim without seeing the first results, using scoring code it writes itself. A claim is confirmed only when both agree.
6. **Report.** One agent writes the report. Alternatives we tried after the fact go in a separate section and never change the verdict.
7. **Adversarial review.** Another agent's only job is to find errors in the report: misquoted paper numbers, misapplied tolerances, a verdict stronger than the evidence, method changes passed off as environment fixes.
8. **Revision.** A further agent fixes every point the reviewer raised, checking each one against the files, and the coordinator confirms the serious ones are gone. We added this step after our first pipeline run, whose draft report had three serious errors that the reviewer caught.
9. **Human approval.** A person reads the report and any issue we plan to open before anything is published.

## Rules

- We change only the environment, dependencies, file paths and obvious crashes. Never the method or hyperparameters. Any change to the authors' code is listed as a diff.
- There is no time limit on computation; we run to the criterion the paper used. If the same failure survives three different fixes, we stop and report it.
- Issues to authors are questions backed by something they can re-run, not verdicts.

## Code

`tools/garimpo.py` builds the ranked list of candidate papers. `tools/reproduce-standard.js` (standard mode) and `tools/reproduce-paper-pipeline-v2.js` (full pipeline) are the orchestration scripts with every agent prompt, run with Claude Code's workflow tool. `tools/reproduce-paper-pipeline.js` is the first version of the pipeline, used for LigandMPNN.

## Hardware

One home computer: AMD Ryzen 9 3900X (12 cores), 64 GB RAM, NVIDIA RTX 2070 SUPER (8 GB), Windows 11 with WSL2 Ubuntu 24.04.

## Cost

In the pilot, one paper took 4 to 24 hours of wall-clock time and about 280k tokens of agent work, roughly a quarter to half of it waiting for the single GPU. On ProteinGym, the standard mode used about 670k tokens and 10 hours (9 of them GPU); the full pipeline used about twice the tokens.
