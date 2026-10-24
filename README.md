# Paper Rerun

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23585151.svg)](https://doi.org/10.5281/zenodo.23585151)

We re-run published research code and report what holds. Project page: https://paper-rerun.github.io

Most papers that ship code are never re-run by anyone outside the lab that wrote them. Reviewers read the paper; they rarely run it. Paper Rerun picks papers that many people build on, runs the authors' code on the authors' data again, and publishes what came out: the numbers, every command, and everything we had to fix to get there.

The work is done by AI agents (Claude, by Anthropic) on one home computer, and a human reviews every report before it goes out. See [how we work](METHOD.md).

## Results so far

| Paper | Field | Verdict | What we found |
|---|---|---|---|
| [ProteinGym](reports/2023-notin-proteingym/REPORT.md), NeurIPS 2023 D&B | protein fitness | Reproduced | All five headline numbers (ESM-1b and four ESM2 sizes) match within 0.003 over all 217 assays, confirmed by a second, independent run. The paper's averages come from the script's protein-first grouping, not the text's definition; ESM-1b was scored with wt-marginals, not the masked-marginals the appendix states; and five long-protein ESM2 scores were computed on the MSA region only, unlike the released code. |
| [LigandMPNN](reports/2025-dauparas-ligandmpnn/REPORT.md), Nature Methods 2025 | protein design | Partially reproduced | The main claim holds: atomic context raises recovery near ligands, most near metals. Three of six headline numbers match. The authors' own per-protein data show that the figure used a different neighbourhood definition than the Results text, and metal-only context on the metal split; that choice moves the metal number by about 15 points. |
| [ACT DR6 lensing](reports/2024-madhavacheril-act-dr6/REPORT.md), ApJ 2024 | cosmology | Reproduced | All targets within 0.1σ, chains run to the paper's convergence criterion. The released setup no longer runs on CAMB 2.x; CAMB 1.3.6 works. |
| [CHGNet](reports/2023-deng-chgnet/REPORT.md), Nature Machine Intelligence 2023 | materials | Partially reproduced | The released model behaves as described, but the test split was drawn without a fixed seed and never published, so the headline test error can't be re-checked. |
| [Cellpose3](reports/2025-stringer-cellpose3/REPORT.md), Nature Methods 2025 | cell imaging | Partially reproduced | All 46 values on real microscopy data match within 0.01. The noisy test images behind the main benchmark were never released. |
| [PlantCAD](reports/2025-zhai-plantcad/REPORT.md), PNAS 2025 | plant genomics | Partially reproduced | All four values fall inside our 95% interval on a weighted 300k-window sample. The full test set would take about 115 days on our GPU. |

The five papers below ProteinGym were a pilot, each run by a single agent. LigandMPNN was then run again through the full pipeline, with a second agent recomputing every number blind; that is the report linked above, and the pilot version sits in its `pilot/` folder. ProteinGym was run twice, once in our standard mode and once through the full pipeline, to compare the two; the second run is in its `pipeline/` folder. Reports from now on use the standard mode described in [METHOD.md](METHOD.md).

Files too large for this repository (the ACT DR6 MCMC chains, about 24 MB, and a few full error tables) are available on request.

## Verdicts

- **Reproduced**: every target number matches within the tolerance the paper itself allows.
- **Partially reproduced**: some targets match, or we could only run a documented subset.
- **Not reproduced**: we ran it and the numbers don't match.
- **Could not run**: data missing, code broken beyond a reasonable fix, or more hardware than we have.

A "partially" is not an accusation. So far, every partial verdict came from something missing (a test split, a dataset, compute), not from a wrong result.

## What a report contains

The exact paper numbers we compared against and where they are in the paper, our numbers, the tolerance, every command and log, the environment that worked, any change we had to make (as a diff), and a note to the authors. When we find something the authors should know, we open a polite issue on their repository with a link to the report.

## Why AI

Checking a paper takes days of setup that nobody gets credit for, which is why it rarely happens. AI agents make that work cheap, so it can be done for many papers instead of a few. We publish the method, the prompts and the scripts so anyone can do the same for papers in their own field.

## If you are an author

If a report gets something wrong, open an issue here. We will re-check, and we will correct or withdraw the report and say so publicly.

## License

Reports: CC BY 4.0. Code: MIT. See [LICENSE.md](LICENSE.md).

## Contact

Filipe Tessaro, https://github.com/paper-rerun/paper-rerun/issues
