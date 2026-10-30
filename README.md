# Paper Rerun

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23585151.svg)](https://doi.org/10.5281/zenodo.23585151)

We re-run published research code and report what holds. Project page: https://paper-rerun.github.io

Most papers that ship code are never re-run by anyone outside the lab that wrote them. Reviewers read the paper; they rarely run it. Paper Rerun picks papers that many people build on, runs the authors' code on the authors' data again, and publishes what came out: the numbers, every command, and everything we had to fix to get there.

The work is done by AI agents (Claude, by Anthropic) on one home computer, and a human reviews every report before it goes out. See [how we work](METHOD.md).

## What we do

- **Rerun**: we re-run published research code on the authors' data and report what holds.
- **Fix Back**: when a rerun finds something broken or missing, we send the authors a small fix as a pull request, not only a report.
- **Open Tables**: we turn trial results buried in Portuguese-language technical literature into open, checked datasets.
- **Upkeep**: we fix small, testable problems in widely used scientific software.

## Results so far

| Paper | Field | Verdict | What we found |
|---|---|---|---|
| [FoldMason](reports/2026-gilchrist-foldmason/REPORT.md), Science 2026 | protein structure | Partially reproduced | Fig. 2B (AFDB clusters): on the 32 clusters whose inputs are still complete, 31 give the authors' LDDT to 6 decimals and the same alignment. 285 of the 3,200 benchmark structures have since been deleted from AlphaFold DB, so the 160-cluster means run on reduced inputs only. Fig. 2A could not run: the HOMSTRAD reference is offline and not archived anywhere we could find. |
| [LIANA+](reports/2024-dimitrov-liana-slidetags/REPORT.md), Nature Cell Biology 2024 | cell biology | Reproduced | Fig. 4 (ligand-receptor methods scored against spatial co-localisation on 5 Slide-tags datasets) re-runs from the released files and matches the Source Data to about 1e-16. In the evaluation code, the FDR correction the Methods describe is applied to a 0/1 vector and has no effect; done as described, it reorders the methods. We asked which was intended. |
| [Pantheon+](reports/2022-brout-pantheonplus/REPORT.md), ApJ 2022 | cosmology | Reproduced | Table 3 with the released distances and covariance: Omega_m = 0.3327 ± 0.018 against 0.334 ± 0.018 in flat ΛCDM; the ΛCDM and wCDM rows and the SH0ES H0 (73.54 against 73.6) also hold. The w0waCDM row does not (Omega_m 0.32 against 0.403); it depends on the prior range, and the authors' released chains do not reach 0.403 either. We asked which prior and settings produced it. |
| [Particle Transformer](reports/2022-qu-particle-transformer/REPORT.md), ICML 2022 | particle physics | Reproduced | Table 1 with the released checkpoints on all 20 M JetClass test jets: ParT accuracy 0.86051 and AUC 0.98772 match the printed 0.861 and 0.9877, and all nine background rejections fall inside the pre-registered statistical band; all 11 ParticleNet numbers match. The README installs weaver-core>=0.4, which now gives 0.5.3; with it the same checkpoint runs without error but scores 0.123 accuracy. |
| [miniprot](reports/2023-li-miniprot/REPORT.md), Bioinformatics 2023 | genomics | Partially reproduced | Table 1 (protein-to-genome alignment accuracy of miniprot-0.7): % confirmed splice junctions matches in all four columns, but base-level sensitivity on the human genome comes out 0.95 to 1.2 points lower and 6 of 12 percentages miss the 0.5-point tolerance. The paper does not publish the test protein lists or the evaluation command lines; we asked the author for both. |
| [MatGL](reports/2025-ko-matgl/REPORT.md), npj Computational Materials 2025 | materials / chemistry | Not reproduced | Fig. 4 (COMP6 energy and force errors of three released ML potentials) does not reproduce: 3 of 36 values match, the rest differ in both directions. Two independent runs of ours agree with each other within 0.03 meV/atom. The model ranking holds. We asked the authors how the figure was computed. |
| [ProteinGym](reports/2023-notin-proteingym/REPORT.md), NeurIPS 2023 D&B | protein fitness | Reproduced | All five headline numbers (ESM-1b and four ESM2 sizes) match within 0.003 over all 217 assays, confirmed by a second, independent run. The paper's averages come from the script's protein-first grouping, not the text's definition; ESM-1b was scored with wt-marginals, not the masked-marginals the appendix states; and five long-protein ESM2 scores were computed on the MSA region only, unlike the released code. |
| [LigandMPNN](reports/2025-dauparas-ligandmpnn/REPORT.md), Nature Methods 2025 | protein design | Partially reproduced | The main claim holds: atomic context raises recovery near ligands, most near metals. Three of six headline numbers match. The authors' own per-protein data show that the figure used a different neighbourhood definition than the Results text, and metal-only context on the metal split; that choice moves the metal number by about 15 points. |
| [ACT DR6 lensing](reports/2024-madhavacheril-act-dr6/REPORT.md), ApJ 2024 | cosmology | Reproduced | All targets within 0.1σ, chains run to the paper's convergence criterion. The released setup no longer runs on CAMB 2.x; CAMB 1.3.6 works. |
| [CHGNet](reports/2023-deng-chgnet/REPORT.md), Nature Machine Intelligence 2023 | materials | Partially reproduced | The released model behaves as described, but the test split was drawn without a fixed seed and never published, so the headline test error can't be re-checked. |
| [Cellpose3](reports/2025-stringer-cellpose3/REPORT.md), Nature Methods 2025 | cell imaging | Partially reproduced | All 46 values on real microscopy data match within 0.01. The noisy test images behind the main benchmark were never released. |
| [PlantCAD](reports/2025-zhai-plantcad/REPORT.md), PNAS 2025 | plant genomics | Partially reproduced | All four values fall inside our 95% interval on a weighted 300k-window sample. The full test set would take about 115 days on our GPU. |

The five papers below ProteinGym were a pilot, each run by a single agent. LigandMPNN was then run again through the full pipeline, with a second agent recomputing every number blind; that is the report linked above, and the pilot version sits in its `pilot/` folder. ProteinGym was run twice, once in our standard mode and once through the full pipeline, to compare the two; the second run is in its `pipeline/` folder. Reports from now on use the standard mode described in [METHOD.md](METHOD.md).

Files too large for this repository (the ACT DR6 MCMC chains, about 24 MB, and a few full error tables) are available on request.

## Open Tables datasets

Results that exist only in Portuguese-language PDFs, turned into open tables. Every entry was transcribed twice independently and checked against the PDF.

Crop trials, each from 20 Embrapa publications:

- [Asian soybean rust control trials](https://github.com/paper-rerun/soybean-rust-trials-br): 5,836 results, including five national summaries of the cooperative fungicide trials.
- [Cassava management trials](https://github.com/paper-rerun/cassava-trials-br): 3,311 results from 77 trials.
- [Rice blast management trials](https://github.com/paper-rerun/rice-blast-trials-br): 2,990 results.
- [Wheat management trials](https://github.com/paper-rerun/wheat-trials-br): 2,851 results.
- [Cowpea (feijão-caupi) trials](https://github.com/paper-rerun/cowpea-trials-br): 2,541 results.
- [Fall armyworm control trials in maize](https://github.com/paper-rerun/fall-armyworm-maize-trials-br): 2,075 results.
- [Tomato management trials](https://github.com/paper-rerun/tomato-trials-br): 2,068 results.
- [Potato management trials](https://github.com/paper-rerun/potato-trials-br): 1,874 results.
- [Common bean disease management trials](https://github.com/paper-rerun/bean-disease-trials-br): 1,562 results from 52 trials.

Other fields:

- [Historical public health results, 1960 to 1985](https://github.com/paper-rerun/public-health-historical-br): 2,619 aggregated results from 8 Brazilian studies.
- [Fish landings and aquaculture trials](https://github.com/paper-rerun/fisheries-aquaculture-br): 1,672 results from 8 publications that exist only as PDF.
- [Fauna and flora inventories](https://github.com/paper-rerun/biodiversity-inventories-br): 1,152 species occurrences from 8 Embrapa inventories not yet in GBIF.

## After the report

A rerun changes something only once the authors hear about it. [FOLLOWUP.md](FOLLOWUP.md) tracks the note each report sends to the authors, where it goes and what happened after. Some problems we find also keep changing: a new release of a dependency breaks the code, or a data server goes offline. [tools/drift_watch.py](tools/drift_watch.py) re-checks those every week, so a report can say whether its finding is still true today.

## How to help

Point us to a paper, pass a note to authors you know, use the datasets, or run a rerun in your own field. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Verdicts

- **Reproduced**: every target number matches within the tolerance the paper itself allows.
- **Partially reproduced**: some targets match, or we could only run a documented subset.
- **Not reproduced**: we ran it and the numbers don't match.
- **Could not run**: data missing, code broken beyond a reasonable fix, or more hardware than we have.

A "partially" is not an accusation. So far, every partial verdict came from something missing (a test split, a dataset, compute), not from a wrong result. "Not reproduced" is also not an accusation: it means our careful rerun of the released code and data gives different numbers, and we ask the authors why.

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
