# How to help

Paper Rerun is run by one person with AI agents on one home computer. More hands mean more papers checked, more authors told, and more datasets opened. Here is what helps, from least to most effort.

## Point us to a paper

Open an issue titled `Paper: <short title>` with the DOI, the code repository, and why it matters (who builds on it, or an unanswered issue asking how to reproduce it). Papers with public code and data, many users, and a result that other work depends on come first. Health, food, energy and climate get priority, as in [METHOD.md](METHOD.md#choosing-papers).

## Tell an author

Each report has a note for the authors. If you know the authors, or you use their code, the note carries more weight coming from a user. [FOLLOWUP.md](FOLLOWUP.md) lists which notes still need to be posted.

## Use and cite the datasets

The [Open Tables](README.md#open-tables-datasets) datasets turn trial results that only existed in Portuguese PDFs into checked tables. If you work in agronomy, ecology or public health, use them, tell us what is wrong or missing, and cite them. Suggestions for the next publication series are welcome as issues titled `Table: <series>`.

## Run a rerun yourself

You need a computer that can run the paper's code, and Claude Code with its workflow tool. The orchestration scripts are in [tools/](tools/):

- `reproduce-standard.js`: the standard mode in [METHOD.md](METHOD.md#standard-mode), for most papers.
- `reproduce-paper-pipeline-v2.js`: the full pipeline, for widely used papers or a result that does not reproduce.

The scripts were written for our machine. Before running them, change the working paths (`root`, `wroot`), the hardware lines and the GPU lock in the shared prompt at the top of each script, and point the rules line at your copy of [templates/REPORT.md](templates/REPORT.md). The arguments are the paper, the code repository, the target (which table or figure), the working folder and the triage notes.

A contributed report is a pull request that adds one folder, `reports/<year>-<first author>-<short name>/`, with:

- `REPORT.md`, following [templates/REPORT.md](templates/REPORT.md);
- `claims.json` and `claims.sha256`, written before anything ran;
- `env/` with the lockfile and the setup script;
- `runs/` with the scripts, logs and outputs behind every number;
- `review.json`, the adversarial review, and how each point was handled.

The rules are the ones in [METHOD.md](METHOD.md#rules): change only the environment, dependencies, paths and obvious crashes; run to the paper's own criterion; write to authors as questions they can re-run. A human reviews every report before it is merged, and nothing is posted to the authors before that.

## Keep the checks current

[tools/drift_watch.json](tools/drift_watch.json) lists the dependency releases and data files that broke a rerun. When a new report finds one, add an entry, so the weekly check keeps watching it.

## If you are an author

If a report gets something wrong, open an issue. We will re-check, and correct or withdraw the report publicly.
