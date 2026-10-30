# Follow-up with authors

Every report ends with a note for the authors. This page tracks where each note goes and what happened after. A rerun only changes something once the authors hear about it, so this is the part of the work that counts.

How to post: open an issue (or, where the fix is one line in an environment file, a pull request) on the authors' repository, using the note under "Notes for the authors" in the report, with a link to the report. Then replace the status below with the link, and update it when the authors answer.

Status values: **ready** (note written, not posted), **posted** (issue or PR open, link given), **answered**, **fixed** (the authors changed code, data or text), **closed without change**.

## Pull requests worth opening first

These change one line in an environment file or a script, so they are easy for authors to accept and they protect every new user.

| Paper | Repository | Change | Status |
|---|---|---|---|
| [Particle Transformer](reports/2022-qu-particle-transformer/REPORT.md#notes-for-the-authors) | [jet-universe/particle_transformer](https://github.com/jet-universe/particle_transformer) | README: `pip install 'weaver-core>=0.4,<0.5'`. With 0.5.x the released checkpoint gives near-random scores without any error. | ready |
| [ACT DR6 lensing](reports/2024-madhavacheril-act-dr6/REPORT.md#notes-for-the-authors) | [ACTCollaboration/act_dr6_lenslike](https://github.com/ACTCollaboration/act_dr6_lenslike) | README: say that the recommended settings need `camb<2` (`lens_margin` was removed in CAMB 2). | ready |
| [LigandMPNN](reports/2025-dauparas-ligandmpnn/REPORT.md#notes-for-the-authors) | [dauparas/LigandMPNN](https://github.com/dauparas/LigandMPNN) | `requirements.txt`: add `setuptools<81`, because ProDy 2.4.1 imports `pkg_resources`. | ready |
| [FoldMason](reports/2026-gilchrist-foldmason/REPORT.md#notes-for-the-authors) | [steineggerlab/foldmason-analysis](https://github.com/steineggerlab/foldmason-analysis) | `compute_scores.sh` calls an undefined `compute_nirmsd`; `FoldMason_benchmarks.R` filters `"Homstrad"` while `name_map` produces `"HOMSTRAD"`. | ready |

## Issues

| Paper | Repository | What we ask | Status |
|---|---|---|---|
| [Pantheon+](reports/2022-brout-pantheonplus/REPORT.md#notes-for-the-authors) | [PantheonPlusSH0ES/DataRelease](https://github.com/PantheonPlusSH0ES/DataRelease) | Which prior and settings gave the w0waCDM row; whether the PolyChord chains behind Table 3 can be released. | ready |
| [Particle Transformer](reports/2022-qu-particle-transformer/REPORT.md#notes-for-the-authors) | [jet-universe/particle_transformer](https://github.com/jet-universe/particle_transformer) | Confirm that the released `*_full.pt` files are the Table 1 models (can go in the PR above). | ready |
| [CHGNet](reports/2023-deng-chgnet/REPORT.md#notes-for-the-authors) | [CederGroupHub/chgnet](https://github.com/CederGroupHub/chgnet) | Publish the MPtrj train/val/test mp-ids used for model 0.2.0. | ready |
| [miniprot](reports/2023-li-miniprot/REPORT.md#notes-for-the-authors) | [lh3/miniprot](https://github.com/lh3/miniprot) | The test protein lists and the evaluation command lines behind Table 1. | ready |
| [ProteinGym](reports/2023-notin-proteingym/REPORT.md#notes-for-the-authors) | [OATML-Markslab/ProteinGym](https://github.com/OATML-Markslab/ProteinGym) | ESM2 scores on 5 long-protein assays; the ESM-1b scoring rule (same point as their issue #99); the averaging used for the headline numbers. | ready |
| [LIANA+](reports/2024-dimitrov-liana-slidetags/REPORT.md#notes-for-the-authors) | [saezlab/lianaplus_manuscript](https://github.com/saezlab/lianaplus_manuscript) | The FDR correction in `utils.join_pred_truth` has no effect as written; which was intended. Plus the scSeqComm cutoff and the Spearman value in Supplementary Note 5. | ready |
| [ACT DR6 lensing](reports/2024-madhavacheril-act-dr6/REPORT.md#notes-for-the-authors) | [ACTCollaboration/act_dr6_lenslike](https://github.com/ACTCollaboration/act_dr6_lenslike) | Cobaya 3.6 data path error (may be their #19/#27); pandas 3 breaks the BAO likelihoods. | ready |
| [LigandMPNN](reports/2025-dauparas-ligandmpnn/REPORT.md#notes-for-the-authors) | [dauparas/LigandMPNN](https://github.com/dauparas/LigandMPNN) | Six questions on the neighbourhood definition, metal context and checkpoint behind Fig. 2a. | ready |
| [MatGL](reports/2025-ko-matgl/REPORT.md#notes-for-the-authors) | [materialyzeai/matgl](https://github.com/materialyzeai/matgl) | How Fig. 4 was computed; the COMP6 force sign; the ANI-MD description. | ready |
| [Cellpose3](reports/2025-stringer-cellpose3/REPORT.md#notes-for-the-authors) | [MouseLand/cellpose](https://github.com/MouseLand/cellpose) | Release the noisy test sets behind Fig. 1, 3 and 4. | ready |
| [PlantCAD](reports/2025-zhai-plantcad/REPORT.md#notes-for-the-authors) | [plantcad/plantcad](https://github.com/plantcad/plantcad) | float16 loading returns a float32 model with the pinned transformers. | ready |
| [FoldMason](reports/2026-gilchrist-foldmason/REPORT.md#notes-for-the-authors) | [steineggerlab/foldmason](https://github.com/steineggerlab/foldmason) | Deposit the HOMSTRAD release used for Fig. 2A (server offline, see their #38); 285 AFDB members deleted. | ready |

## Still true today?

[tools/drift_watch.py](tools/drift_watch.py) re-checks every Monday whether the dependency and data problems above are still live, and the [Drift watch](https://github.com/paper-rerun/paper-rerun/actions/workflows/drift-watch.yml) workflow shows the result. When a problem goes away, update the report and this page.
