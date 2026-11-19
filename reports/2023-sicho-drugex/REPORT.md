# DrugEx — sampling statistics, Table S4

- Paper: Sicho, M.; Luukkonen, S.; van den Maagdenberg, H. W.; Schoenmaker, L.; Bequignon, O. J. M.; van Westen, G. J. P. *DrugEx: Deep Learning Models and Tools for Exploration of Drug-like Chemical Space.* J. Chem. Inf. Model. 2023, 63 (12), 3629-3636. DOI 10.1021/acs.jcim.3c00434. The numbers are in the Supporting Information, section S4, Table S4; the article body carries no benchmark number, because it is a software paper. A supplementary number counts as a target here as long as the report says where it comes from.
- Data: none to download. Each RNN samples from scratch, so there is no input test set. The published values are also deposited as a spreadsheet at 10.5281/zenodo.7928362, one row per model per machine over six GPUs, together with 2,240,000 of the molecules those rows summarise.
- Code: `CDDLeiden/DrugEx` at `dev`, commit `76c1c3919566d1e1c57ff5a8401610c3c314b56c`, MIT, unmodified. Not `master`: there, `SequenceRNN` sets `torch.device('cuda:-1')` with no guard and cannot start on a machine without a GPU.
- Weights: the two Zenodo records, MIT, anonymous. ChEMBL 27 LSTM RNN `10.5281/zenodo.7096837` (md5 `ed6ebd972e530a108e16ed4646b2a38a`), ChEMBL 31 GRU RNN `10.5281/zenodo.7550739`.
- Target: the four values frozen in `claims.json`, SHA-256 `96d22c18194e8e1b5de69bb4a132290fe85524628e9b65e42dc83aa9270c3ee5`, frozen at 2026-11-19T03:08:10Z, before anything of ours was sampled.
- Verdict: **Partially reproduced** — 1 of 4 inside the frozen band. Three of the four printed values are reproducible and the fourth is not, but only one of the three is reproducible as the quantity the table says it is: the validity column of the RNN rows is the share of sampled sequences that came out non-empty, not the share that parse, and under that rule our two runs land on 0.999 and 1.000 exactly. The ChEMBL 27 LSTM uniqueness of 0.600 is unaccounted for under every reading we and an independent blind run could construct.
- Date: 2026-11-19
- Hardware: Ryzen 9 3900X, 64 GB, CPU only, 4 threads under `nice -n 19`. The GPU was not touched. Peak working set of the two scored runs, 390.6 MB and 380.0 MB.
- Wall clock: 36 min of sampling (1081 s at 10.814 ms per molecule for the LSTM, 1093 s at 10.925 for the GRU), plus about 20 min of passes over the authors' 496 MB molecule file. Folder 1,527 MB: `env/` 1,195, `repo/` 145, `downloads/` 112 (the two deposited files), `data/` 74 (the two checkpoints).

## What this run is

Table S4 gives, for each pretrained DrugEx model, the ratio of sampled representations that
form a valid molecule and the ratio of molecules that are unique, at 100,000 molecules and
batch size 600. We took the two models the table names first — the ChEMBL 27 LSTM RNN and the
ChEMBL 31 GRU RNN — sampled 100,000 sequences from each on CPU with the authors' own code, and
computed the two ratios.

The six transformer rows are out of scope and were out before the run: `generate.py` defaults
to a BRICS split of Papyrus 05.5 that was never published, so their accuracy cannot be scored
against the authors' input. The relative sampling time column is wall clock on their GPUs and
is not comparable to ours.

Two checks ran on top of this one. `REVIEW.md` is an adversarial review of the first draft of
this report: it raised five blockers and all five were real. A blind recount ran in a separate
folder with no access to any of ours, pre-registered its own definitions and sampled its own
100,000 per model; it is the one that found what the validity column actually counts. Both are
summarised near the end, and every number below is the corrected one.

## Verdict against the frozen rule

| claim | model | metric | ours | published | delta | band | |
|---|---|---|---|---|---|---|---|
| C1 | ChEMBL 27 LSTM | validity | 0.6832 | 0.9990 | −0.3158 | 0.00999 | **fails** |
| C2 | ChEMBL 27 LSTM | uniqueness | 0.5747 | 0.6000 | −0.0253 | 0.00600 | **fails** |
| C3 | ChEMBL 31 GRU | validity | 0.9146 | 1.0000 | −0.0854 | 0.01000 | **fails** |
| C4 | ChEMBL 31 GRU | uniqueness | 0.9962 | 0.9960 | +0.0002 | 0.00996 | ok |

The band is 1% relative, and it is the authors' own: the Table S4 legend states that the
deviation across independent sampling runs was below 1.00% for everything except the relative
sampling time. We did not pick it after seeing our numbers and we did not resize it after.
Read instead as one absolute percentage point, which the legend also allows, nothing changes.

C1 and C3 fail because the frozen definition of validity is the release's own — RDKit parses it
and it is a single fragment — and that is not what the column holds. Under the rule the column
does follow, section 1, our LSTM reads 0.99920 against a printed 0.999 and our GRU 1.00000
against 1.000. We are leaving the verdict at 1 of 4 because the frozen rule is the rule, and
because a definition recovered after the fact is worth less than one fixed before; but the
honest summary of the run is that three of the four numbers come back and the paper's
description of two of them is wrong.

Two caveats that belong next to this table rather than buried in the pre-registration.

**The uniqueness definition was fitted to C4.** No published script computes the ratio Table S4
prints, so the definition had to be recovered from the authors' deposited molecules, and the
reading we froze — distinct canonical molecules among the valid ones, over the valid ones — was
chosen because it is the one that returns a published value (0.99639 to 0.99651 on their four
machines against the printed 0.996). C4 is the claim that passes, and it passes on a definition
picked because it matched C4. The blind run froze the same reading independently, for the same
reason, which is some comfort and not independence.

**C1 and C2 are not independent.** The frozen uniqueness denominator is our own valid count, so
a lower validity mechanically raises uniqueness-over-valid. Ours is 68,323 valid against their
68,485 to 68,744, and our uniqueness ratio sits just above all four of theirs; part of that
0.003 is the smaller denominator, not a different repetition rate.

## 1. The validity column is not validity

The blind recount found the rule, and it holds on every RNN row of the authors' own deposit:
the printed validity is the share of sampled sequences that decoded to a non-empty string,
parseable or not.

| model | printed | non-empty share, their 4 machines | parseable share, their 4 machines |
|---|---|---|---|
| ChEMBL 27 LSTM | 0.999 | 0.99910 to 0.99932 | 0.68485 to 0.68744 |
| ChEMBL 31 GRU | 1.000 | 1.00000 | 0.91401 to 0.91624 |
| ChEMBL 31 LSTM | 1.000 | 1.00000 | 0.96071 to 0.96286 |
| Papyrus 05.5 GRU | 1.000 | 1.00000 | 0.91449 to 0.91674 |
| Papyrus 05.5 LSTM | 1.000 | 1.00000 | 0.95656 to 0.95717 |

Twenty of twenty RNN machine-rows round to the printed value under the non-empty rule
(`scripts/08_nonempty.py`, `runs/out/nonempty.json`). Our own two runs do the same: 80 empty
strings in 100,000 on the LSTM gives 0.99920, which rounds to the printed 0.999, and zero empty
strings on the GRU gives 1.00000 against 1.000.

The discriminating row is the ChEMBL 27 LSTM, because it is the only RNN that does not print
1.000. Its 0.999 is not a rounded 1.000 and it is not a rounded 0.685 either; it is the exact
shortfall left by about ninety empty strings. The four rows that print 1.000 are consistent with
the rule and prove nothing on their own.

So the column reproduces and its legend does not describe it. The legend offers "the ratio of
molecular representations that make valid molecular structures" (Table S4, Supporting
Information), and for the ChEMBL 31 GRU that ratio is 0.914 in the authors' own molecules while
the table prints 1.000. A reader comparing DrugEx against another generator on this column is
comparing a number that is near 1.000 for any model that emits a string at all.

One nit, immaterial here: their `SmilesChecker` counts the `.` of a multi-fragment SMILES in the
raw string and we count it in the canonical one. No sequence of either model produced a fragment,
so the two agree on every row.

The invalid strings are not borderline chemistry, they are broken syntax. From their own M01
rows: `C=CCOCc1ccccc1)OCc1ccccc1`, a closing bracket that never opened.

## 2. Uniqueness: one model reproduces, one value is unaccounted for

The deposited `Unique` flag has a rule too, and it is the raw one: distinct sampled strings over
all 100,000 rows, invalid strings included. It reproduces the flag exactly on all eight machines
of the two models (`uniqueness_their_flag` equals `uniqueness_distinct_raw_over_n` to five
decimals in `runs/out/definitions.json`). But the flag's rule is not the printed column's rule:
it gives 0.99678 to 0.99693 for the GRU, which rounds to 0.997, where the table prints 0.996.
The reading that lands on 0.996 is the frozen one, distinct canonical molecules among the valid
ones: 0.99639 to 0.99651 on their machines, 0.99621 on ours. The blind run read the GRU's 0.996
off the raw rule instead; that is a rounding slip on its side, and it does not touch its own
verdict, which used the same frozen reading we did.

The ChEMBL 27 LSTM's 0.600 lands under no rule at all:

| reading | LSTM, ours | LSTM, their four machines | printed |
|---|---|---|---|
| distinct canonical among valid, over valid (frozen) | 0.57467 | 0.56843 to 0.57216 | 0.600 |
| distinct valid strings over distinct raw strings | **0.59413** | 0.59336 to 0.59681 | 0.600 |
| distinct raw strings over n (their `Unique` flag) | 0.66487 | 0.66105 to 0.66418 | 0.600 |
| distinct canonical over n (the release's own `unique_ratio`) | 0.39263 | 0.38964 to 0.39298 | 0.600 |

The second row — deduplicate the raw sample first, then count the valid distinct ones — puts us
at 0.59413, inside C2's band of [0.594, 0.606] by 0.00013. So C2 passes under that reading, and
the review found it, not us. It does not rescue the table, because the same reading breaks the
GRU: 0.91434 against a printed 0.996. That is the shape of the whole result on this column. Each
reading can carry one of the two uniqueness values and never both, so the count stays at 1 of 4
whichever reading you adopt — a different 1 each time.

The blind run reached the same dead end from its own sample and its own menu, and named the same
four candidates: 0.662, 0.572, 0.576, 0.392. Two runs that never saw each other's work both fail
to produce 0.600, and the published value is 0.599 to 0.601 across six machines, so it is not
noise either.

What survives any reading is the size of the effect the row claims. Every other RNN in Table S4
prints 0.988 to 0.996 and this model prints 0.600, and under all four readings above the ChEMBL
27 LSTM really does repeat itself heavily. The unusual behaviour is real; the printed figure is
not one the deposit supports.

## 3. Our sample and theirs are the same distribution

The ratios agreeing could still hide a different model, so we compared the molecules themselves.

Shared molecules first (`scripts/07_overlap.py`), with the authors' machine-to-machine overlap as
the yardstick, since each of their machines is an independent unseeded draw:

| model | our distinct molecules | theirs | ours ∩ each of theirs | theirs ∩ theirs |
|---|---|---|---|---|
| ChEMBL 27 LSTM | 39,262 | 38,963 to 39,297 | 15.45% to 15.88% | 15.67% to 15.96% |
| ChEMBL 31 GRU | 91,115 | 91,064 to 91,291 | 0.538% to 0.562% | 0.532% to 0.582% |

On the GRU our overlap sits inside their band and our distinct count is 0.19% off theirs. On the
LSTM two of our four overlaps fall just below their lowest pair, 15.45% and 15.64% against
15.67%, and our distinct count is 0.77% above their lowest. Same order, slightly outside: the
first draft called this nested and it is not.

The sharper fingerprint is in the invalid strings, which an overlap percentage cannot see because
overlap is dominated by the concentrated head of the distribution. Our LSTM produced 31,677
invalid strings and their M01 produced 31,362, and the two sets break the same way
(`review/r3_invalid_shape.log`): the five commonest endings appear 960, 662, 507, 458 and 346
times in ours against 956, 630, 493, 463 and 300 in theirs, and the share of invalid strings with
more closing than opening parentheses is 59.7% against 59.9%. A different decode path, a different
vocabulary or different weights would not fail in the same proportions in the same way.

The blind run, sampling independently with its own seed and its own loop, landed on 0.68558 and
0.91398 against our 0.68323 and 0.91462 and the authors' 0.68485 to 0.68744 and 0.91401 to
0.91624. Four independent draws of the same two distributions.

## 4. What the spreadsheet and the molecules do and do not share

The spreadsheet and the molecule file are two files of the same Zenodo record. For the same
machine, model, sample size and batch they agree on validity once the column's real rule is
known, and they disagree on the LSTM uniqueness under every rule. M01 on both sides:

| | spreadsheet | molecules |
|---|---|---|
| ChEMBL 27 LSTM validity | 0.999 | 0.99910 non-empty, 0.68577 parseable |
| ChEMBL 27 LSTM uniqueness | 0.599 | 0.66418 distinct raw over n, 0.57156 distinct canonical over valid |
| ChEMBL 31 GRU validity | 1.000 | 1.00000 non-empty, 0.91401 parseable |
| ChEMBL 31 GRU uniqueness | 0.996 | 0.99689 distinct raw over n, 0.99645 distinct canonical over valid |

`scripts/05_deposit_vs_deposit.py` crosses every reading of the two ratios against every machine
of both models and asks which pair lands inside 1% of print on all of them.
`readings_that_match_both_models` comes back empty, and the review widened the menu from 12 pairs
to 60 without changing that (`review/r1_readings.log`). That empty result is now narrower than it
looked: the menu was built out of readings that require a molecule, so it could not contain the
non-empty rule, and section 1 is the pair it was missing. On uniqueness the exhaustion stands.

Two smaller facts from the same comparison. The spreadsheet covers six machines, M01 to M06; the
molecule file covers four, M01 to M04, so the two files do not describe the same set of runs. And
a few rows per machine are flagged valid by the authors and rejected by RDKit 2026.9.2 — 18 to 29
on the LSTM, 13 to 16 on the GRU, so 0.03% — which is version drift and nothing more.

## 5. The metric the table prints is not in the release

The release does compute a uniqueness ratio, in `drugex/training/explorers/interfaces.py:122-124`:
`unique = accurate.drop_duplicates(subset='SMILES')` and then `unique_ratio = len(unique) / ntot`,
documented as "ratio of valid and unique molecules". Its denominator is everything sampled, so it
is the fourth row of the table in section 2: 0.393 for the LSTM and 0.911 for the GRU against
printed 0.600 and 0.996. The release's own definition does not produce the release's own table
either, and nothing in the release counts non-empty strings, which is what the validity column
holds.

`SequenceRNN.validateNet` computes `valid_ratio` and nothing else, the `Uniqueness` scorer in
`properties.py` is a per-molecule duplication score used in reinforcement learning, and no
published code emits the pair of ratios the table prints. That is why the definitions had to be
recovered from the deposited molecules before anything could be measured, which is what
`scripts/01` and `scripts/02` do and why they ran before `claims.json` was frozen. Two more
scripts predate the freeze and measure nothing of ours: `00_probe_tsv.py`, which counts malformed
lines in the deposit, and `read_xlsx.py`, which dumps the spreadsheet. `scripts/08_nonempty.py`
was written after the blind run reported and measures the deposit, not us.

There is also a structural reason the table cannot come from the obvious entry point.
`generate()` defaults to `drop_invalid=True` and `drop_duplicates=True` and loops until it holds
`num_samples` molecules, so its output is all valid and all unique by construction and neither
ratio can be computed from it. Table S4 reports ratios, so it was made from a raw sample, with a
script we cannot see.

## 6. Everything the release let us check

- The clean path is `dev`. On `master` and at tag v3.4.8, `sequence_rnn.py` sets `self.device = torch.device(f'cuda:{gpus[0]}')` with no guard, so `gpus = (-1,)` raises `RuntimeError: Invalid device string: 'cuda:-1'` and the released version cannot sample on a machine without a GPU. The guard is in `dev` at line 46, which is what we ran. PR #20 proposed that guard for `master`; read on GitHub on 2026-11-08, it is closed without merge, dated 2026-07-29. The blind run hit the same wall from the released package and worked around it with a four-line monkeypatch, which is independent confirmation that the bug is in the path a reader takes.
- `python -m drugex.generate` does not start from a plain install either. `generate.py:10` imports `drugex.train`, which imports `qsprpred` at module level (`train.py:7-8`), and `qsprpred` is an optional extra in `pyproject.toml:51`, so it is absent unless the reader knew to ask for it. The documented command for sampling depends on the QSAR stack it does not need.
- `generate.py:175` warns that dropping duplicates is being ignored because invalids are kept, and `generate.py:181` then forwards `drop_duplicates=not args.keep_duplicates` anyway. The message and the argument disagree; the blind run found this one.
- Both checkpoints load under `torch.load(..., weights_only=True)`, which the current code uses. A 2022 pickle surviving that is worth saying, because it is the kind of thing that breaks silently.
- No seed in the sampling path. `generate.py` has no `--seed`, and `torch.manual_seed` appears three times in the repository, all three in `tutorial/advanced/rocs/`, none of them where molecules are sampled. So no sample can be reproduced exactly. The authors handled that the right way, by publishing the dispersion instead, and their numbers are far more stable than their own claim: the ChEMBL 27 LSTM uniqueness reads 0.599, 0.600, 0.601 across six GPUs, a spread of 0.002 against the 1.00% the legend allows itself.
- `max_len` is not the knob behind the invalid strings. Sampling the LSTM at `max_len` 100, 120, 140 and 200 gives validity 0.671, 0.695, 0.667, 0.698 (`scripts/04_truncation.py`, n = 1,800 per setting, so a binomial standard error of about 0.011 — one cloud, not four measurements). What that rules out is a large effect of the window, not a small one. The blind run measured the same thing more sharply: 51 of its 100,000 sequences used every token available, 43 of them among the 31,442 invalid ones. The invalid strings are not truncation artefacts; the v2 ChEMBL 27 model simply emits about 31% unparseable SMILES.
- The ChEMBL 27 checkpoint is a DrugEx **v2** model, as its own README says, run under the v3 code that ships with this paper, because that is the only code the paper releases. That is a fair suspicion for its low validity, and it is not the answer: the ChEMBL 31 GRU is a native v3.3.3 model and still gives 0.915 where its row prints 1.000.
- CPU is a workable platform for this. 10.814 ms per molecule on the LSTM against 2.273 to 3.052 on the deposit's six GPUs (3.5x to 4.8x), and 10.925 against 1.693 to 2.086 on the GRU (5.2x to 6.5x). The RNN is latency-bound on a sequential step, which is why the gap is single-digit.

## 7. What we did not do, and two inert defects of our own

- Three of the five RNNs in Table S4 were not run: Papyrus 05.5 GRU, ChEMBL 31 LSTM and Papyrus
  05.5 LSTM. Their weights are released and each would cost about 18 minutes. They are not in
  this verdict, though their deposited molecules are, in section 1.
- The transformers were out before the run, for the missing split. Their validity column prints
  0.944 to 0.964, below 1.000, so the two halves of the column do not look computed the same way.
  We did not check them and do not claim anything about them.
- One number of ours moved after the pilot: uniqueness is a function of the sample size, and the
  1,200-molecule pilot reads 0.879 where the 100,000 run reads 0.575. Nothing was decided on the
  pilot.
- `scripts/02_definitions.py` fills `canon` and `canon_valid` with the same value on every
  parseable row, so the numerator of `uniqueness_distinct_canonical_over_valid` skips the
  single-fragment rule its own denominator applies. Inert in this data, since no sequence of
  either model produced a fragment, and left in place so the logs still match the scripts.
- `scripts/07_overlap.py` filters the authors' side by their `Valid` flag and ours by RDKit, so
  the two sides of the overlap are built by slightly different rules. Measured during the review:
  one molecule of difference on ChEMBL 27 M01, 39,230 against 39,231.
- The Supporting Information PDF itself was never read from the publisher. Both runs took the
  Table S4 values and the legend from the authors' own deposit for that table. The blind run tried
  the publisher and EuropePMC and got an interstitial and a figures-only endpoint.

## What the two checks caught

The adversarial review raised five blockers, all verified against the artifacts before being
accepted:

1. **The nestedness claim was false.** The draft said our overlap sits inside the authors'
   machine-to-machine range on both models; on the LSTM two of our four values fall below their
   minimum. Section 3 now says what the numbers say, and leads with the invalid-string
   fingerprint instead, which the review also supplied.
2. **A range in the draft mixed two statistics.** "0.571 to 0.577" for the authors' LSTM
   uniqueness took its floor from the canonical reading and its ceiling from the raw one, and the
   mixed range happened to bracket our value while the correct one, 0.5684 to 0.5722, does not.
3. **"No reading lands on 0.600" was wrong**, and the reading that does was not in our menu of
   twelve. C2 passes under it, by 0.00013.
4. **"No code in DrugEx computes a uniqueness ratio" was wrong.** The release has `unique_ratio`
   in `explorers/interfaces.py`, and that was the whole justification for recovering the
   definition from the deposit. The justification is narrower than the draft claimed: the release
   computes a uniqueness ratio, just not the one the table prints. `claims.json` carries the wrong
   sentence too and keeps it: it is frozen and its hash has to stay checkable, so the correction
   lives here and not there.
5. **Both deposit tables mixed machines and statistics**, including a column headed M01 that
   carried M02's numbers on one model. Both tables were rebuilt from `runs/out/definitions.json`
   with one statistic per column.

Nine smaller corrections came from the same review and are in the text above: the folder size
(110 MB in the draft, 1,527 MB), the peak memory (the pilot's instead of the runs'), the CPU
slowdown (3x in the draft, 3.5x to 6.5x), `torch.manual_seed` (claimed absent, three times in
tutorials), the dispersion spread (0.001 for 0.002), the truncation scan's sample size and what it
can rule out, the provenance of the example invalid string, and the two caveats now standing next
to the verdict table.

The blind recount landed on the same verdict, 1 of 4, with the same claim passing, from its own
pre-registration (`2023-sicho-drugex-cego/claims.json`, SHA-256
`465e1bd17fdb2b55fb88a31c661ee3893632ea27522b29548d1df2e9453af9da`) and its own sample. What it
added:

- **The validity column counts non-empty strings.** This is the finding of the whole cycle and it
  is theirs. We had the deposit's parseable share and the printed value and concluded only that
  the two cannot be reconciled; they asked what else the column could be counting. Verified here
  on all 20 RNN machine-rows and on our own two samples.
- **The truncation question answered properly**, by counting sequences that used every token
  rather than by scanning `max_len` at small n.
- **Two usability defects**, the `qsprpred` import and the `keep_invalid` warning.

One thing of theirs did not hold: reading the printed GRU uniqueness of 0.996 off the raw rule,
which gives 0.9969 and rounds to 0.997. Section 2 has it.

The review also attacked and failed to break: the pre-registration hash and the freeze ordering,
every published value quoted, all four bands and deltas, the 1% test inside script 05, the claim
that our sampling loop is the authors' `generate()` with the filters off, and the `master` CPU bug.

## Reproducing

```
scripts/01_recount_authors.py downloads/sampled_molecules.tsv.xz ...   # their table from their molecules
scripts/02_definitions.py     ...   # the same, under every reading, with RDKit parsing
scripts/05_deposit_vs_deposit.py ...   # which reading survives: none
scripts/08_nonempty.py        ...   # the non-empty share, per machine, against print
scripts/run_full.sh                  # our two samples, 100000 each, batch 600
scripts/06_score.py           ...   # checks the claims hash, then scores
scripts/07_overlap.py         ...   # our molecules against theirs
```

`scripts/03_sample.py` is the sampler the shell script calls and `scripts/04_truncation.py` is
the max_len scan. `review/` holds the three scripts the adversarial review ran. `data/README.txt`
gives the download lines and the checksums for the two checkpoints and the two deposited files,
all of which are in this folder and none of which belong in a public repository.

## Notes for the authors

Four things, in the order they matter to a reader of Table S4.

1. **The validity column of the RNN rows does not report validity.** It reports the share of
   sampled sequences that came out non-empty. This reproduces on all twenty RNN machine-rows of
   your own deposit and on two fresh samples of ours. The parseable share of the same molecules is
   0.685 for the ChEMBL 27 LSTM, 0.914 for the ChEMBL 31 GRU, 0.961 for the ChEMBL 31 LSTM, 0.914
   and 0.957 for the two Papyrus models. The legend describes the second quantity and the table
   prints the first. The transformer rows print 0.944 to 0.964, so the column may not be computed
   the same way down its length; we did not check those.
2. **The ChEMBL 27 LSTM uniqueness of 0.600 is unaccounted for.** Recomputed from your own
   deposited molecules it is 0.664 under the rule your `Unique` flag follows, 0.572 under distinct
   canonical over valid, 0.594 under distinct valid over distinct raw, 0.392 under the
   `unique_ratio` the release itself computes. Your six machines print 0.599 to 0.601, so it is a
   stable number, not a slip in one run. We would like to know which script produced it.
3. **No released code computes either column.** `generate()` drops invalid and duplicate
   molecules and resamples to fill the quota, so neither ratio is computable from its output;
   `unique_ratio` in `explorers/interfaces.py` uses a different denominator; nothing counts
   non-empty strings. Publishing the Table S4 script would settle points 1 and 2 at once.
4. **Two things that stop a reader at the first command.** `python -m drugex.generate` imports
   `drugex.train`, which imports `qsprpred` at module level, and `qsprpred` is an optional extra,
   so the documented sampling command fails on a default install. And on `master` and v3.4.8,
   `SequenceRNN` builds `torch.device('cuda:-1')` with no guard, so sampling cannot start without
   a GPU, which the README says it should; the guard exists on `dev` and PR #20 for `master` is
   closed unmerged.

For the record: the GRU uniqueness reproduces, 0.9962 against 0.996, under distinct canonical
molecules among the valid ones over the valid ones. That reading is also the one that makes your
GRU row come out at 0.996 rather than 0.997, so we believe it is yours.
