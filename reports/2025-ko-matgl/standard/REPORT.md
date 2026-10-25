# Reproduction report: Materials Graph Library (MatGL), an open-source graph deep learning library for materials science and chemistry

- Paper: Ko, Deng, Nassar et al., npj Computational Materials 11, 253 (2025). DOI: 10.1038/s41524-025-01742-y (preprint arXiv 2503.03837)
- Code: https://github.com/materialyzeai/matgl @ v1.3.0 (a6ebaebd6a0021e14d49d001103508c4980d94da)
- Data: COMP6 v1, https://github.com/isayev/COMP6 @ 79f41c156f8e19506fe951b5513b98e7c534a503 (11 HDF5 files, 101,352 conformations)
- Target: Fig. 4a (energy MAE, meV/atom) and Fig. 4b (force MAE, eV/Å) on COMP6 for the three released ANI-1x-Subset potentials (M3GNet, TensorNet, SO3Net) across the 6 plotted groups. That makes 36 numbers. Secondary: the ANI-MD values quoted in the text on p. 5.
- Verdict: **Not reproduced** (4 of 36 match, 8 close, 24 mismatch)
- Date: 2026-10-24
- Hardware: Ryzen 9 3900X, 31 GB RAM available to WSL2, RTX 2070 SUPER 8 GB, WSL2 Ubuntu 24.04. The primary run used the CPU only (see "What it took").

## Results

The paper values are the Fig. 4 bar heights, read from the vector drawing in the journal PDF. Each bar is known to within ±0.0002 meV/atom and ±0.000002 eV/Å. All claims, definitions and tolerances were fixed in `claims.json` before any model ran (sha256 `80c8c13e2010436c052516ba3a5ab73a867a46ba3c5d4cca31d10eb2bc9d2990`, checked again before scoring).

Definitions used for the verdict:
- **Energy:** mean over conformations of |E_pred − E_ref| / N_atoms, using absolute total energies.
- **Force:** MAE pooled over every Cartesian component.
- **Groups:** "GDB 9-11" = the three GDB07to09 files and "GDB 12-13" = the four GDB10to13 files.
- **Tolerance:** max(5% of the paper value, 0.05 meV/atom or 0.001 eV/Å).
- **Grades:** "close" means within 3× the tolerance. Diff = ours − paper.

| Quantity | Paper | Ours | Diff | Grade |
|---|---|---|---|---|
| M3GNet energy, ANI-MD (meV/atom) | 19.159 | 7.672 | −11.487 (−60.0%) | mismatch |
| M3GNet force, ANI-MD (eV/Å) | 0.142 | 0.1136 | −0.0284 (−20.0%) | mismatch |
| M3GNet energy, GDB 9-11 | 8.925 | 3.522 | −5.403 (−60.5%) | mismatch |
| M3GNet force, GDB 9-11 | 0.074 | 0.0644 | −0.0096 (−13.0%) | close |
| M3GNet energy, GDB 12-13 | 3.655 | 5.902 | +2.247 (+61.5%) | mismatch |
| M3GNet force, GDB 12-13 | 0.118 | 0.1199 | +0.0019 (+1.6%) | match |
| M3GNet energy, Drugbank | 12.010 | 8.933 | −3.077 (−25.6%) | mismatch |
| M3GNet force, Drugbank | 0.126 | 0.1065 | −0.0195 (−15.4%) | mismatch |
| M3GNet energy, S66x8 | 9.835 | 7.507 | −2.328 (−23.7%) | mismatch |
| M3GNet force, S66x8 | 0.029 | 0.0449 | +0.0159 (+54.8%) | mismatch |
| M3GNet energy, Tripeptides | 2.662 | 5.708 | +3.046 (+114.4%) | mismatch |
| M3GNet force, Tripeptides | 0.067 | 0.0767 | +0.0097 (+14.5%) | close |
| TensorNet energy, ANI-MD | 11.099 | 2.800 | −8.299 (−74.8%) | mismatch |
| TensorNet force, ANI-MD | 0.099 | 0.0789 | −0.0201 (−20.3%) | mismatch |
| TensorNet energy, GDB 9-11 | 1.705 | 3.377 | +1.672 (+98.1%) | mismatch |
| TensorNet force, GDB 9-11 | 0.056 | 0.0604 | +0.0044 (+7.8%) | close |
| TensorNet energy, GDB 12-13 | 3.252 | 4.694 | +1.442 (+44.4%) | mismatch |
| TensorNet force, GDB 12-13 | 0.090 | 0.0989 | +0.0089 (+9.9%) | close |
| TensorNet energy, Drugbank | 1.123 | 2.797 | +1.674 (+149.1%) | mismatch |
| TensorNet force, Drugbank | 0.086 | 0.0764 | −0.0096 (−11.2%) | close |
| TensorNet energy, S66x8 | 6.031 | 5.673 | −0.358 (−5.9%) | close |
| TensorNet force, S66x8 | 0.045 | 0.0382 | −0.0068 (−15.1%) | mismatch |
| TensorNet energy, Tripeptides | 2.248 | 3.098 | +0.850 (+37.8%) | mismatch |
| TensorNet force, Tripeptides | 0.067 | 0.0667 | −0.0003 (−0.5%) | match |
| SO3Net energy, ANI-MD | 2.283 | 1.011 | −1.272 (−55.7%) | mismatch |
| SO3Net force, ANI-MD | 0.044 | 0.0352 | −0.0088 (−20.0%) | mismatch |
| SO3Net energy, GDB 9-11 | 3.889 | 1.680 | −2.209 (−56.8%) | mismatch |
| SO3Net force, GDB 9-11 | 0.032 | 0.0293 | −0.0027 (−8.4%) | close |
| SO3Net energy, GDB 12-13 | 1.271 | 2.197 | +0.926 (+72.9%) | mismatch |
| SO3Net force, GDB 12-13 | 0.044 | 0.0492 | +0.0052 (+11.8%) | close |
| SO3Net energy, Drugbank | 0.969 | 1.456 | +0.487 (+50.2%) | mismatch |
| SO3Net force, Drugbank | 0.044 | 0.0338 | −0.0102 (−23.1%) | mismatch |
| SO3Net energy, S66x8 | 2.558 | 1.664 | −0.894 (−34.9%) | mismatch |
| SO3Net force, S66x8 | 0.011 | 0.0154 | +0.0044 (+40.2%) | mismatch |
| SO3Net energy, Tripeptides | 1.245 | 1.243 | −0.002 (−0.1%) | match |
| SO3Net force, Tripeptides | 0.029 | 0.0291 | +0.0001 (+0.3%) | match |

**Verdict rule** (pre-registered): Reproduced needs all 36 to match. Partially reproduced needs at least 18 matches, or all 36 at match or close. We have 4 matches, 8 close and 24 mismatches, so the result is Not reproduced.

**Which checkpoints the figure used.** The v1.3.0 model cards of M3GNet and SO3Net repeat the Table 5 numbers. Nothing in the paper ties Fig. 4 to these checkpoints, and TensorNet has no model card at the tag (`claims.json`, D-CHECKPOINT). Our comparison assumes the released weights are the ones behind Fig. 4.

**The differences go both ways.** We are lower than the figure on ANI-MD for all three models: 2.3 to 4 times lower in energy (paper/ours 2.50, 3.96 and 2.26). On GDB 12-13 and Drugbank we are mostly higher. On ANI-MD the force bars are 1.25× ours for all three models (1.250, 1.255, 1.249). A common factor across three architectures points to a difference in normalisation or in the ANI-MD set (the text says 16 systems; `ani_md_bench.h5` has 14), not to the models. Swapping MAE for RMSE does not explain it: RMSE/MAE is 1.64 to 1.71 on these files. Elsewhere the force ratio ranges from 0.65 to 1.30, so there is no global scale factor.

**The three equal SO3Net force bars.** The pre-registration flagged that the figure gives SO3Net force 0.044 for ANI-MD, GDB 12-13 and Drugbank. We get 0.035, 0.049 and 0.034, which does not support three equal values. It may be a data-entry error in the figure.

**The ranking does hold** (exploratory, not pre-registered: the trend sentence is out of scope in `claims.json`). The paper says SO3Net beats TensorNet, which beats M3GNet, and that "this trend can be also found in other benchmark datasets". In our numbers that order holds in all 12 group × quantity cases. It does not hold in every single file: on gdb11_07 energy, M3GNet (2.954) is below TensorNet (3.085). The authors' own figure breaks the order twice (GDB 9-11 energy, S66x8 force) and has a tie in Tripeptides force (M3GNet = TensorNet = 0.067).

**Text checks on p. 5** (secondary, ANI-MD):

| Text says | Ours | Pass |
|---|---|---|
| M3GNet energy above 14 meV/atom | 7.672 | no |
| M3GNet force above 0.14 eV/Å | 0.1136 | no |
| TensorNet energy "11 meV/atom" | 2.800 | no |
| TensorNet force "0.1 eV/Å" | 0.0789 | yes (one significant figure) |
| SO3Net energy "2.3 meV/atom" | 1.011 | no |
| SO3Net force "0.044 eV/Å" | 0.0352 | no |

**Sanity check against the training distribution.** The v1.3.0 model cards of M3GNet and SO3Net repeat the Table 5 ANI-1x test MAEs: M3GNet 3.746 meV/atom and 0.085 eV/Å, SO3Net 1.596 meV/atom and 0.035 eV/Å. Nothing in the paper ties Fig. 4 to these checkpoints. On our smallest COMP6 file (gdb11_07, 15.3 atoms on average), M3GNet gives 2.954 meV/atom and 0.0546 eV/Å, and SO3Net gives 1.587 meV/atom and 0.0259 eV/Å. Errors grow steadily with molecule size across the seven GDB files for every model (per-file table below). This is what you would expect from correctly loaded models.

Exploratory: Table 5 gives TensorNet a test energy MAE of 3.015 meV/atom on ANI-1x, inside its training distribution. The figure's TensorNet energy bars for Drugbank (1.123) and GDB 9-11 (1.705) sit below that number, even though both sets have larger molecules outside the distribution and use absolute per-atom energies. That is unlikely, and it suggests the figure used a different metric or different data.

**Per-file values** (secondary, primary metric definitions). Each cell is energy (meV/atom) / force (eV/Å):

| File (conformations, mean atoms) | M3GNet | TensorNet | SO3Net |
|---|---|---|---|
| ani_md_bench (1791, 75.2) | 7.672 / 0.1136 | 2.800 / 0.0789 | 1.011 / 0.0352 |
| gdb11_07 (12000, 15.3) | 2.954 / 0.0546 | 3.085 / 0.0534 | 1.587 / 0.0259 |
| gdb11_08 (12000, 17.0) | 3.434 / 0.0639 | 3.364 / 0.0602 | 1.629 / 0.0291 |
| gdb11_09 (12000, 18.8) | 4.177 / 0.0728 | 3.682 / 0.0662 | 1.824 / 0.0322 |
| gdb11_10 (12000, 20.6) | 5.124 / 0.0823 | 3.953 / 0.0730 | 1.968 / 0.0347 |
| gdb11_11 (11670, 23.4) | 5.441 / 0.1152 | 4.685 / 0.0996 | 2.122 / 0.0494 |
| gdb13_12 (12000, 25.3) | 6.227 / 0.1318 | 4.990 / 0.1058 | 2.260 / 0.0534 |
| gdb13_13 (12000, 27.3) | 6.801 / 0.1413 | 5.149 / 0.1114 | 2.437 / 0.0562 |
| drugbank_testset (13379, 44.4) | 8.933 / 0.1065 | 2.797 / 0.0764 | 1.456 / 0.0338 |
| s66x8 (528, 19.9) | 7.507 / 0.0449 | 5.673 / 0.0382 | 1.664 / 0.0154 |
| tripeptide_full (1984, 52.5) | 5.708 / 0.0767 | 3.098 / 0.0667 | 1.243 / 0.0291 |

No conformation was excluded: all are C/H/N/O with finite references.

## Alternative readings

None of these change the verdict. They were pre-registered as secondary, except the last row of the first table, which we added afterwards and label as exploratory.

**Other averaging definitions.** The count is the number of the 18 energy or 18 force claims within tolerance.

| Definition | Matches (primary grouping) | Matches (literal GDB grouping) |
|---|---|---|
| Energy, primary: mean of \|dE\|/N | 1/18 | 1/18 |
| Energy (b): total-energy MAE / mean N | 1/18 | 1/18 |
| Energy (c): sum \|dE\| / sum N | identical to (b) by definition | same |
| Energy (d): unweighted mean of per-file MAEs | 1/18 | 1/18 |
| Force, primary: pooled component MAE | 3/18 | 2/18 |
| Force (b): mean of per-conformation MAE | 3/18 | 2/18 |
| Force (c): per-atom force-vector error norm | 0/18 | 0/18 |
| Force (d): unweighted mean of per-file MAEs | 3/18 | 2/18 |
| Exploratory: energy with each molecule's mean error removed | 2/18 | 1/18 |

Full numbers for every group and definition are in `runs/results_main.json`.

**Literal reading of the GDB labels.** Here "GDB 9-11" = gdb11_09 + gdb11_10 + gdb11_11 and "GDB 12-13" = gdb13_12 + gdb13_13. Values are energy (meV/atom) / force (eV/Å):

| Group | M3GNet | TensorNet | SO3Net |
|---|---|---|---|
| GDB 9-11 | 4.909 / 0.0914 | 4.101 / 0.0807 | 1.970 / 0.0393 |
| GDB 12-13 | 6.514 / 0.1367 | 5.070 / 0.1087 | 2.349 / 0.0548 |

This reading moves us further from the figure for 4 of 6 energies (closer for M3GNet and SO3Net on GDB 9-11), and still gives 1/18 energy matches. In the figure, GDB 9-11 is higher than GDB 12-13 for M3GNet and SO3Net. In our data, every grouping has the larger GDB molecules with the larger errors.

**Where M3GNet's energy error comes from.** On ANI-MD and Drugbank most of M3GNet's energy error is a constant offset per molecule. The mean signed error is +7.15 of the 7.67 meV/atom MAE on ANI-MD and +8.16 of 8.93 on Drugbank. Removing each molecule's mean error drops these to 1.66 and 1.73 meV/atom. A relative-energy metric would therefore give much smaller numbers than the figure, not larger.

**Batched evaluation of M3GNet.** In matgl 1.3.0, `create_line_graph` builds the three-body line graph on the edges pruned to `threebody_cutoff` (4 Å). `ThreeBodyInteractions` then uses those indices as if they pointed into the unpruned 5 Å graph. This is the problem fixed later by PR #840. The output for a molecule therefore depends on which other molecules share its batch.

We ran M3GNet through batched `Potential` calls of up to 4,000 atoms each on three files:

| File | Energy, per-molecule | Energy, batched | Force, per-molecule | Force, batched | Max \|dE\|/atom (meV) | Max \|dF\| (eV/Å) |
|---|---|---|---|---|---|---|
| gdb11_07 | 2.954 | 2.958 | 0.0546 | 0.0546 | 0.621 | 0.047 |
| gdb11_08 | 3.434 | 3.440 | 0.0639 | 0.0639 | 0.684 | 0.025 |
| s66x8 | 7.507 | 7.536 | 0.0449 | 0.0449 | 0.907 | 0.016 |

Individual predictions change by up to 0.9 meV/atom and 0.047 eV/Å, but the MAEs move by at most 0.03 meV/atom. So batched evaluation does not explain the gap with the figure. TensorNet has no three-body step and gave identical batched and per-molecule results (50 ANI-MD conformations: max |dE| 0.0 eV, max |dF| 6.2e-6 eV/Å).

The batched run for the other 8 files was stopped. On CPU it needed about 8 GB of RAM per job and the jobs were OOM-killed. On the GPU, ANI-MD alone ran for more than 25 minutes without finishing.

**Not run.** The optional matgl 4.x M3GNet run (after PR #840) was not attempted. 4.x dropped DGL, and the 1.3.0 DGL checkpoints are not documented to load there.

## What it took

**Environment (`env/setup_env.sh`, `env/requirements.lock.txt`, 84 packages).**
- Python 3.11 via uv, torch 2.4.0+cu121, dgl 2.4.0+cu121 (data.dgl.ai torch-2.4/cu121 wheels), torchdata 0.8.0 and matgl 1.3.0. These are the upper bounds in the v1.3.0 `pyproject.toml`.
- Also numpy 1.26.4, lightning 2.5.6 and torch-geometric 2.8.1.
- Change 1: with ase 3.29 (the latest), `import matgl.ext.ase` fails because ase removed `ase.constraints.ExpCellFilter`. We pinned **ase 3.25.0**.
- Change 2: we pinned **pymatgen 2025.6.14** as a precaution (a release before the tag date); no failure was observed with a newer pymatgen. Both pins are releases from before the v1.3.0 tag date (2025-08-12).
- `REBUILD_FROM_LOCK=1 bash env/setup_env.sh` reinstalls the exact lockfile.

**Weights.**
- Taken from `pretrained_models/{M3GNet,SO3Net,TensorNet}-ANI-1x-Subset-PES/` in a clone of tag v1.3.0 (`data/matgl`, HEAD verified as a6ebaebd).
- Loaded by local path with `matgl.load_model`, because loading by name downloads from a URL that now returns 404 (issue #680).
- model.pt is 3,969,478 B for all three. The state.pt sizes and sha256 are M3GNet 1,164,446 B `4efa3b11…`, SO3Net 429,416 B `947361c5…` and TensorNet 856,757 B `02fdfcd1…`.
- Each state.pt is byte-identical to its Hugging Face copy (materialyze/*-PES-ANI-1x-Subset, downloaded without login).
- The model.json files match the hashes recorded at pre-registration. The TensorNet json from the tag was used, not the one on Hugging Face.

**Data.**
- 11 files from raw.githubusercontent.com at the pinned commit, 271 MB in total.
- Each file matched the byte size and the git blob SHA-1 from the GitHub tree API (`runs/download.log`, which also records the sha256 values).

**Format check before the batch** (`runs/out/units_check.json`).
- We fitted predicted against stored forces on the first molecule of s66x8 and of ANI-MD (8 conformations each), with stored values converted from Ha/Å to eV/Å.
- The slopes were −0.931 and −0.998. COMP6's `forces` field holds energy gradients, so its sign was flipped. The units are Ha/Å, not Ha/Bohr.
- Energies were converted with 1 Ha = 27.211386245988 eV. The first ANI-MD conformation gives −14022.503 eV predicted against −14022.460 eV reference.

**Inference.**
- Our own script (`runs/scripts/comp6_eval.py`): single-point energy and forces at the stored geometries with `matgl.ext.ase.PESCalculator`, one conformation at a time, non-periodic ASE `Atoms`, float32. This is the primary path in the pre-registration.
- We ran it on the CPU, as 10 processes with 2 threads each. `PESCalculator` does not move graphs to the model's device. With `torch.set_default_device("cuda")` the GPU managed about 0.1 s per small molecule, against 0.034 s on one CPU process.
- The only faster GPU route, batched `Potential` calls, failed the pre-registered agreement test for M3GNet. It must match `PESCalculator` within 1e-4 eV and 1e-4 eV/Å. On 50 ANI-MD conformations the max difference was 0.015625 eV in energy and 0.0078 eV/Å in force (`runs/out/check_batch_vs_calc.jsonl`). The energy difference (0.015625 eV) is one float32 ulp at |E| ≈ 2.1e5 eV, so the 1e-4 eV criterion cannot be met in float32 for large molecules. The force difference (0.0078 eV/Å) and the per-file batched comparison show the three-body batch dependence. We kept `PESCalculator`, the primary pre-registered path.
- Separately, loading SO3Net while `torch.set_default_device("cuda")` was active failed with matgl's generic "Unknown error occurred while loading model". We did not dig into it, since the run did not need the GPU.

**Runtime and restarts.**
- 304,056 model-conformation evaluations took 24.6 process-hours: M3GNet 6.3, TensorNet 6.2, SO3Net 12.1. Wall clock was about 3.5 h.
- One job (SO3Net on ANI-MD) was OOM-killed because we had started the batched side run at the same time. It was rerun alone (1,005 s). The driver skips finished (model, file) outputs.

**Scoring and outputs.**
- `runs/scripts/score.py` produced `runs/results_main.{json,md}`.
- Per-conformation predictions are in `runs/out_main/*.npz`: reference and predicted energy, every force component, molecule and conformation index.

**Changes to the authors' code:** none. The `data/matgl` checkout is clean at a6ebaebd (empty git status), and the installed matgl 1.3.0 package is byte-identical to `src/matgl` at the tag (diff -rq).

**Correction to a pre-registration note.** The D-CHECKPOINT annotation in `claims.json` says the model-card split does not match the 0.2/0.05/0.05 ratio. That is wrong: 991,735/248,355/248,355 is 4:1:1, the same as 0.2:0.05:0.05. The note is corrected here. The frozen file was not changed, and the note is an observation, not a definition, so no scored claim depends on it.

## Notes for the authors

Thanks for releasing the ANI-1x checkpoints with the library. They load and run cleanly from the v1.3.0 tag. We tried to reproduce Fig. 4 (COMP6) from them and could not, so here is what we found:

1. **Fig. 4 does not come back from the released weights with the obvious evaluation.** We used single-point `PESCalculator` predictions on all 101,352 COMP6 v1 conformations, per-atom energy MAE and component force MAE. Only 4 of the 36 bars match within 5%.
   - The ANI-MD bars are 2.3 to 4 times higher than what we get in energy: TensorNet 11.1 against 2.8 meV/atom, SO3Net 2.3 against 1.0.
   - On ANI-MD the force bars are 1.25× ours for all three models (1.250, 1.255, 1.249). A common factor across three architectures points to a difference in normalisation or in the ANI-MD set (the text says 16 systems; `ani_md_bench.h5` has 14), not to the models. Elsewhere the force ratio ranges from 0.65 to 1.30, so there is no global scale factor. Which version of ANI-MD did you use, and which atom count went into the per-atom normalisation?
   - The GDB 12-13 and Drugbank bars are mostly lower than ours.
   - The figure gives SO3Net force 0.044 for ANI-MD, GDB 12-13 and Drugbank. We get 0.035, 0.049 and 0.034, which does not support three equal values. Could one of these be a data-entry error in the figure?
   - None of the averaging variants we tried closes the gap, including the literal reading of the GDB labels and molecule-relative energies.
   - Could you share the script that made Fig. 4? Also: which checkpoints it used, whether energies were absolute or relative, and which COMP6 files went into "GDB 9-11" and "GDB 12-13". COMP6 ships GDB07to09 and GDB10to13.
   - Per-molecule numbers would also settle this quickly.
2. **The M3GNet three-body indexing in 1.3.0 makes batched predictions depend on batch composition.** In our tests that was up to 0.9 meV/atom and 0.047 eV/Å per molecule, while the MAE moved by less than 0.03 meV/atom. PR #840 fixes this for 4.x. It may be worth a note on the 1.3.0 models, since they were trained and evaluated with this behaviour.
3. **`matgl.ext.ase` in 1.3.0 does not import with ase 3.29**, because `ExpCellFilter` was removed there. A pin such as `ase<3.27` in the 1.x line would help people running these DGL checkpoints.
4. **Small text and model-card items:**
   - p. 5 describes ANI-MD as "14 well-known drug molecules and 2 small proteins". `ani_md_bench.h5` holds 14 systems: 12 drugs plus Chignolin and Trp-cage (312 atoms).
   - SI Table S5 gives num_rbf 32 for TensorNet, while the released model.json has 3. This has no effect on the model: with rbf_type SphericalBessel, `_tensornet.py` sets num_rbf = max_n (3). The SI entry is cosmetic.
   - The SO3Net model card calls itself "a M3GNet potential".
   - The Table 5 caption gives a 0.9/0.05/0.05 split, while Dataset details gives 0.2/0.05/0.05 for the ANI-1x subset. The model-card split (991,735/248,355/248,355) matches the 0.2/0.05/0.05 version.
   - TensorNet has no model card at the tag.
5. A detail that may save others time: COMP6's `forces` dataset stores energy gradients in Ha/Å, so it needs a sign flip before comparing with MLIP forces.

## How this report was made

This reproduction was run by AI agents (Claude, by Anthropic) on a home computer and reviewed by a human before publication. No number in this report was estimated or typed by hand: each one comes from code that ran on this machine, and the commands, logs and outputs are in this folder.

A single agent built the environment, ran the authors' code and released weights on a Ryzen 9 3900X (the RTX 2070 SUPER 8 GB was used only for checks and a side run), compared the results with the paper and wrote this report. Before any model ran, a separate agent read the paper and pre-registered the 36 claims, every definition the computation needs and the tolerances in `claims.json`, whose hash was fixed and checked again before scoring. After the run, a reviewer agent and a reviser agent checked this report against the logs, and a human approved publication. This was a single-agent run, without blind recomputation by a second agent.

We do this because most published code is never re-run by anyone else, and AI agents make that check cheap. The method, prompts and scripts are public at https://github.com/paper-rerun/paper-rerun/blob/main/METHOD.md, so anyone can run the same checks on papers in their own field.

Contact: Filipe Tessaro, https://github.com/paper-rerun/paper-rerun/issues