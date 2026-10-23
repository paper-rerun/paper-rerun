# Reproduction report: CHGNet as a pretrained universal neural network potential for charge-informed atomistic modelling

- Paper: Bowen Deng, Peichen Zhong, KyuJung Jun, Janosh Riebesell, Kevin Han, Christopher J. Bartel, Gerbrand Ceder. Nature Machine Intelligence 5, 1031-1041 (2023). DOI: 10.1038/s42256-023-00716-3 (preprint arXiv:2302.14231)
- Code: https://github.com/CederGroupHub/chgnet @ b9a6c15860237297a5a5169660e83b2e61a78e76 (v0.4.1-7-gb9a6c15, 2026-09-15). License: modified BSD with the LBNL/UC "Enhancements" clause; GitHub labels it "other".
- Model: pretrained checkpoint `chgnet/pretrained/0.2.0/chgnet_0.2.0_e30f77s348m32.pth.tar`. The repo README says 0.2.0 is the version "published with CHGNet Nature Machine Intelligence paper"; 0.3.0 (the current default) came later and used a different 9:0.5:0.5 split. Loaded with `CHGNet.load(model_name="0.2.0")`, 400,438 parameters as in the paper.
- Data: MPtrj_2022.9_full.json, Figshare article 23713842, 12,188,168,685 bytes, MD5 50ead5f27f9a4f6beb7564c4188f1e9f (checked, matches Figshare). MIT license.
- Target: Table I of arXiv:2302.14231 (Table 1 in the journal version), "MAEs of CHGNet on MPtrj test set of 157,955 structures from 14,572 materials", row "With mag": energy 30 meV/atom, force 77 meV/Å, stress 0.348 GPa, magmom 0.032 μB.
- Verdict: **Partially reproduced**
- Date: 2026-10-22
- Hardware: Ryzen 9 3900X, 64 GB RAM, RTX 2070 SUPER 8 GB, WSL2 Ubuntu 24.04

## Results

The authors' test split cannot be rebuilt (see "What it took"), so we made a test split with the same documented procedure: 10% of mp-ids drawn at random (seed 0), with all their frames. That gives 14,704 materials and 159,000 frames (paper: 14,572 and 157,955). We ran CHGNet 0.2.0 over the whole split on the GPU and computed the MAEs with the authors' own `CombinedLoss`.

| Quantity | Paper, test (Table I) | Ours, full random 10% split (158,823 frames) | Diff vs paper | Expected if ~80% of our split was in the authors' training set |
|---|---|---|---|---|
| Energy (meV/atom) | 30 | 23.4 (95% CI 22.7-24.2) | -6.6 | 23.6 |
| Force (meV/Å) | 77 | 57.6 | -19.4 | 62.4 |
| Stress (GPa) | 0.348 | 0.270 | -0.078 | 0.267 |
| Magmom (μB) | 0.032 | 0.0299 | -0.0021 | 0.0305 |

CI on energy: 2,000 bootstrap resamples over materials. Only energy is logged per frame, so force, stress and magmom have point values only. Sizes behind each MAE: 158,823 energies, 14,745,795 force components, 1,429,407 stress components, 794,604 labelled magmoms. 177 frames (0.11%) could not be turned into graphs (isolated atoms at the 5 Å cutoff) and were skipped, which is what the authors' training code does too.

An earlier CPU run on a random 20,000-frame sample of the same split gave 23.7 / 57.3 / 0.274 / 0.0318. On the first 4,000 shared frames the CPU and GPU runs agree to 0.1 meV/atom (`logs/eval_test_seed0_gpu_bs40_stopped.log` vs `logs/eval_test_seed0_cpu20k_model0.2.0.log`).

How to read this. Our split is random, the authors' split was random, and the two are independent. So about 80% of our test materials were in the authors' training set, 10% in their validation set and 10% in their test set. The checkpoint's README (`chgnet/pretrained/0.2.0/README.md`) lists the 0.2.0 MAEs per partition: train 22 / 59 / 0.246 / 0.030, validation 30 / 75 / 0.350 / 0.033, test 30 / 77 / 0.348 / 0.032. Mixing them 0.8 / 0.1 / 0.1 gives the last column. Energy, stress and magmom land on that mix within 2%. Force comes out 5 meV/Å below the mix, and even below the README train value (59). Our guess is that the README train number is the running average over the last training epoch, taken while the weights were still moving, which would make it a bit pessimistic; we can't check that.

What this means for the paper's claim: the released model, the published data and the authors' metric code give numbers that agree with the per-partition errors the authors report. But our evaluation is mostly in-sample, so on its own it cannot confirm the held-out test error (30 / 77 / 0.348 / 0.032). That is why the verdict is "Partially reproduced" and not "Reproduced". Getting to "Reproduced" needs the authors' list of test mp-ids.

Dataset counts match the paper exactly: 145,923 materials and 1,580,395 frames in the file.

## What it took

Steps:

1. Cloned the repo and read `chgnet/pretrained/0.2.0/README.md` to confirm 0.2.0 is the paper checkpoint and that its split was 8:1:1.
2. Looked for the split. `GraphData.get_train_val_test_loader` and `StructureJsonData.get_train_val_test_loader` in `chgnet/data/dataset.py` call `random.shuffle(mp_ids)` with no seed, and no list of test mp-ids is in the repo, the Figshare record, the paper or the issue tracker (searched for split, test set, MPtrj, reproduce). The paper (Methods) only says the sets "were randomly selected based on the 145,923 compounds (based on the mp-id)". So the exact split is lost.
3. Downloaded the 12.2 GB JSON, about 1 h. The Figshare transfer stalled twice and was resumed with `curl -C -`.
4. Built the test split on Windows with `scripts/make_test_split.py`. It streams the JSON with ijson (yajl2_c backend, one material in memory at a time), draws one uniform number per mp-id with `random.Random(0)`, keeps the material if the number is below 0.1, and writes its frames to a 1.2 GB JSONL (`data/mptrj_test_seed0.jsonl`; ids and counts in `data/mptrj_test_seed0_ids.json`). It ran while the download was still going, 29 min total.
5. Evaluated with `scripts/eval_test.py` in WSL. It converts each structure with the model's own `graph_converter` (5 Å / 3 Å cutoffs for 0.2.0), applies the same label transforms as `StructureData.__getitem__` (stress times -0.1, i.e. VASP kBar to GPa with the sign flip; absolute magmom; frames without magmom left out of the magmom MAE), runs `model(graphs, task="efsm")`, and averages the per-batch `CombinedLoss` MAEs weighted by the sizes the loss returns. That is the same arithmetic as `Trainer._validate`. Batch size only changes speed, not the MAE.
6. Full split on the GPU, batch 8: 57 min of compute (about 47 frames/s), under the shared GPU lock.

Wall clock: about 7 h from start to the full result. Roughly 1 h download, 29 min split (overlapped with the download), 53 min for the CPU subset, 57 min for the full GPU run, and over 3 h waiting for the shared GPU.

Changes to the authors' code: none, so `patches/` is empty. Our two scripts are in `scripts/`. Environment fixes:

- System Python 3.12 had no `Python.h`, so chgnet's Cython graph converter would not build, and apt was locked by another job. Fixed by using a uv-managed Python (`uv venv --managed-python -p 3.12`).
- The PyTorch DataLoader ran out of file handles passing the many small graph tensors between workers (`Too many open files`). Fixed with `torch.multiprocessing.set_sharing_strategy("file_system")` in our script.
- Speed: with batch 40 the GPU run did about 11 frames/s with the main process at 90% CPU; batch 8 did 47-57 frames/s. Per-frame cost grows with batch size in this setup (we saw the same on CPU). We did not dig into why.
- Environment: chgnet from the clone (0.4.1), torch 2.14.1+cu130, pymatgen 2026.9.24, numpy 2.5.4, ase 3.29.0, Python 3.12.15. Full lock in `env/requirements.lock.txt`. The Windows splitter only needs ijson 3.6.0 (`env/requirements-windows-split.lock.txt`).

We did not use the 2023-era chgnet 0.2.x package. The repo keeps 0.2.0 loadable "for backward compatibility with NMI paper" and sets `mlp_out_bias=True` for it, so we took the current code as the intended way to run that checkpoint.

Independent reproductions: we found none that re-evaluates the released CHGNet on an MPtrj test split. Matbench Discovery benchmarks CHGNet on WBM, a different out-of-distribution task, and FastCHGNet (arXiv:2412.20796) retrains the architecture instead of checking the released model. No issue in CederGroupHub/chgnet reports an attempt to reproduce Table I.

Files: `logs/eval_test_seed0_full_model0.2.0.log` (full run log), `logs/test_seed0_full_model0.2.0_result.json` (MAEs, sizes, skipped frames), `logs/test_seed0_full_model0.2.0_energy_errors.csv` (per-frame energy error); the same three for the 20k CPU run (`*cpu20k*`); `logs/eval_test_seed0_gpu_bs40_stopped.log` (batch-40 run stopped for speed); `logs/make_test_split.log`, `logs/md5.log`, `logs/download*.log`, `logs/env_setup.log`, and a 302-frame smoke test in `logs/smoke_0.2.0_result.json`. The 12 GB JSON and the 1.2 GB test JSONL stay in `data/` and should not be committed.

## Notes for the authors

Draft issue, not posted:

> **Publish the MPtrj train/val/test mp-ids used for the NMI paper (model 0.2.0)?**
>
> Hi, we tried to reproduce Table 1 of the NMI paper (test MAEs 30 meV/atom, 77 meV/Å, 0.348 GPa, 0.032 μB) with the released 0.2.0 weights and MPtrj_2022.9_full.json. The model, the data and your `CombinedLoss` all work fine. On a random 10% mp-id split (159k frames) we get 23.4 / 57.6 / 0.270 / 0.030, which matches a 0.8/0.1/0.1 mix of the train/val/test MAEs in `pretrained/0.2.0/README.md`. But `get_train_val_test_loader` shuffles the mp-ids without a seed and we couldn't find the ids saved anywhere, so there is no way to evaluate on the actual held-out materials, and the test numbers can't be checked from outside.
>
> Would it be possible to publish the test (and val) mp-ids for 0.2.0 and 0.3.0, for example as a JSON next to the checkpoints or on the MPtrj Figshare record? A `seed` argument on `get_train_val_test_loader` would also help. Thanks!
>
> Smaller point: `StructureData.__getitem__` and `GraphData.__getitem__` replace a structure that fails graph conversion with a random other one. That is fine for training, but it double-counts frames if someone uses those datasets to compute a test MAE.

## How this report was made

This reproduction was run by AI agents (Claude, by Anthropic) on a home computer and reviewed by a human before publication. No number in this report was estimated or typed by hand: each one comes from code that ran on this machine, and the commands, logs and outputs are in this folder.

A single agent read the paper, built the environment, ran the authors' code and released weights on one RTX 2070 SUPER (8 GB) and a Ryzen 9 3900X, compared the results with the paper and wrote this report. A coordinating agent checked the report against the logs, and a human approved publication. This was a pilot run, before we added blind recomputation by a second agent.

We do this because most published code is never re-run by anyone else, and AI agents make that check cheap. The method, prompts and scripts are public at https://github.com/paper-rerun/paper-rerun/blob/main/METHOD.md, so anyone can run the same checks on papers in their own field.

Contact: Filipe Tessaro, https://github.com/paper-rerun/paper-rerun/issues
