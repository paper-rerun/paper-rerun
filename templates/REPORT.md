# Reproduction report: <paper title>

- Paper: <authors>, <journal or venue> <volume>, <pages> (<year>). DOI: <doi> (<preprint, and which version we compared against>)
- Code: <repository URL> @ <commit hash> (<tag or release, if any>)
- Data: <where each input came from, with DOI, file names, sizes and checksums>
- Target: <which table, figure or numbers in the paper, and how many claims>
- Verdict: **Reproduced** | **Partially reproduced** | **Not reproduced** | **Could not run** (see the verdicts in the [README](https://github.com/paper-rerun/paper-rerun#verdicts))
- Date: <YYYY-MM-DD>
- Hardware: <CPU, RAM, GPU, operating system>

## Results

All claims, definitions and tolerances were fixed in `claims.json` before anything ran. Its sha256 is <hash> and it still matches `claims.sha256`.

| Claim | Paper | Ours | Difference | Tolerance | Verdict |
|---|---|---|---|---|---|
| <id and short name> | <value, with location> | <value> | <difference> | <tolerance and its basis> | <match / miss> |

<One paragraph on what holds and what does not. Every number here comes from a file in `runs/`.>

## What it took

1. Environment (`env/`): <Python and package versions, where the pins came from, the lockfile, and any environment-only fix>.
2. Data: <downloads and how each was checked>.
3. Runs: <commands, run time, anything unusual>.
4. Scoring: <the script that compares against claims.json, and where the outputs are>.

Changes to the authors' code, if any, are in `patches/` as diffs. We change only the environment, dependencies, file paths and obvious crashes, never the method or hyperparameters.

## Alternative readings

<Other definitions or settings we tried after the fact, and what they give. These never change the verdict.>

## Notes for the authors

<Thanks first. Then each point as a question the authors can re-run from their own files, with the numbers. Questions, not verdicts.>

## How this report was made

This reproduction was run by AI agents (Claude, by Anthropic) and reviewed by a human before publication. No number in this report was estimated or typed by hand: each one comes from code that ran, and the commands, logs and outputs are in this folder.

<Which agent did which stage: triage, pre-registration, run, review, revision.>

The method, prompts and scripts are public at https://github.com/paper-rerun/paper-rerun/blob/main/METHOD.md.

Contact: <name>, https://github.com/paper-rerun/paper-rerun/issues
