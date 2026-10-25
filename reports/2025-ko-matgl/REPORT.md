# Reproduction report: Materials Graph Library (MatGL), an open-source graph deep learning library for materials science and chemistry

- Paper: Ko, Deng, Nassar et al., npj Computational Materials 11, 253 (2025). DOI: 10.1038/s41524-025-01742-y (preprint arXiv 2503.03837)
- Code: https://github.com/materialyzeai/matgl @ a6ebaebd6a0021e14d49d001103508c4980d94da (tag v1.3.0)
- Data: https://github.com/isayev/COMP6 @ 79f41c156f8e19506fe951b5513b98e7c534a503 (COMP6 v1, all 11 HDF5 files)
- Target: Fig. 4 (COMP6 energy and force MAE) for M3GNet, TensorNet and SO3Net (36 bars), the 6 ANI-MD numbers quoted in the p.5 text, and 2 numbers describing the ANI-MD dataset. M3GNet-TL is not covered: its weights are not in the v1.3.0 repository or on the materialyze Hugging Face account.
- Verdict: Not reproduced. In both independent runs, 3 of the 36 independent Fig. 4 values fall within the tolerance we fixed in advance, and all 3 are in the Tripeptides group. No model reproduces a whole energy or force series. The project's rules define "Partially reproduced" as "part matches, part does not", and read literally that would apply here. We chose "Not reproduced" anyway. The 3 matches are isolated values inside series whose other values miss by 100 to 1000 times the tolerance, and the misses go both up and down. Even the Tripeptides group is not reproduced as a whole: 3 of its 6 bars match, but M3GNet Tripeptides energy and force and TensorNet Tripeptides energy do not. We did not test whether the 3 matches are coincidence.
- Date: 2026-10-25
- Hardware: Ryzen 9 3900X, 64 GB RAM (31 GB visible to WSL2), RTX 2070 SUPER 8 GB, WSL2 Ubuntu 24.04


> This paper was checked twice, independently. This report is the full pipeline run (claims map, execution, blind recomputation, review). An earlier standard-mode run, with its own pre-registration and evaluation code, reached the same numbers; it is in [standard/REPORT.md](standard/REPORT.md).

## Results

**Definitions.** These are the definitions in `claims.json` (v1, written 2026-10-24 16:52:08, before any model ran) plus three corrections recorded in `claims_v2.json`:
- Energy MAE is computed per conformation as |E_pred − E_DFT| / n_atoms on total energies, then averaged over conformations, in meV/atom. MatGL's own `training.py` uses the same metric at v1.3.0.
- Force MAE is the mean absolute error over every Cartesian component, pooled over the whole group, in eV/Å.
- COMP6 energies and forces were converted from Ha and Ha/Å with `ase.units.Hartree`. No energy offset was fitted.
- Multi-file groups were pooled into one MAE. "GDB 9-11" is gdb11_09 + gdb11_10 + gdb11_11 (35,670 conformations). "GDB 12-13" is gdb13_12 + gdb13_13 (24,000).
- All 101,352 conformations were used, and none failed.

Where the v2 corrections came from: the claims-check stage (scripts in `claims_check/`, dated 16:54 to 16:58 on 2026-10-24) returned a corrected claim list, but that stage did not save it to disk. `claims_v2.json` was written during the revision of this report on 2026-10-25. It keeps v1 untouched, lists only the three changes the later stages applied, and points to the earliest file on disk that shows each one. The first model call on disk is `logs/smoke_test.log`, at 17:12:19. The three changes:
1. **Force unit test.** v1 sets the force sign from Pearson r alone. v2 adds a least-squares slope through the origin and requires |slope| between 0.8 and 1.25 to accept Ha/Å. That window first appears on disk in `exec/comp6-m3gnet/signcheck.py` at 17:14:48. This is after the smoke test but before the first sign and unit decision (`signcheck.json`, 17:16:53). Nothing on disk shows that the window existed earlier.
2. **ANI-MD atom count.** v1 records the claim as the literal sentence "the molecules in the ANI-MD dataset have 312 atoms". v2 scores it as "atoms in the largest ANI-MD molecule". This reading was chosen after `claims_work/animd_molecules.txt` (16:49) had already shown that only Trp-cage has 312 atoms (see the dataset table below).
3. **63-atom training claim.** v2 adds an optional item, `data-train-maxatoms` ("largest training molecule has 63 atoms"), which may be skipped without penalty. It was not in v1. The first file that shows it is `exec/data-description-optional/results.json`.

**Paper values.** The authors published no table for Fig. 4, so the paper values come from the figure itself. We read them from the vector paths in the journal PDF (p.7), calibrated on the axis ticks. A second agent read them again with its own script and got the same values. Every bar height lies within 1.4e-4 of a 3-decimal value.

**Tolerances.** The energy tolerance is ±0.01 meV/atom and the force tolerance is ±0.0006 eV/Å. They come from the 3-decimal plotting resolution plus a budget for float32 arithmetic and unit conversion. Values quoted in the text get half a unit of their last digit.

**The two runs.** Run 1 is the main computation, done one structure at a time. Run 2 is the blind recomputation: a separate environment built from the lockfile, scoring code written separately, and batched inference. Diff is Run 1 minus Paper. "Within tol." is "yes" only when both runs pass.

| Quantity | Paper | Tol. | Ours (run 1) | Ours (run 2, blind) | Diff | Within tol. |
|---|---|---|---|---|---|---|
| M3GNet, ANI-MD, energy (meV/atom) | 19.159 | ±0.01 | 7.669 | 7.677 | −11.490 | no |
| M3GNet, GDB 9-11, energy (meV/atom) | 8.925 | ±0.01 | 4.909 | 4.910 | −4.016 | no |
| M3GNet, GDB 12-13, energy (meV/atom) | 3.655 | ±0.01 | 6.514 | 6.516 | +2.859 | no |
| M3GNet, Drugbank, energy (meV/atom) | 12.010 | ±0.01 | 8.930 | 8.935 | −3.080 | no |
| M3GNet, S66x8, energy (meV/atom) | 9.835 | ±0.01 | 7.504 | 7.533 | −2.331 | no |
| M3GNet, Tripeptides, energy (meV/atom) | 2.662 | ±0.01 | 5.703 | 5.702 | +3.041 | no |
| M3GNet, ANI-MD, force (eV/Å) | 0.142 | ±0.0006 | 0.1136 | 0.1136 | −0.0284 | no |
| M3GNet, GDB 9-11, force (eV/Å) | 0.074 | ±0.0006 | 0.0914 | 0.0914 | +0.0174 | no |
| M3GNet, GDB 12-13, force (eV/Å) | 0.118 | ±0.0006 | 0.1367 | 0.1367 | +0.0187 | no |
| M3GNet, Drugbank, force (eV/Å) | 0.126 | ±0.0006 | 0.1065 | 0.1065 | −0.0195 | no |
| M3GNet, S66x8, force (eV/Å) | 0.029 | ±0.0006 | 0.0449 | 0.0449 | +0.0159 | no |
| M3GNet, Tripeptides, force (eV/Å) | 0.067 | ±0.0006 | 0.0767 | 0.0767 | +0.0097 | no |
| TensorNet, ANI-MD, energy (meV/atom) | 11.099 | ±0.01 | 2.798 | 2.798 | −8.301 | no |
| TensorNet, GDB 9-11, energy (meV/atom) | 1.705 | ±0.01 | 4.102 | 4.102 | +2.397 | no |
| TensorNet, GDB 12-13, energy (meV/atom) | 3.252 | ±0.01 | 5.071 | 5.071 | +1.819 | no |
| TensorNet, Drugbank, energy (meV/atom) | 1.123 | ±0.01 | 2.797 | 2.797 | +1.674 | no |
| TensorNet, S66x8, energy (meV/atom) | 6.031 | ±0.01 | 5.671 | 5.671 | −0.360 | no |
| TensorNet, Tripeptides, energy (meV/atom) | 2.248 | ±0.01 | 3.099 | 3.099 | +0.851 | no |
| TensorNet, ANI-MD, force (eV/Å) | 0.099 | ±0.0006 | 0.0789 | 0.0789 | −0.0201 | no |
| TensorNet, GDB 9-11, force (eV/Å) | 0.056 | ±0.0006 | 0.0807 | 0.0807 | +0.0247 | no |
| TensorNet, GDB 12-13, force (eV/Å) | 0.090 | ±0.0006 | 0.1087 | 0.1087 | +0.0187 | no |
| TensorNet, Drugbank, force (eV/Å) | 0.086 | ±0.0006 | 0.0764 | 0.0764 | −0.0096 | no |
| TensorNet, S66x8, force (eV/Å) | 0.045 | ±0.0006 | 0.0382 | 0.0382 | −0.0068 | no |
| TensorNet, Tripeptides, force (eV/Å) | 0.067 | ±0.0006 | 0.0667 | 0.0667 | −0.0003 | **yes** |
| SO3Net, ANI-MD, energy (meV/atom) | 2.283 | ±0.01 | 1.009 | 1.009 | −1.274 | no |
| SO3Net, GDB 9-11, energy (meV/atom) | 3.889 | ±0.01 | 1.968 | 1.968 | −1.921 | no |
| SO3Net, GDB 12-13, energy (meV/atom) | 1.271 | ±0.01 | 2.347 | 2.347 | +1.076 | no |
| SO3Net, Drugbank, energy (meV/atom) | 0.969 | ±0.01 | 1.454 | 1.455 | +0.485 | no |
| SO3Net, S66x8, energy (meV/atom) | 2.558 | ±0.01 | 1.661 | 1.661 | −0.897 | no |
| SO3Net, Tripeptides, energy (meV/atom) | 1.245 | ±0.01 | 1.243 | 1.243 | −0.002 | **yes** |
| SO3Net, ANI-MD, force (eV/Å) | 0.044 | ±0.0006 | 0.0352 | 0.0352 | −0.0088 | no |
| SO3Net, GDB 9-11, force (eV/Å) | 0.032 | ±0.0006 | 0.0393 | 0.0393 | +0.0073 | no |
| SO3Net, GDB 12-13, force (eV/Å) | 0.044 | ±0.0006 | 0.0548 | 0.0548 | +0.0108 | no |
| SO3Net, Drugbank, force (eV/Å) | 0.044 | ±0.0006 | 0.0338 | 0.0338 | −0.0102 | no |
| SO3Net, S66x8, force (eV/Å) | 0.011 | ±0.0006 | 0.0154 | 0.0154 | +0.0044 | no |
| SO3Net, Tripeptides, force (eV/Å) | 0.029 | ±0.0006 | 0.0291 | 0.0291 | +0.0001 | **yes** |

Numbers quoted in the p.5 text. These come from the same ANI-MD computation as 6 of the bars above, so they are not independent of the figure and do not count toward the 3 of 36:

| Quantity | Paper | Tol. | Ours (run 1) | Ours (run 2, blind) | Diff | Within tol. |
|---|---|---|---|---|---|---|
| M3GNet energy "above 14 meV/atom" | > 14 | inequality | 7.669 | 7.677 | −6.331 | no |
| M3GNet force "above 0.14 eV/Å" | > 0.14 | inequality | 0.1136 | 0.1136 | −0.0264 | no |
| TensorNet energy "11 meV/atom" | 11 | ±0.5 | 2.798 | 2.798 | −8.202 | no |
| TensorNet force "0.1 eV/Å" | 0.1 | ±0.05 | 0.0789 | 0.0789 | −0.0211 | **yes** |
| SO3Net energy "2.3 meV/atom" | 2.3 | ±0.05 | 1.009 | 1.009 | −1.291 | no |
| SO3Net force "0.044 eV/Å" | 0.044 | ±0.0005 | 0.0352 | 0.0352 | −0.0088 | no |

The TensorNet force text value passes only because the paper rounds it to one significant figure ("0.1"). The same quantity misses the Fig. 4 bar (0.099 ± 0.0006) by 0.020 eV/Å.

Dataset description (p.5), counted from `ani_md_bench.h5` (git blob d168ba5e):

| Quantity | Paper | Ours (both runs) | Within tol. |
|---|---|---|---|
| ANI-MD trajectories ("14 well-known drug molecules and 2 small proteins") | 16 | 14 | no |
| ANI-MD atom count. Literal reading (v1): "the molecules in the ANI-MD dataset have 312 atoms". Reading B (v2): atoms in the largest molecule | 312 | 312 in 1 of 14 molecules; the other 13 have 20 to 149 | ambiguous: no under the literal reading, yes under reading B |
| Atoms in the largest training molecule ("63 atoms") | 63 | not computed | skipped |

The ANI-MD file holds 12 drugs plus ChignolinNeutral (149 atoms) and TrpCage1L2Y (312 atoms). Only Trp-cage has 312 atoms, and the largest drug, Atazanavir, has 103. The literal wording registered in `claims.json` v1 fails. The "largest molecule" reading, which passes, was adopted after the file contents were known. The 63-atom claim needs the multi-GB ANI-1x release, which we did not download. That item was added in v2 as optional, so it could be skipped without penalty.

**How well the two runs agree.** They agree to 0.0001 eV/Å or better on every force value. They also agree to 0.0001 meV/atom or better on every TensorNet and SO3Net energy. M3GNet energies differ more: 0.0289 meV/atom on S66x8, 0.0081 on ANI-MD and 0.0052 on Drugbank. Run 2 ran M3GNet in batches of up to 1500 atoms. On the 44 M3GNet conformations it checked against matgl's single-structure ASE calculator, the batched energies differ by up to 0.0078 eV (a 60-atom tripeptide) and the forces by up to 0.012 eV/Å per component (`verify/crosscheck_ase.json`). Run 1's own batch test showed the same effect. At batch size 16 the S66x8 MAE was 7.517 instead of 7.504, and single structures moved by up to 0.67 meV/atom at batch size 32 (`exec/comp6-m3gnet/batched_sensitivity.json`). So the M3GNet S66x8 energy carries about 0.03 meV/atom of run-to-run spread, which is more than its 0.01 tolerance. The gaps to the paper are 100 to 1000 times larger than this spread, so the verdict does not depend on it.

## What it took

1. **Environment.** matgl 1.3.0 was installed editable from the tag, with no source changes. The authors' `uv.lock` pins torch 2.2.0 together with dgl 2.4.0 built for torch 2.4, and those two do not install together. We followed the v1.3.0 CI instead: torch 2.4.0+cu121, dgl 2.4.0+cu121 and torchdata 0.8.0. Every other package is pinned to the version in the authors' lock. The only addition is h5py 3.16.0, to read COMP6. The lockfile is at `env/requirements.lock.txt` and the rebuild script at `env/setup.sh`. A full rebuild takes about 10 minutes.
2. **Weights.** We used `pretrained_models/{M3GNet,TensorNet,SO3Net}-ANI-1x-Subset-PES` from the tag, loaded by path, because loading by name returns a 404 (issue #680). All three `state.pt` files match Hugging Face byte for byte. The TensorNet `model.json` on Hugging Face points to a module that does not exist in 1.3.0, so we used the copy from the tag. matgl 1.3.0 loads weights with `strict=False`, so we checked each `state.pt` against the model that `load_model` builds. All three load with no missing, unexpected or reshaped tensors, and the loaded values equal the stored ones exactly:
   - TensorNet: 69 tensors (`exec/comp6-tensornet/keycheck.log`)
   - SO3Net: 46 tensors (`exec/comp6-so3net/keycheck.log`)
   - M3GNet: 115 tensors (`exec/comp6-m3gnet/keycheck.log`). This check was added on 2026-10-25, during the revision of this report.
3. **Force sign.** The COMP6 `forces` arrays are stored as the gradient (+dE/dR), not as forces. Before the batch we checked two molecules (Caffeine from ANI-MD and gdb11_s09/mol0000) with all three models. The model forces correlated with the stored values at r between −0.985 and −0.999. The slope through the origin was between −0.988 and −1.005. Under the v1 sign rule (r < −0.9 means flip), we flipped the sign. Under the v2 unit test (|slope| between 0.8 and 1.25), we kept Ha/Å. Without the flip, the force MAE per group is about 0.25 eV/Å (S66x8) to 2.75 eV/Å (GDB 12-13).
4. **Inference.** The evaluation path is Atoms2Graph followed by the Potential forward pass, the same as `PESCalculator.calculate`, in float32 on the GPU. Run 1 compared 3 conformations per model with matgl's own ASE `PESCalculator` on CPU. Energies matched to the last float32 digit, and forces agreed within 1.4e-5 eV/Å. Run 2 checked 132 random conformations (44 per model) against the same calculator, using its batched predictions. The worst gaps by model:
   - M3GNet: 0.0078 eV in energy and 0.012 eV/Å per force component
   - TensorNet: 0.001 eV and 1.9e-5 eV/Å
   - SO3Net: 0 eV and 1.3e-5 eV/Å
5. **Runtime.** Run 1 used batch size 1 and took about 3 h 15 min for M3GNet, 90 min for TensorNet and 2.6 h for SO3Net. Run 2 used batched inference and took about 40 min of GPU time for SO3Net and a few minutes each for the other two.
6. **One crash.** In run 2, SO3Net was first launched with batches of up to 1500 atoms. The run stopped with `CUDA error: device not ready`, and a retry was followed by a full machine freeze at about 05:00. The likely cause was GPU memory: one 312-atom Trp-cage structure already needs 4.8 GB (`verify/probe_mem.py`), so 1500-atom batches probably went past the 8 GB card. That is an inference, though. The error was "device not ready", not the out-of-memory error PyTorch normally raises. `verify/logs/predict2.log` ends after model loading, so nothing records what happened at the freeze, and a driver or WSL GPU failure under load cannot be ruled out. After the reboot we checked the environment, the repository state and the prediction files already on disk. Nothing written to disk was lost. SO3Net was then rerun with batches capped at 10,000 edges. This changed only our own script (`verify/predict.py --batch-edges`), not the authors' code or method.
7. **Patches.** None. No author code, model setting or hyperparameter was changed. M3GNet ran with the v1.3.0 three-body indexing code as released (PR #840 came later), because that is the code from the paper's time.

## Alternative readings

All of these were computed after we saw the main results. Some were listed as possible alternatives when the definitions were fixed, but none of them can change the verdict.

- **Other GDB groupings** (planned in advance as a sensitivity check). Reading B (gdb11_07 to gdb11_11, 59,670 conformations) gives an energy MAE of 4.219 / 3.749 / 1.823 meV/atom for M3GNet / TensorNet / SO3Net. Reading C (the COMP6 folder GDB07to09) gives 3.521 / 3.378 / 1.678. For GDB 12-13, reading C (folder GDB10to13) gives 5.901 / 4.695 / 2.196. None comes near the paper's 8.925 / 1.705 / 3.889 or 3.655 / 3.252 / 1.271. The paper also shows M3GNet with a lower energy error on GDB 12-13 than on GDB 9-11. Under every reading we tried, all three models get worse as the number of heavy atoms grows.
- **Other metrics** (computed in run 1):
  - Total-energy MAE divided by the mean atom count gives ANI-MD values of 12.578 / 3.830 / 1.163 meV/atom.
  - The mean of per-conformation force MAEs gives 0.0916 / 0.0665 / 0.0304 eV/Å.
  - The per-atom force-vector norm gives 0.229 / 0.158 / 0.071 eV/Å.
  - Averaging per-file MAEs instead of pooling changes the GDB energies by less than 0.01 meV/atom. For force, the change is up to 0.0014 eV/Å (M3GNet GDB 9-11: 0.0914 pooled, 0.0901 averaged), 0.0011 for TensorNet and 0.0006 for SO3Net. That is at or above the force tolerance, so the pooling choice matters at tolerance level, but the shifts are 5 to 20 times smaller than the gaps.

  None of these matches the figure for all three models.
- **Energy offset.** M3GNet's error on the non-GDB sets is mostly a constant positive offset: the mean signed error is +7.14 meV/atom on ANI-MD and +8.15 on Drugbank. SO3Net's offsets are small (+0.39 to +1.47 meV/atom). TensorNet's offsets vary in sign. On S66x8, its +4.36 meV/atom offset makes up most of its 5.67 meV/atom MAE. On GDB 12-13 and Tripeptides its offsets are −1.60 and −1.43, against MAEs of 5.07 and 3.10. Following the definitions, we report the offsets and do not remove them.
- **ANI-MD by molecule.** For M3GNet, only the two peptides come close to the paper's ANI-MD level: Chignolin at 24.58 and Trp-cage at 18.62 meV/atom. For TensorNet, no molecule reaches 11 meV/atom; the highest is Chignolin at 8.41. For SO3Net, the highest is Trp-cage at 1.745. So no subset of this file can produce the paper's TensorNet or SO3Net ANI-MD bars with these weights.
- **What could explain the gap** (a hypothesis we did not test). Some of our values are higher than the paper's and some are lower, and the datasets rank differently. A pure unit factor would scale every value by the same ratio, and the gaps of mixed sign rule that out. The other normalizations we computed (listed above) do not match the figure either. The pattern fits Fig. 4 having been made with different checkpoints, a different matgl version or a different evaluation set. One concrete lead: the TensorNet `model.pt` (init args) on Hugging Face differs from the one at the tag, even though `state.pt` is identical.

## Notes for the authors

Thanks for releasing the code, the weights and the model configs. They made this check possible. Here is what we found, written as we would put it in a GitHub issue:

1. **Fig. 4 does not reproduce with the v1.3.0 weights.** We evaluated all 101,352 COMP6 v1 conformations with the released ANI-1x-Subset PES models. 3 of the 36 bars match: SO3Net Tripeptides energy and force, and TensorNet Tripeptides force. The rest differ in both directions, for example TensorNet ANI-MD energy at 2.80 versus 11.10 meV/atom. Could you share the evaluation script and the matgl version and checkpoints used for Fig. 4? Per-group numbers would also help, as would the definition of "meV/atom" and how the GDB files were grouped ("GDB 9-11" and "GDB 12-13" do not match any COMP6 folder).
2. **COMP6 force sign.** The COMP6 v1 `forces` field stores the energy gradient, so model forces must be compared against the negated values. Without the flip, the force MAEs come out at about 0.25 eV/Å (S66x8) to 2.75 eV/Å (GDB 12-13) per group, so the figure was probably made with the flip. Saying so explicitly would save others time.
3. **ANI-MD description.** The file has 14 trajectories (12 drugs and 2 peptides), not "14 drugs and 2 small proteins". Only Trp-cage has 312 atoms.
4. **The "trend in other datasets" sentence.** The paper says the ordering with M3GNet worst and SO3Net best also holds on the other datasets, but the paper's own figure does not show that everywhere:
   - GDB 9-11 energy: TensorNet 1.705 < SO3Net 3.889 < M3GNet 8.925.
   - S66x8 force: M3GNet 0.029 < TensorNet 0.045.
   - Tripeptides force: M3GNet and TensorNet tie at 0.067.
5. **Small items.**
   - arXiv v1 says "Table 4" where it means Fig. 4.
   - The TensorNet weights folder has no README.
   - The SO3Net README calls the model "a M3GNet potential".
   - The Table 5 caption gives a 0.9/0.05/0.05 split, while Methods gives 0.2/0.05/0.05.
   - `load_model` by name returns a 404 at v1.3.0 (#680).
   - The TensorNet `model.json` on Hugging Face does not load with 1.3.0.
   - The pinned `uv.lock` combines torch 2.2.0 with dgl 2.4.0 built for torch 2.4, and those do not install together.
6. **M3GNet batching.** In v1.3.0, M3GNet results depend on how structures are batched: up to 0.008 eV in energy and 0.012 eV/Å per force component on the conformations we checked. TensorNet and SO3Net stay within 0.001 eV and 2e-5 eV/Å under the same test, so float32 rounding alone does not seem to explain the M3GNet numbers. This may be related to the three-body indexing fixed in PR #840, but we did not test that. It is far too small to explain the Fig. 4 gaps, but it matters for anyone comparing numbers at the 0.01 meV/atom level.

## How this report was made

This reproduction was run by AI agents (Claude, by Anthropic) on a home computer and reviewed by a human before publication. No number in this report was estimated or typed by hand: each one comes from code that ran on this machine, and the commands, logs and outputs are in this folder.

1. One agent read the paper and listed the numeric claims to check. Every definition the computation needs (cutoffs, test sets, how results are averaged) was fixed from the paper text before anything ran. A second agent checked that list against the paper.
2. One agent built the software environment once and froze it, starting from the versions the authors used.
3. Separate agents computed each group of claims with the authors' code and released weights, on one RTX 2070 SUPER (8 GB) and a Ryzen 9 3900X.
4. A different agent rebuilt the environment from the frozen lockfile and recomputed every claim without seeing the first results, using scoring code it wrote itself.
5. One agent wrote this report and another one tried to find errors in it.
6. A human read the report and approved publication.

We do this because most published code is never re-run by anyone else, and AI agents make that check cheap. The method, prompts and scripts are public at https://github.com/paper-rerun/paper-rerun/blob/main/METHOD.md, so anyone can run the same checks on papers in their own field.

Contact: Filipe Tessaro, https://github.com/paper-rerun/paper-rerun/issues