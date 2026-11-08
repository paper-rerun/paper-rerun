# PeSTo (Krapp et al. 2023) — blind independent rerun of Figure 2b

> **Coordinator's note, 2026-11-08.** This report was written by the blind agent and is kept as it
> wrote it, with one correction. Section 3 says the SPPIDER and PSIVER per-residue predictions are
> not in the repository. They are: `masif-site_benchmark/sppider_pred/` holds 57 files and
> `masif-site_benchmark/psiver_pred/psiver_pdbs/` holds 55, in this folder's own checkout. The
> first (non-blind) run scored both from those files and got medians of 0.7345 and 0.6411, against
> 0.73 and 0.64 in the authors' notebook, and the same 38 of 53. So the "38" is checkable from the
> repository without borrowing the authors' columns, and this report's C3 is weaker than it needed
> to be, not wrong. Everything else here was checked against the first run and agrees.

Licence: CC BY-NC-SA 4.0, inherited from the authors' code and weights. Non-commercial use.
Paper: Krapp, Abriata, Cortés Rodriguez, Dal Peraro, *PeSTo: parameter-free geometric deep learning
for accurate prediction of protein binding interfaces*, Nat Commun 14:2175 (2023),
doi 10.1038/s41467-023-37701-8. Code and weights: github.com/LBM-EPFL/PeSTo, commit
`ba651aa29aaa839d0ee2c458dee90ca1f934d90a`.

Run date 2026-11-08. CPU only, nice 19, 4 threads in total (the MaSIF set with one process at 4
threads, the ScanNet set with two processes at 2 threads each). No GPU.

Pre-registration: `claims.json`, SHA-256
`570c7fab607df0cf3b9549cb1ed067d5aec2bf58129320a52f70900cbd746221`, written and hashed before any
bioassembly was downloaded and before the weights were loaded. Re-checked after the run: identical.

## Verdict

**Reproduced.** Both medians come out on the published value, and the agreement is not merely at the
level of the median: 468 of the 469 structures I scored match the authors' own per-structure values
to three decimals. The single structure that disagrees (4DX0_A) and the single structure I could not
build at all (1FSS_A) have the same cause, and I pinned it down: the PDB entries were revised after
the paper was published, and the current biological assembly is no longer the one the authors used.

| Claim | Paper | Mine | My interval | Result |
|---|---|---|---|---|
| C1 median ROC AUC, MaSIF-site benchmark (n=53) | 0.92 | **0.9247** | bootstrap 95% [0.8908, 0.9479] | pass |
| C2 median ROC AUC, set shared with ScanNet (n=417) | 0.93 | **0.9299** (n=416) | [0.9096, 0.9402] | pass |
| C3 PeSTo best of all methods, MaSIF-site set | 38 of 53 | **38 of 53** | — | pass |
| C4 median ROC AUC of MaSIF-site, same 53 (control) | 0.80 | **0.8002** | [0.7639, 0.8421] | pass |
| C5 size of the MaSIF-site benchmark set | 53 entries | **53 entries, 47 sids** | exact match of the sid multiset | pass |

Tolerances were fixed in `claims.json`: ±0.03 for C1 and C4, ±0.02 for C2, ±3 structures for C3,
plus the requirement that each median fall inside the bootstrap interval of the median of the
authors' own per-structure values. All five are satisfied.

## 1. The medians, and how many structures went into each

**MaSIF-site benchmark: median ROC AUC 0.9247 over 53 structures** (mean 0.8565). Every one of the
53 has a defined AUC, so nothing was dropped for want of positives or negatives. The authors'
own Source Data gives 0.9250 over the same 53, which prints as 0.92.

**Set shared with ScanNet: median ROC AUC 0.9299 over 416 structures** (mean 0.8643). The paper
says 417. I could build 416 of the 417; the missing one is 1FSS_A, explained in section 5.
The authors' median over the same 416 sids is 0.9296, and over all 417 it is 0.9294. Supplementary
Table 1 prints 0.929. Replacing my 4DX0_A value with the one computed on the 2023 assembly gives
0.9296, i.e. the same number to three decimals.

Timing, for whoever runs this next: median 9.6 s and mean 10.6 s per structure at 2 threads, max
34.3 s. The paper reports 5.3 ± 2.8 s on CPU and its Source Data has a mean of 5.10 s, so this
machine is about twice as slow per structure, which is what you expect at 2 threads.

## 2. Which items are in the MaSIF-site benchmark set, and does my set match

It matches exactly, and there are two independent ways to check it.

The set is not simply "53 PDB chains". It is 53 **subunit entries** drawn from 47 distinct
`PDBID_chain` names, because the benchmark notebook does not restrict itself to the first
bioassembly: 2AYO_A and 2F4M_A each appear three times, 1W1W_B and 3SJA_I twice. The names come
from `masif-site_benchmark/testing_transient.txt` (53 lines, 53 distinct names), of which 51 have a
per-residue MaSIF-site prediction in `masif_pred_per_res.json`; 2Y5B_A and 4FZV_A do not, and drop
out. Of the 51, four produce no entry at all under the authors' own dataset filters, and six
produce more than one. 51 − 4 + 6 = 53.

I rebuilt the set from the published name list and my own reimplementation of
`processing/build_dataset.py`, with no reference to the authors' per-structure outputs, and then
compared:

- against column A of sheet `Fig2b-comparison` of the Source Data: 53 entries, 47 unique sids, and
  the sid multiplicities agree one for one. No difference anywhere.
- against the file names in `repo/pdbs_test` (159 files = 53 × 3, one prediction, one `_T` ground
  truth and one `_M` MaSIF-site file per entry). The keys encode PDB id, bioassembly number and
  model-tagged chain, e.g. `AY_2AYO_2_A:1`, and my 53 keys are the same 53.

Stronger than name agreement: my reconstructed interface labels are **identical residue by residue
to the authors' released `_T` files on all 53 entries** (zero differing residues). And the
`_M` files match `masif_pred_per_res.json` to two decimals on all 53, which confirms that my residue
ordering is theirs too.

For the ScanNet set the answer is weaker, and that is the paper's fault rather than mine: see
section 4.

## 3. The "38 out of 53" claim

It can be checked, and it comes out at 38.

Two ways. First, from published data alone: the `best` column of sheet `Fig2b-comparison` counts
PeSTo 38, MaSIF-site 10, SPPIDER 3, PSIVER 2 — and recomputing the row-wise argmax over the four
AUC columns gives the same 38/10/3/2, with no ties. So the sentence is internally consistent with
the Source Data.

Second, with my own numbers: replacing the PeSTo column with **my** AUCs and keeping the authors'
MaSIF-site, SPPIDER and PSIVER columns, PeSTo is strictly best on **38 of 53**. The same 38.

I used the authors' values for the other three methods. (See the coordinator's note at the top of
this report: the SPPIDER and PSIVER per-residue predictions are in fact in the repository, and the
first run scored them directly, reaching the same 38.) MaSIF-site is the competitor whose
predictions are published as `masif_pred_per_res.json`, which is why C4 could be recomputed from
scratch.

## 4. What is published and what I had to reconstruct

Published, and used as published:

- the four trained checkpoints, including `i_v4_1` used for the paper;
- the whole inference stack: structure parsing (`src/structure_io.py`), cleaning and subunit
  splitting (`src/structure.py`), feature and topology encoding (`src/data_encoding.py`), the
  network (`model/save/i_v4_1_2021-09-07_11-21/model.py` plus `src/model_operations.py`);
- the MaSIF-site benchmark name list and the MaSIF-site per-residue predictions;
- per-structure AUCs for both panels of Fig 2b, in the Source Data xlsx — this is the single most
  useful thing they released, and it is what makes a claim like "38 out of 53" checkable at all;
- the dataset build script, which is what lets the dataset be rebuilt even though the dataset itself
  is not released.

Not published, reconstructed here:

- **the dataset itself.** `datasets/contacts_rr5A_64nn_8192.h5` is a dangling symlink in the
  repository and the HDF5 is nowhere. Everything downstream — the structures, the interface labels,
  the set membership — had to be rebuilt. I reimplemented `processing/build_dataset.py` in
  `scripts/pesto_rerun.py`: fetch the legacy RCSB biological assembly (`.pdbN.gz`), drop it if the
  raw atom count including waters and hydrogens is ≥ 8192, clean, tag non-polymer chains, split by
  chain, drop non-atomic and duplicate subunits, require at least two subunits, then take 5 Å
  residue–residue contacts. The label is column 0 of the authors' five, i.e. the target residue is a
  standard amino acid and has a 5 Å contact with a standard amino acid of another subunit. That the
  labels came out identical to their released `_T` files on all 53 MaSIF entries is the evidence
  that the reconstruction is faithful.
- **the identity of the 417 ScanNet-shared structures.** The paper says only "a subset of 417
  structures common in the benchmark dataset of ScanNet and the testing dataset of PeSTo". There is
  no list in the repository, and the notebook reads ScanNet predictions from a `scannet/` directory
  that does not exist. I recovered the 417 names from column A of the Source Data sheet
  `Fig2b-ScanNet` — so they are published, but as a by-product of the figure data, not as a dataset.
  Even then the names are only `PDBID_chain`: the bioassembly and the model tag are not published. I
  pre-registered the rule "first bioassembly, lowest model tag", which is the only sensible reading
  of `max_ba = 1` in `config_data`. It holds up: 416 of the 416 sids I built were found in assembly
  1, none needed a fallback, and for the 49 sids where assembly 1 yields several model copies, no
  sibling copy would have matched the authors better than the one the rule picks. So the rule is
  almost certainly theirs.
- **the ScanNet numbers themselves.** I did not run ScanNet. Reproducing 0.87 would mean installing
  another project under another licence, which is outside what was asked. The 0.87 in the table
  below the PeSTo column is the authors' released value, not mine.
- the environment: there is no lockfile, only `pesto.yml` and `requirements.txt` without pins. I
  pinned torch 2.2.2+cpu, numpy 1.26.4, scipy 1.11.4, scikit-learn 1.3.2, gemmi 0.6.5, python 3.11.

Two traps worth writing down for anyone who repeats this:

- `model/save/i_v4_1_2021-09-07_11-21/src/` is a 2021 snapshot of `src/` that calls `np.object` and
  dies on any numpy ≥ 1.24. The authors' notebook happens to avoid it because it imports from the
  repository root `src` before putting the save folder on `sys.path`. Put the save folder *after*
  the repository root, or the run fails on the first structure.
- the 8192-atom limit is applied to the **raw** assembly, before waters and hydrogens are removed.
  It is a filter on the file, not on the protein. This is what decides membership for the large
  complexes, and it is what dropped 1FSS_A (section 5).

## 5. The structures that disagree, and why

Two cases out of 469, both the same story, and neither is a bug in the paper or in my code.

**4DX0_A — my 0.9609 against their 0.9091.** Both model copies of chain A in today's assembly 1 give
about 0.961, so it is not a choice-of-copy problem. My prediction is not the issue either: taking
today's structure of chain A and scoring it against a label built only from the partner peptide
chain P of the *same* model copy gives 27 positive residues and an AUC of **0.909058**, against the
authors' 0.909057557582855 — the same number. So the network output is bit-identical to theirs; what
changed is the label, because the assembly changed. Today's biological assembly 1 of 4DX0 contains
two copies of A and two of P, so chain A also touches the second A copy and the second P copy, which
raises the positive count from 27 to 51 and the AUC with it. PDB entry 4DX0 was revised on
2023-09-13 and again on 2023-12-13, both after the paper appeared in April 2023. The authors ran the
pre-revision file. I checked that the authors' accuracy, TPR and TNR for this row are jointly
consistent with 27 positives, which closes the loop.

**1FSS_A — present in their 417, absent from mine.** Today's assembly 1 of 1FSS has 9482 raw atoms,
over the authors' own 8192 limit, so `build_dataset.py` discards the whole assembly and chain A never
enters the dataset. The file now holds two copies of the complex (chains A:0/B:0 and A:1/B:1, 4225
atoms per A copy). In 2023 it evidently did not: 1FSS was revised on 2024-10-23, again after
publication. This one is a side effect of the atom limit rather than of the label definition, which
is why it vanishes instead of merely shifting.

Alternatives I ruled out before settling on the PDB-revision explanation: a bug of mine (the labels
match the authors' released `_T` files exactly on all 53 MaSIF entries, and the predictions match to
three decimals on 468 of 469 structures); the choice of bioassembly (no ScanNet sid needed an
assembly beyond the first, and no alternative model copy fits the authors better on any of the 49
ambiguous sids); the atom limit as a general cause (it explains 1FSS but not 4DX0, where the limit is
not reached).

## An extra finding, not part of any claim

The 53 PeSTo prediction files in `repo/pdbs_test/*.pdb` do **not** reproduce Figure 2b. Scored
against their own `_T` labels they give a median ROC AUC of 0.9007, and the per-structure values are
far from the Source Data in both directions (3BH6_B 0.700 against the published 0.977, 2V3B_A 0.924
against 0.656). They are not the output of any of the four released checkpoints either: I ran
`i_v3_0`, `i_v3_1`, `i_v4_0` and `i_v4_1` on three of those structures and none matches. The `_T`
(ground truth) and `_M` (MaSIF-site) files in the same folder are correct and match my own labels and
`masif_pred_per_res.json` respectively. So the folder is leftover output from some earlier model
state, and nothing in the repository says so. Anyone who takes those b-factors as "the paper's
predictions" will get 0.90 and conclude the paper overstates its result. It does not; the published
checkpoint gives 0.92.

## Files

- `claims.json`, `claims.json.sha256` — pre-registration and its hash
- `scripts/pesto_rerun.py` — dataset rebuild, labels and inference
- `scripts/analyze.py` — medians, bootstrap intervals, set comparison, C3 and C4
- `scripts/compare_released_pdbs.py` — my labels and predictions against `repo/pdbs_test`
- `scripts/check_released_auc.py`, `scripts/which_variant.py` — the `pdbs_test` investigation
- `out/masif.jsonl` — 53 entries with per-residue predictions and labels
- `out/scannet_p0.jsonl`, `out/scannet_p1.jsonl`, `out/scannet.jsonl` — 416 entries
- `work/fig2b_comparison.csv`, `work/fig2b_scannet.csv` — Source Data extracted from the xlsx
- `work/scannet_sids.txt`, `work/masif_sids.txt` — the two name lists
- `downloads/` — Supplementary Information and Source Data as downloaded from the publisher
- `biounits/` — cached RCSB legacy assemblies (56 MB)

Folder total about 2.3 GB, of which 1.1 GB is the cloned repository and 1.1 GB the Python
environment. No account was created, no licence or terms were accepted, nothing was published and no
issue or pull request was opened.
