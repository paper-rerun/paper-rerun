# Adversarial review of the CodonTransformer reproduction

- Reviewed: `REPORT.md`, `claims.json`, `claims.frozen_at.txt`, all 13 files in `runs/logs/`, the 6 files in `runs/out/`, the 10 scripts in `scripts/`, the authors' extracted R code, the Fig. 4 workbook and the paper full text. Against `E:\Ciencia\PIPELINE.md`, stage 7.
- Date: 2026-11-10. Nothing was published, pushed or mailed. No model was re-run, nothing was downloaded, nothing was installed. REPORT.md was not edited.
- Independent checks I ran for this review: recomputation from `runs/out/*.csv`, re-reading of the `%MinMax` and `DTW` sheets with openpyxl, a symmetric2 DTW written from the step pattern, and a quantisation-direction test. Commands are in the scratchpad; every number below is reproducible from files in this folder.

Short version: the arithmetic in this report is sound and I could not break a single number in it. The verdict on top of it is not the verdict the frozen rule gives, and the two findings the report flagged for attack both need rewriting — one because its evidence is the wrong evidence, the other because its cause is wrong and its conclusion is too pessimistic.

---

## F1. The headline verdict is not the one the frozen rule gives. Severity: high

`claims.json` `verdict_rule`: *Not reproduced* = "Any claim outside its band at L1 or L2." The L2 band reads: "same rounding band as L1 on the means; **in addition, at least 95% of the 260 per-protein values must agree with the authors' to 1e-6** (Jaccard, similarity) and to 1e-6 (normalized DTW)." C3 gives 0 of 260 (`analyze_sourcedata.log:9`, `l2_dtw_diff_stats.log:1`). C3 is outside its band at L2. The rule has one answer and it is *Not reproduced*.

There is no third door. *Partially reproduced* also requires "all three inside their band at L1 and L2", so it is unavailable too. The report picks the strongest of the three labels after the clause it wrote has failed, and the reason it gives — the clause was unmeetable because the deposited profiles are rounded — is a reason the clause was badly written, not a reason the run met it. Both of those things can be true at once, and the report treats the second as cancelling the first.

The report is honest about this. It states the literal reading in full, calls it a contradiction, says "we are not going to hide it behind the headline", and names this call as the one most in need of adversarial review. That candour is worth something and it does not change the arithmetic of the rule.

Would a rule that can be waived this way ever bind? No. A clause that gets reclassified as a defect of the input after it fails is not a pre-registration, it is a comment. This is the pilot's own failure mode from a different angle: on LigandMPNN the agent chose the definition after seeing the number; here the agent keeps the definition and discards the threshold. PIPELINE.md stage 7 lists "veredito mais forte do que a evidência" as the thing this stage exists to catch.

For the record, the report is right that the clause was unmeetable. The authors' own notebook rounds the profiles to two decimals at deposit (see F2), and their published per-protein values were computed from the unrounded ones, so nobody — the authors included — could rebuild their numbers to 1e-6 from the file they released. The clause measured the precision of the deposit. That is an argument for a different band next time, not for a different label this time.

**What the report should say.** Verdict line: *Not reproduced under the rule as frozen* — C3 fails the L2 per-protein clause, 0 of 260 — with the substantive summary immediately after, in the same breath: C1 and C2 reproduce from the deposited sequences and from the released checkpoints byte for byte; C3 reproduces on the mean and sd and cannot be checked per pair from the deposit. Then the band defect, named as a defect of our band. The paragraph already in the report under "The verdict against the pre-registered rule" is most of this text; it needs to be the headline, not the alternative reading.

**For the next pre-registration**: do not weld a per-item exactness clause onto a mean band with no partial-credit path, and set per-item tolerances from the precision of the deposit you are going to read (here, 3e-3, which all 260 meet). Check the deposit's precision before writing the clause; the authors' code said `round(digits = 2)` and it was already extracted in `runs/out/authors_notebook_code.txt` before the freeze.

## F2. The rounding argument is right in its conclusion and wrong in its evidence. Severity: medium

Three parts.

**The grid is firmer than the report says, and the proof was already in hand.** I read all 523,068 deposited `%MinMax` values: every one sits exactly on the 0.01 grid, maximum deviation 7.1e-15. The "[1, 2]" in `dtw_rounding_check.log:1` is stripped trailing zeros, nothing else — the decimal-count histogram is 38,716 integers, 44,504 at one decimal, 439,848 at two. So "rounded to one or two decimals" should read "rounded to two decimals", and the ±0.005 half-step the simulation used is the right half-step. Better still, `runs/out/authors_notebook_code.txt:1736` is `minmax = minmax |> round(digits = 2)`, inside the chunk that writes `benchmark_minmax_profiles.tsv`, the deposited profile sheet — while `benchmark_DTW_results` (line 1745) is built from the unrounded in-memory `benchmark_minmax_results`. That one line settles the whole question: rounding happens at deposit only, their DTW came from full precision, ours cannot. The report argued from counting decimal places in the file and never cited the line, which was in its own extracted file before the freeze.

**The simulation does not reproduce what we observe.** It adds symmetric ±0.005 noise to the published profiles and reports |shift|: mean 3.51e-04, p95 8.58e-04, max 2.04e-03. The differences we actually see are not symmetric. From `runs/out/l1_l2_per_protein.csv`: 211 of 260 of our values are **below** the authors', mean signed difference −2.809e-04 against mean absolute 3.626e-04. Three quarters of the size of the residual is one-sided bias, and a zero-mean noise model predicts a zero-mean shift. Matching the magnitude of |shift| therefore is not "the same distribution", and "to the digit on the maximum" compares the maximum of 780 random draws with the maximum of 260 observations, which is not a test of anything. As written, the probe can only ever confirm the order of magnitude it was built to confirm. Observed p95 is 9.45e-04 against the simulated 8.58e-04, for completeness.

**The test that does support it.** Quantisation of this metric has a direction, and it can be measured without the unrounded profiles: take the deposited 0.01-grid profiles as truth, coarsen them one more step to 0.1, recompute. On 40 pairs the normalized DTW moves **down in 39 of 40**, mean signed −8.60e-03, median −8.35e-03. Scaled by the 10× finer step that is ≈ −8.6e-04 against the −2.81e-04 we observe: same sign, same order. That is the claim the report wants — rounding both profiles onto a grid collapses small local differences and shortens the warped path — and it is the claim its own probe cannot make.

**What the report should say.** Cite `round(digits = 2)` from the authors' code as the primary evidence; state the grid as two decimals; report the signed statistics (211/260 below, mean −2.81e-04) instead of only the absolute ones; replace the symmetric-noise probe with the direction test, or keep it and say plainly that it bounds the magnitude and says nothing about the sign. Drop "the same distribution, to the digit on the maximum".

## F3. A log contradicts the report, and the disagreement runs the report's way. Severity: medium

`runs/logs/dtw_rounding_check.log:3`: "observed |ours - authors| per protein (from the L2 run): mean ~5e-4, max 2.03e-3". `runs/logs/l2_dtw_diff_stats.log:1`: mean 3.626e-04. The report quotes 3.6e-04 and cites both logs in the same sentence.

Recomputed from `l1_l2_per_protein.csv`: 3.626e-04. The report is right, the log is wrong, and the wrong number is a hardcoded string — `scripts/dtw_rounding_check.py:59` prints it as literal text, it was never computed. Two consequences. The log the report leans on as "measured rather than argued" contains a hand-typed figure in the middle of the measurement. And 5e-4 against a simulated 3.51e-04 would have made the agreement look 40% worse than 3.6e-04 does, so the error, by chance, favours the conclusion.

**What the report should say.** Fix the script to print the computed value, and add one clause noting the two logs disagreed, which one is right, and why. Also retire "No number in this report was estimated or typed by hand" or qualify it: it is true of the report and false of that log line.

## F4. The DTW sheet: the symptom holds, the cause does not, and the conclusion is too pessimistic. Severity: high

**The symptom is solid, and firmer than the report shows.** I confirmed one distinct `normalized_distance` per protein, 260 of 260. The report stopped there. The raw `distance` column is also a single value per protein, 260 of 260 — and `distance / (n + m)` is the normalized value to the last digit: 41.281353997167265 / 872 = 0.047341002290329434 for *A. thaliana* / Adalimumab heavy chain. So the deposited cell is one genuine DTW output, correctly normalized, broadcast across the labels. That rules out a mangled export or a recycled float, and it was free: `scripts/probe_dtw_sheet.py:44` reads the `distance` column into the matrix and never uses it.

**Whose distance is it? The probe asked the wrong question.** It matched each *row's* value to the nearest recomputed partner of that row's `model1`, over all 1352 rows — but every row of a protein carries the same value, so the counts only reflect which model's own profile sits nearest. The near-tie it returned (Fine-tuned 407, Base 406) is an artefact of that design, and the report read it as "the single deposited value is close to the Base vs Fine-tuned cell ... but that is luck, not bookkeeping".

Asked per protein instead — for each protein, which of the 10 to 15 recomputed pairs is closest to its deposited constant? — the answer is **Base vs Fine-tuned in 43 of 45 proteins** (all proteins with profiles under 260 points; the other two attribute to Fine-tuned vs ICOR), median gap 3.18e-04, maximum 1.36e-03. That gap is the rounding residual from F2, not the gap you get from a coincidence. The deposited constant *is* the Base vs Fine-tuned distance, mislabelled as every pair.

That reverses the report's conclusion about L1. "Level 1 is not an independent check of C3" and "C3 therefore rests on L2 alone" are both too strong: L1 averages the quantity C3 names, 260 times over, from numbers the authors computed at full precision. What L1 cannot do is confirm the *comparative* half of the sentence ("minimal ... between the base and fine-tuned model"), because the other pairs are not in the file. The report made its own result weaker than its data, and incidentally weaker than `claims.json`, which says C3 "rests on L1 and L2".

**The named cause cannot be what happened.** The chunk at line 1745 nests `comparison1 = c(model1, minmax1)` and `comparison2 = c(model2, minmax2)` *before* `complete(comparison1, comparison2)`; the authors' comment on the identical natural-gene chunk (line ~735) is "# link model and minmax profiles". The nesting exists precisely so that each profile travels with its label, so crossing the nested columns carries the pairing by construction. And read literally, the report's mechanism — `minmax1` and `minmax2` both taken from the same `model` row — predicts `minmax1 == minmax2` and therefore a matrix of zeros, not a non-zero constant. The observed symptom is neither what the mechanism predicts nor what correct code predicts.

**What is checkable about that chunk, and it is stronger.** The chunk cannot run as written. It ends:

```
select(organism, protein, model1, model2, distance, normalized_distance) |>
select(organism, description, model1, model2, dtw_object)
```

The second `select()` asks for `description` and `dtw_object`, which the first one just dropped; `protein` is dropped in favour of a `description` column this frame does not have. The export chunk at line 1911 then selects `distance` and `normalized_distance` off the saved object, which the first `select()` also dropped. So the deposited notebook's DTW chunks are mutually inconsistent and are not the code that produced the deposited sheet. Anyone can check that in thirty seconds; the label-crossing story is a guess about code nobody ran.

**The alternative the report should have ruled out, and it does rule itself out.** "We are reading the layout wrong" dies on three facts: the sheet is long-format with explicit `model1`/`model2` columns that the probe reads correctly; all 1352 diagonal entries are non-zero (`analyze_sourcedata.log:6`), which no layout convention makes sensible; and the single value per protein is a real, correctly normalized DTW of the pair C3 names. So: pairing lost, number real, cause unknown.

**And the paper's figure is fine.** The paper quotes four different per-pair DTW means — 0.05 ± 0.03 base vs fine-tuned, 0.07 ± 0.02 Twist/IDT, 0.24 ± 0.11 Genewiz/Twist, highest for Genewiz/IDT (verified in `paper/fulltext_PMC11968976.txt`). A figure drawn from the broken object would show one value per protein across all pairs and could not produce those four numbers. The breakage is in the deposit, downstream of the figure. The report never says this, and it is the single most useful sentence for the authors.

**What the report should say.** Keep the symptom, with the raw-`distance` evidence added. State the per-protein attribution (43 of 45 to Base vs Fine-tuned) and restore L1 as a real check of the C3 mean, noting that it cannot check the comparison against the other tools. Replace the mechanism with the two facts that hold: the chunk as deposited cannot run, and the breakage is in the deposited sheet only because the paper reports per-pair values the broken object cannot yield. In "Notes for the authors" item 1, drop the sentence that asserts the mechanism — a question to the authors should carry the symptom and the non-runnable chunk, not our guess at the line that caused it.

## F5. Byte-identity is a provenance result, and the claim table shows one fact as nine. Severity: medium

520 of 520 identical means the L3 column equals the L2 column by construction — for C1 and C2 as much as for C3. The report notes the mechanism only for C3 (line 38). And for C1 and C2, L1 equals L2 as well: maximum per-protein difference 0.000e+00, 260 of 260. So the 4×4 table holds two independent facts:

1. our implementation of the three definitions, run on the deposited sequences and profiles, gives 0.7379, 69.2629 and 0.0459 ± 0.0338, which round to the published 0.74, 69.26 and 0.05 ± 0.03;
2. the two released checkpoints with deterministic decoding regenerate the deposited sequences byte for byte.

"Reproduced for C1 and C2 at all three levels" reads as three checks and is one. Say two facts, and say which is which.

What identity cannot catch: nothing about training or pretraining (the report covers this well for issue #28); nothing about the `%MinMax` → DTW path, since identical DNA does not supply the missing frequency table; nothing about the comparator tools; nothing about Fig. 4d or Figures 1–3; and nothing about whether the deposited sequences are the ones that made the figure — that is argued by the metric agreement, not by the identity. Identity is also silent on any defect shared by the checkpoint and the deposit, which is the honest reading of issue #28 and which the report gives.

One thing the identity does establish and the report leaves implicit: the authors' benchmark must also have been generated deterministically, because a sampled decode would not come back byte-identical 520 times. That is a finding. It also means the pre-registered decoding choice was not merely prudent, it was the authors' own, and the report presents the convergence as prudence.

## F6. The E. coli token conclusion follows; the sentence about how much it matters does not. Severity: medium

The conclusion is safe: 52/52 byte-identical with `Escherichia coli general`, 0/52 with MG1655, for both checkpoints (`compare_l3_primary.log`, `compare_l3_mg1655.log`). An exact match on 52 sequences settles which vocabulary entry the benchmark used. The third entry, `Escherichia coli O157-H7 str. Sakai` (id 50), was never generated; with an exact match in hand that does not matter, and the report should say that rather than leave the reader to notice.

The framing around it is wrong. "Similarity is 71.4173 against 71.5759 (delta +2.1573 from 69.26, **outside** the ±2.0 band)" compares a one-organism mean with a five-organism published mean, inside a band `claims.json` defines for the 260-pair mean. The like-for-like comparison is the one the same sentence already prints: 71.5759 → 71.4173, **0.16 percentage points**. So the token changes every one of 52 sequences and moves the aggregate by 0.16 pp. Calling that "the only band miss at L3 in any log" and "the measure of how much the unstated token matters" promotes a category error to a finding. `compare_l3_mg1655.log:10` prints `OUTSIDE` because the script was handed the all-organism published value; the log is doing what it was told, not reporting a miss.

**What the report should say**: with the wrong token no sequence matches, and the *E. coli* mean codon similarity moves by 0.16 pp. Drop the 2.1573 and the band language, or mark it in the log as not applicable for a single-organism subset.

## F7. Four report numbers cite logs that do not contain them. All four are right. Severity: low

- "the published %MinMax profile length is exactly the codon count minus 17 for all 260 proteins and both checkpoints", cited to `analyze_sourcedata.log` — not in that log, nor in any log. Recomputed from `l1_l2_per_protein.csv`: holds for all 260 and both checkpoints, 0 violations. Codon counts base == fine for 260 of 260, which is the log's "0 pairs of unequal length".
- the agreement ladder "46 within 1e-4, 194 within 5e-4, 250 within 1e-3, 259 within 2e-3, all 260 within 3e-3", no citation — recomputed: 46 / 194 / 250 / 259 / 260. Exact.
- "687.9 s model time summed per row, mean 1.32 s per sequence, slowest single sequence 26.6 s", cited to `generate_primary.log`, which logs only every twentieth row and the 698 s total — recomputed from `generated_primary_metrics.csv`: sum 687.9 s, mean 1.32 s, max 26.6 s over 520. Exact.
- "Proteins run from 102 to 1369 amino acids, median 372", no citation — recomputed from `generated_primary.csv`: 102 to 1369, median 371.5 over 260 proteins. The report rounds a half-integer median to 372 without saying so.

Nothing here is wrong; the citations are. Point them at the CSVs, or print the lines into a log.

## F8. "The quotes match it word for word" is not true. Severity: low

Checked against `paper/fulltext_PMC11968976.txt`. All three published values are verbatim — "mean of 0.74", "mean of 69.26", "mean of 0.05 ± 0.03" — and the panel assignments (4a, 4b, 4c) and the "excluding ICOR" aggregation are right. The quoted *sentences* are paraphrases: `claims.json` C1 ends "than with any other tool" where the paper has "tools", and drops the paper's parenthetical; C2 reads "showed the highest sequence similarity score" where the paper has "showed the highest score". Meaning intact. Claim paraphrase, not verbatim.

## F9. C3's one surviving level passes with little room. Severity: low

L2 mean 0.045890 against a band of 0.05 ± 0.005: 0.00089 left, 18% of the band. The sd, 0.033764, has 0.00124 left. True and thin, and after L1's lost labels and L3's missing table it is the whole of C3. One clause.

## F10. The "Not checked" list is honest, with two gaps. Severity: low

It is better than most: issue #28 and the pretraining, Fig. 4d and the proprietary columns, Figures 1–3, peak RSS never measured, no CPU model, adversarial review and blind recount both declared not done, verdict declared provisional. I found nothing in it that the run actually did check, and nothing checked that it claims not to have.

Two things it does not say. First, nothing in this run speaks to the paper's actual claim that the optimizer works: C1, C2 and C3 are internal consistency between the paper's own two checkpoints, and a reader who stops at "Reproduced" will not get that from the list. Second, with the frequency table missing, the `%MinMax` step is not validated in either direction — C3 at L2 is a check of our DTW on their profiles, not a check of their profiles. The `%MinMax` section says so; the Not-checked list should repeat it, because that is the list people read.

---

## Attacked and did not break

- **The pre-registration hash.** Recomputed SHA-256 of `claims.json`: `f0f534f986e28bd0fc05c1632821540c958191063a809121b6ce90220e203a02`. Matches `claims.json.sha256`, `claims_hash_check.log` and the report. The 14-minute inconsistency in the internal `frozen_at` field is disclosed in the report and is cosmetic; the hash and `claims.frozen_at.txt` (20:26:08Z) are the record. Order in time rests on timestamps inside a folder the agent controlled, which no reviewer can verify from here; that is a limit of the method, not a finding against this run.
- **dtw-python against R's dtw.** The report asserts "nothing in the numbers suggests a difference between the two implementations" without testing it, which is exactly the kind of sentence that should fail. It does not. I wrote symmetric2 from the step pattern and got values 2.5e-04 higher on average than the run's — the same size as the residual the report attributes to rounding, which looked like a finding for about ten minutes. It is not: the difference is exactly `|a₁ − b₁| / (n + m)` on all 8 pairs tested, to every printed digit, i.e. only the weight of the first cell. With dtw-python's convention my implementation reproduces the run's numbers exactly, including 0.046788990825687986 for the example pair. The assertion stands; it was still asserted untested.
- **The claim table and the band deltas.** Recomputed: C1 0.002144, C2 0.002883, C3 mean 0.003829, C3 sd 0.003760, all inside 0.005. Per-organism table, A1 (0.6266) and A2 (identical, 52 per organism) all match the logs.
- **The probe's other numbers.** 1352 non-zero diagonal entries, 0.0126115 to 0.24322; the 407/406/247/220/50/22 counts; "the Base vs Fine-tuned cell is the smallest off-diagonal entry in both example matrices" — all re-read and correct.
- **The %MinMax table rejection.** Table P 0.1525 and table K 0.0378, both REJECT against the pre-registered 0.02 ceiling, 50 natural genes per organism, worst cases as quoted. Matches `validate_minmax.log`. Table K was added after the freeze and is correctly declared as an extra; since both candidates fail, the addition cannot have moved the verdict.
- **Generation.** 520 rows, 520 identical, zero FAILED lines in either log, 698 s and 104 s as reported.

## Verdict on the verdict

**Not reproduced** is the honest label under the rule as frozen. C3 is outside its L2 band by that band's own second clause, 0 of 260, and the rule says what follows. *Partially reproduced* is not available either, since it also requires all three claims inside at L1 and L2 — so the frozen rule admits exactly one answer, and the report publishes a different one.

I think the report is wrong on the headline and right on nearly everything underneath it. The band it broke is a band it should not have written: a 1e-6 per-item clause against a file the authors rounded to two decimals before deposit, which their own code shows and which this run measured. Saying so is fair. Overriding the label on the strength of it is not, because a threshold that gets reclassified as unmeetable after it fails never constrained anything, and this pipeline exists on the premise that the pre-registration binds.

The substance deserves to be stated plainly in the same place, and it is good: C1 and C2 reproduce at every level that exists, from a deposit and from two released checkpoints that regenerate 520 sequences byte for byte; C3 reproduces on the mean and the sd, to 0.0003, at two levels — L1 included, which F4 restores — and cannot be checked per pair because the deposited sheet lost its pair labels and per item because the deposited profiles were rounded. Plain language calls that partial. The frozen rule cannot say it. Publish the label the rule gives, with the reason in the same sentence, and fix the band before the next paper.

The two calls flagged for attack come out differently from how the report frames them: the C3 band miss is a real miss that should change the label, and the DTW sheet diagnosis is a guess at a cause that the deposited code cannot have produced — while the symptom behind it is firmer than reported, and its consequence for C3 is milder.

Reviewed by an AI agent (Claude, by Anthropic). Nothing here was published; `REPORT.md` was not modified. Per the rule of 2026-11-08, the blind recount has still not run, so no issue can be opened either way.
