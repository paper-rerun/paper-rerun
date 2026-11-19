# Adversarial review of REPORT.md

Reviewed 2026-11-19. Everything below was run from `review/` against the folder's own
artifacts; nothing outside `review/` and this file was touched. No network.

Scripts I ran: `review/r1_readings.py` (wider menu of readings over the two recount JSONs plus
the xlsx), `review/r2_ours_readings.py` (our two 100k samples under the same menu),
`review/r3_invalid_shape.py` (shape of the invalid strings, ours against their M01). Logs next
to them.

## Blockers

**B1. §4, lines 116-117. The nestedness claim is contradicted by the table above it.**
"Our overlap with each of their machines is inside the range their machines show against each
other, on both models." For the ChEMBL 27 LSTM it is not. From `runs/out/overlap.json`,
`share_of_ours` is 0.15639 (M01), 0.15453 (M02), 0.15692 (M03), 0.15883 (M04); the six
their-pair shares run 0.15674 to 0.15961. Two of our four sit below their minimum. The
report's own table prints the two ranges as 15.45-15.88 against 15.68-15.96 and then calls one
nested in the other. This is the load-bearing sentence of the report's strongest claim and it
has to be rewritten to what the numbers say: our overlap is of the same order and slightly
below their band.

**B2. §3, lines 96-98. The range quoted for the authors' molecules is two different statistics
mashed together, and under the frozen metric our number falls outside it.**
The frozen uniqueness is distinct canonical among valid over valid. On their molecules that is
`uniqueness_distinct_canonical_over_valid` in `runs/out/definitions.json`: 0.57156, 0.56843,
0.57103, 0.57216 — range 0.5684 to 0.5722. Ours is 0.57467, above all four. The report instead
quotes "0.571 to 0.577", which takes its floor from the canonical statistic (M03, 0.57103) and
its ceiling from a different one, `distinct_valid_smiles_over_valid` in
`runs/out/authors_recount.json` (M04, 0.57659 — distinct **raw** strings among valid, not
canonical). The mixed range happens to bracket our value; the correct one does not. The same
problem feeds line 8, "our sample agrees with the molecules the authors themselves deposited,
to 0.002": on validity ours is 0.68323 against their 0.68485-0.68785, again below all four, and
on the frozen uniqueness it is above all four. The agreement is close, it is not inside.

**B3. §2, lines 75-78 and §3, line 88. "No reading" is not supported by the twelve readings
tried, and one untried reading lands on the printed 0.600.**
`scripts/05_deposit_vs_deposit.py` crosses 3 validity readings with 4 uniqueness readings. I
widened it to 6 x 10 (`review/r1_readings.log`). Two results:

- No (validity, uniqueness) pair matches all eight cells of both models. That part of the
  conclusion holds, and the deposit really does contradict its own table.
- But "distinct valid strings / distinct raw strings" — dedup the raw sample first, then count
  the valid distinct ones, which is what a script doing `drop_duplicates()` before
  `checkSmiles` would produce — gives 0.59485, 0.59336, 0.59639, 0.59681 on their four
  machines, inside 1% of print on three of them. On our own sample
  (`review/r2_ours_readings.log`) it gives **0.59413**, and the C2 band is 0.600 +/- 0.006,
  that is [0.594, 0.606]. **C2 passes under that reading.** So "nothing lands on 0.600" (line
  88) and "the printed 0.600 sits between two of the readings and on neither" (lines 97-98) are
  false, and the verdict of 1 of 4 is definition-dependent on exactly the claim the report says
  is definition-independent. The GRU still fails under that reading (0.91434 against 0.996), so
  the deposit-versus-table contradiction survives; the uniqueness verdict for the LSTM does not.

**B4. §5, line 123 and `claims.json` ("why_this_section_exists"). "No code in DrugEx computes a
uniqueness ratio" is false.**
`repo/DrugEx/drugex/training/explorers/interfaces.py:122-124`:
`unique = accurate.drop_duplicates(subset='SMILES')` then `dct['unique_ratio'] = len(unique) /
ntot`, documented in the docstring above it as "unique_ratio (float): ratio of valid and unique
molecules". That is a uniqueness ratio in the release, with a denominator of everything sampled
— and it is not the frozen definition. It gives 0.395 for the LSTM and 0.911 for the GRU, so it
does not rescue the table either, but the whole justification for recovering the definition from
the deposit, and for running scripts before the freeze, rests on a claim that does not hold when
you grep the repository. Rewrite it as "no code computes the ratio Table S4 prints" and show the
release's own ratio next to the frozen one.

**B5. §1 and §2 tables. Machines and statistics are mixed inside both deposit tables.**

- Line 46, ChEMBL 27, "the authors' deposited molecules (M01-M04)": printed as 0.68485, 0.68633,
  0.68744, 0.68785. Their four flag values are 0.68577, 0.68485, 0.68744, 0.68633 and their four
  RDKit-parseable values are 0.68638, 0.68547, 0.68785, 0.68683. The printed list drops M01's
  0.68577 and imports M03's parseable 0.68785. Line 47 is the same kind of mix: 0.91401 and
  0.91624 are flag values, 0.91512 and 0.91573 are parseable ones.
- Lines 68-73 are headed "spreadsheet, M01 | molecules, M01", but the ChEMBL 27 molecule column
  is M02 throughout: 0.68485, 0.66105 and 0.57274 are M02's; M01's are 0.68577, 0.66418 and
  0.57613. The ChEMBL 31 column really is M01. A table whose point is "same machine, same model,
  same n" cannot change machine between its rows.
- In the same line 71, "0.57274 canonical over valid" is not canonical. It is
  `distinct_valid_smiles_over_valid`, distinct raw strings among valid. M02's canonical value is
  0.56843.

## Should-fix

**S1. Line 140, "`torch.manual_seed` appears nowhere in the repository"** — it appears three
times, in `tutorial/advanced/rocs/prepare_models.py:229`, `run_cdpkit_rocs.py:212` and
`run_openeye_rocs.py:234`. Nowhere in the sampling path, which is the point being made; say
that instead. `claims.json` carries the same sentence.

**S2. Line 11 and lines 168-169, the cost lines, are both wrong.** "Folder 110 MB" — `du -sm`
gives 1,527 MB: `env/` 1,195, `repo/` 145, `downloads/` 112, `data/` 74. And "The weights and
the 496 MB molecule file are not in this folder": the weights are in `data/chembl27` and
`data/chembl31` (74 MB) and the molecule file is `downloads/sampled_molecules.tsv.xz` (79 MB).
Both are in the folder.

**S3. Line 143, "a CPU is only three times slower".** LSTM: 10.814 ms against 2.273-3.052 on
their six GPUs, that is 3.5x to 4.8x. GRU, which the sentence leaves out: 10.925 against
1.693-2.086, that is 5.2x to 6.5x. Lines 11 and 143 also quote 10.8 ms as if it covered both
runs; the GRU was 10.925.

**S4. Line 10, "Peak working set of a sampling process, 386 MB".** 386.3 MB is `pilot2_c27`.
The two scored runs report 390.6 and 380.0 (`full_c27.json`, `full_c31.json`).

**S5. Line 141, the truncation scan is thinner than the sentence it supports.**
`runs/out/truncation_c27.json` is n=1800 per max_len, which the report does not state. The
binomial standard error there is about 0.011, so 0.671 / 0.695 / 0.667 / 0.698 are one cloud,
not four measurements; the scan can rule out a 30-point effect of max_len, not a few-point one.
`scripts/04_truncation.py:46` also scores validity as parseable alone, not the frozen rule, and
the scan was run on the LSTM only. And "Truncation is not what makes the strings invalid"
overshoots the other way: 59.7% of our invalid LSTM strings have more `)` than `(` (18,898 of
31,677, `review/r3_invalid_shape.log`), which is what a cut sequence looks like. What was shown
is that `max_len` is not the knob, not that the strings are not cut.

**S6. Line 59, the example string.** `C=CCOCc1ccccc1)OCc1ccccc1` does not occur in any of our
five sampled outputs (0 hits in the two full runs and the three pilots). It occurs 3 times in
the authors' M01 rows of the deposit. The example is real, and it is theirs; say which file it
came from, since the paragraph sits in a section about our sample.

**S7. The frozen uniqueness reading was fitted to a published value, and the report does not say
so.** `claims.json` is honest about it in its own words — "this is the only reading that returns
a published value from the authors' own deposited molecules (0.99651 against the printed 0.996
for the ChEMBL 31 GRU)" — but §5 lines 126-128 call it "recovered", and lines 35-37 defend only
the band against the charge of fitting. C4 is the one claim that passes, and it passes on a
definition chosen because it matched C4's published value. That is not fraud, it is the only way
to pin an unpublished metric, but the caveat belongs where the verdict is stated, not only in
the preregistration.

**S8. The two LSTM claims are not independent, and the report scores them as two.** The frozen
uniqueness denominator is our own valid count, so a lower validity mechanically raises
uniqueness-over-valid: ours is 68,323 valid against their 68,485-68,785, and our uniqueness
ratio sits above all four of theirs. One sentence would cover it.

**S9. Two assertions have no artifact behind them.** Line 138 quotes a runtime error
(`RuntimeError: Invalid device string: 'cuda:-1'`) that no log in `runs/logs/` records, and the
closing date of PR #20 cannot be checked from this folder at all. I verified the first myself
(see "What held up"); the second stays unsourced and should be marked as read from GitHub on a
date rather than stated flat.

## Minor

- Line 140, "a spread of 0.001": 0.599 to 0.601 is a spread of 0.002. `claims.json` says
  "+/-0.001", which is right.
- Lines 52-53, "0.685 ... 0.688": the four-machine means are 0.6861 (their flag) and 0.6866
  (parseable), so 0.686 and 0.687. Both roundings widen the gap to our 0.683.
- Line 117, "the distinct counts match to a few tenths of a percent": true for the GRU (0.19%),
  not for the LSTM, where ours is 0.77% above their M02 (39,262 against 38,963).
- Line 113, "15.68%": the smallest their-pair share is 0.156742, so 15.67%.
- Line 57, "which is exactly what we do": `SmilesChecker.checkSmiles`
  (`drugex/training/scorers/smiles.py:31`) counts `.` in the **raw** string; our scripts test it
  in the canonical SMILES. Immaterial here because no sequence of either model produced a
  fragment, but it is not "exactly".
- `scripts/02_definitions.py:56-57`: `canon` and `canon_valid` get the same value on every
  parseable row, so the numerator of `uniqueness_distinct_canonical_over_valid` ignores the
  single-fragment rule that its own denominator applies. Inert in this data
  (`validity_single_fragment` equals `validity_parseable` in all eight cells) and dead code that
  would quietly misreport on a model that emits fragments.
- `scripts/07_overlap.py:62` filters their side by their `Valid` flag while our side is
  unfiltered, so the two sides of the comparison are not built by the same rule. I measured it:
  flag-filtered distinct canonical for ChEMBL 27 M01 is 39,230 against 39,231 unfiltered, one
  molecule. Immaterial, but it should be the same rule on both sides, or stated.
- Line 83, "18 to 29 rows per machine": that is the LSTM range. The GRU is 13 to 16
  (`overlap.json`).
- Line 126 says two scripts ran before the freeze. Three did: `00_probe_tsv.py`
  (`tsv_probe.log`, 23:59) and `read_xlsx.py` (`xlsx_dump.txt`, 23:50) also predate
  `claims.json` (00:08 local, 03:08Z). Neither measures anything of ours; the count should still
  be right.

## What held up

Tested and found correct, so the next reader knows which parts were attacked:

- **The preregistration hash.** `sha256sum claims.json` gives
  `96d22c18194e8e1b5de69bb4a132290fe85524628e9b65e42dc83aa9270c3ee5`, matching `claims.sha256`
  and the report's line 7. `scripts/06_score.py:14-17` recomputes it and exits on a mismatch.
- **The freeze ordering.** `claims.json` is 00:08 local (03:08:10Z, matching
  `claims.frozen_at.txt`); every sample of ours is later — pilots 00:09 and 00:10, truncation
  00:15, the two scored runs 00:29 and 00:50. Nothing of ours was measured before the freeze.
- **Every published value quoted.** 0.999 / 0.600 / 1.000 / 0.996, the per-machine 0.599-0.601
  over six GPUs, the "0.988 to 0.996" for the other RNNs and the 2.3-3.1 ms GPU range all match
  `downloads/sampling_time.xlsx` as dumped in `runs/logs/xlsx_dump.txt`.
- **The band arithmetic.** All four bands are 1% of the published value and all four deltas
  recompute from `full_c27.json` and `full_c31.json`; the report's table matches `verdict.json`
  to the digit.
- **The band's relative-versus-absolute ambiguity does not matter.** The legend says only "lower
  than 1.00%". Read as one absolute percentage point instead of 1% relative, C1, C2 and C3 still
  fail and C4 still passes. The verdict does not turn on the reading.
- **The 1% test inside `05_deposit_vs_deposit.py`** is written correctly, relative to each
  machine's own published value, and the empty `readings_that_match_both_models` survives a menu
  five times larger than the one it tries (`review/r1_readings.log`). The contradiction between
  the two deposited files is real.
- **The sampling loop really is their `generate()` with the filters off.** `generate()` in
  `sequence_rnn.py:297` is `while not len(df_all) >= num_samples: new_smiles =
  self.sample(batch_size)` plus an optional `filterNewMolecules`; `scripts/03_sample.py:81-86`
  is the same loop without the filter, truncated to exactly 100,000. Validity does follow
  `SmilesChecker.checkSmiles` (RDKit parse plus single fragment), modulo the raw-versus-canonical
  nit above.
- **The branch claim.** `git show origin/master:...sequence_rnn.py` and tag `v3.4.8` both set
  `torch.device(f'cuda:{gpus[0]}')` with no `-1` guard; `origin/dev` has it at line 46. And
  `torch.device('cuda:-1')` raises exactly `RuntimeError: Invalid device string: 'cuda:-1'` in
  this venv. The claim is right even though no log in the folder shows it.
- **The attribution has better evidence than the report uses.** The invalid strings of our LSTM
  sample and of their M01 agree in shape, not only in count: the five commonest 11-character
  endings are 960/956, 662/630, 507/493, 458/463, 346/300 (ours/theirs), out of 31,677 and
  31,362 invalid strings, and the share of invalids with unbalanced parentheses is 59.7% against
  59.9% (`review/r3_invalid_shape.log`). That is a sharper fingerprint than an overlap
  percentage, which is dominated by the head of a concentrated distribution and would move
  little under a mild difference in the decode path. If B1 is fixed by softening the overlap
  claim, this is what should replace it.
