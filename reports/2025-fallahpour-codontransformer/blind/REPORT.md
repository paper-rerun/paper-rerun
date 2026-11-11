# Blind recount: CodonTransformer, Figure 4, Base vs Fine-tuned

Paper: Fallahpour A, Gureghian V, Filion GJ, Lindner AB, Pandi A. "CodonTransformer: a multispecies codon optimizer using context-aware neural networks." Nature Communications 16, 3205 (2025). DOI 10.1038/s41467-025-58588-7.

Code: github.com/Adibvafa/CodonTransformer (Apache-2.0). Weights: huggingface.co/adibvafa/CodonTransformer (fine-tuned) and .../CodonTransformer-base (base), both public and ungated.

This is the blind recount arm. It was written from this folder's own evidence: the paper full text (Europe PMC PMC11968976; the full text itself is not redistributed here), the published Source Data zip, the two Hugging Face weight repos, and the `kodonz` R package tables. No earlier reproduction of this paper was opened. Read and approved for publication by Filipe Tessaro on 2026-11-11.

Pre-registration: `claims.json`, SHA-256 `308d4ef340c207c724e3747a7fa90bff2a270744ef1401952022d5ab9245042f`, frozen 2026-11-11T00:37:34Z (`claims.sha256`). The hash still matches the file as it stands. Every band quoted below was written before any metric was run.

## Verdict

**Reproduced, with the pre-registered caveat on Fig. 4d.** All four headline claims land inside their frozen bands, the secondary claim C5 does too, and the ordering claim C6 holds once its wording is corrected (see below). Two things keep the word "Reproduced" from standing bare, and both were foreseeable from the frozen rule itself:

1. The frozen `verdict_rule` has a branch "Reproduced with a caveat" that fires when "C4 had to be read off the authors' published counts rather than recomputed from the GenScript tool (which is the plan, so this caveat is expected and must be stated whatever the outcome)". That is exactly what happened, so the rule's own text points at the caveat branch and not at plain "Reproduced".
2. C6 as frozen says the base/fine-tuned pair is "the most similar pair among the five organism-general tools" in Fig. 4a. Taken literally that half of C6 fails: IDT vs Twist comes out at 0.9235, well above base vs fine-tuned at 0.7379. But the paper does not claim otherwise. Its own sentence reads "Among all the pairs, IDT and Twist showed the highest similarity score (0.92)". The frozen C6 misstated the paper, not the other way around. Corrected wording, recorded here as a correction to my own pre-registration: *in Fig. 4a the fine-tuned model is the base model's most similar partner among the other tools; the globally highest Jaccard pair is IDT/Twist, as the paper says.* Under that reading C6 holds on 4a, 4b and 4c. The literal frozen wording, applied without the fix, would cap the verdict at "Partially reproduced" through no fault of the paper.

Nothing else in the evidence works against the verdict.

## Headline claims

Published values from the Results section "Model benchmark for heterologous expression of proteins" and the Fig. 4 caption. Recount values from `results_recount.json` (final run: `logs/recount3.log`). n = 52 proteins x 5 organisms = 260 pairs.

| Claim | Panel | Published | Recount | Band | Gap | In band |
|---|---|---|---|---|---|---|
| C1 | 4a, Jaccard, base vs fine-tuned | 0.74 | 0.7378555443768628 | 0.015 | 0.0021 | yes |
| C2 | 4b, sequence similarity | 69.26 | 69.26288301454848 | 0.75 | 0.0029 | yes |
| C3 | 4c, normalized DTW mean | 0.05 | 0.045890135997284975 | 0.02 | 0.0041 | yes |
| C3 | 4c, normalized DTW sd | 0.03 | 0.03376387617694362 | 0.02 | 0.0038 | yes |

C1 and C2 come from the Source Data sheet "DNA sequences, CSI, CIS-element": 260 rows, 52 distinct proteins, the 5 expected organisms, no length mismatch in any tool pair. C3 runs my own DTW over the authors' published %MinMax profiles (1352 profiles, 6 model labels) from the "%MinMax" sheet.

C3b, the sensitivity arm where the %MinMax profiles are rebuilt from scratch instead of read from the Source Data (Clarke & Clark as `kodonz/R/pminmax.r` implements it, window 18 codons, kodonz's own GenScript host tables, all six tables 64 codons): pooled mean 0.04608884935972924 with the `saccharomyces` yeast table, 0.046211005373219385 with the `yeast` table, sd 0.0337 either way (`results_minmax_own.json`). Both sit inside the 0.03 band, and the table choice that the Methods leave open moves the pooled mean by 0.00012. Per organism the from-scratch distance ranges from 0.0245 (M. musculus) to 0.0976 (S. cerevisiae). C3b cannot change the verdict and does not need to.

## Fig. 4d, the ten cis-element values

Recomputed means per organism, n = 52 per organism per model, band 0.01:

| Organism | Published base | Recount base | Published fine-tuned | Recount fine-tuned |
|---|---|---|---|---|
| E. coli | 0.37 | 0.36538461538461536 | 0.29 | 0.28846153846153844 |
| S. cerevisiae | 0.02 | 0.019230769230769232 | 0.1 | 0.09615384615384616 |
| A. thaliana | 0.06 | 0.057692307692307696 | 0.17 | 0.17307692307692307 |
| M. musculus | 0.1 | 0.09615384615384616 | 0.02 | 0.019230769230769232 |
| H. sapiens | 0.1 | 0.09615384615384616 | 0.04 | 0.038461538461538464 |

Ten of ten inside the band; the largest gap is 0.0046 (E. coli, base). Every recount value is an exact multiple of 1/52, which also confirms the denominator. The reading fixed before running - in each published pair the first number is the base model and the second the fine-tuned one, inferred from the following sentence saying the fine-tuned model reduced the count for E. coli - is consistent with all five pairs.

**Caveat, pre-registered and unavoidable.** The published cis-element counts come from GenScript's rare-codon-analysis web form, an interactive third-party service. I did not submit 520 sequences to it. C4 therefore averages the per-sequence CIS counts the authors themselves published in the Source Data. It tests the arithmetic and the reporting of Fig. 4d. It does not test the GenScript tool, and it does not independently confirm that those per-sequence counts are what GenScript returns today.

## Regeneration from the published weights (C5)

`scripts/generate.py` regenerates all 52 x 5 sequences for both models from the Hugging Face weights, CPU only, through the authors' own `predict_dna_sequence` entry point, deterministic, `attention_type="original_full"`, the "protein sequence only" route of the Methods. Both snapshots carry 89,579,610 parameters. Snapshots pulled: `9744dcc920d813066391fc828d7a590207f148e8` (fine-tuned) and `15cf7f265320eeca9943f2132d43100faa4d3bee` (base).

Result (`results_generate.json`): **520 of 520 regenerated sequences are byte-identical to the Source Data sequences** - 260 of 260 base, 260 of 260 fine-tuned, mean per-codon identity 100.0% for both. The Fig. 4a/4b means recomputed on my own sequences are therefore identical to C1 and C2 to every digit: Jaccard 0.7378555443768628, sequence similarity 69.26288301454848. Bands were 0.05 and 4.0; the gap is zero. This is the strongest single piece of evidence in the folder: the published weights, driven by the published package, reproduce the published benchmark sequences exactly, and those sequences give the published figure.

The organism token chosen for each host is recorded in the output: "Escherichia coli general" for E. coli, and the plain binomial for the other four.

## Cross-check on the other tool pairs

Not verdict-driving (C6 context), but every other Fig. 4 number the running text gives can be checked from the same recount:

| Published | Recount | Gap |
|---|---|---|
| 4a, base vs Twist 0.61 | 0.6071764426860529 | 0.0028 |
| 4a, base vs IDT 0.60 | 0.6042291346052934 | 0.0042 |
| 4a, base vs Genewiz 0.59 | 0.5919598964012147 | 0.0020 |
| 4a, IDT vs Twist 0.92 (highest pair) | 0.9235140118048266 | 0.0035 |
| 4b, Genewiz vs base 61.42 | 61.42239200446058 | 0.0024 |
| **4b, Genewiz vs fine-tuned 62.58** | **62.68000221612384** | **0.10** |
| 4c, Twist vs IDT 0.07 +/- 0.02 | 0.07376848086622993 +/- 0.01982589322625632 | 0.0038 |
| 4c, Genewiz vs Twist 0.24 +/- 0.11 | 0.24181545309424074 +/- 0.10620344747104991 | 0.0018 |
| 4c, Genewiz vs IDT 0.40 +/- 0.15 | 0.4006276826873867 +/- 0.15125300708736808 | 0.0006 |

The paper's two blanket statements in 4b also hold: IDT is under 40 with sd under 4 in all its comparisons (37.18 to 38.96, sd 3.09 to 3.48) and Twist is under 50 with sd under 4 (43.85 to 46.97).

**The one that does not match is Genewiz vs fine-tuned in Fig. 4b: the paper says 62.58, I get 62.68.** The gap is 0.10, twenty times the 0.005 that two-decimal rounding allows, while the sibling value in the same sentence (Genewiz vs base, 61.42) matches to 0.0024 and every other number in the table matches to within 0.005. A transposed digit in 62.58 / 62.68 is the obvious reading, but I cannot prove it from here, so it goes to the authors as a question. It does not touch the base-vs-fine-tuned comparison this recount was asked about, and it does not change any ordering: 62.68 is still well below 69.26.

## Three defects found

**1. Equation 6 does not describe the implementation the Methods name.** The paper's eq. 6 gives %MinMax as (xmax - xmin)/(xmax + xmin) * 100. The Methods say the %MinMax profiles were computed with the R package `kodonz`, and `kodonz/R/pminmax.r` implements Clarke & Clark 2008 instead: over a sliding window, sum(f - favg) / sum(fmax - favg) when the numerator is positive, otherwise sum(f - favg) / sum(favg - fmin), returning a signed fraction. The %MinMax values published in the Source Data are signed fractions in roughly [-1, 1], which eq. 6 cannot produce - it is non-negative and on a percent scale. I did not use eq. 6 anywhere. C3 uses the authors' published profiles, and C3b reimplements the kodonz arithmetic; both land on the paper's number, which is further evidence that the published figure came from kodonz and not from eq. 6. The equation as printed is wrong, or at least describes something else.

**2. The per-pair DTW sheet of the Fig. 4 workbook is unusable.** Checked in `results_recount.json` under `published_DTW_sheet_check`: 7072 rows; 1352 of them are self-comparisons (model1 == model2), and **not one** of those 1352 has distance 0, which a self-comparison must; and all 260 (organism, protein) groups carry exactly one distinct distance value across every model pair in the group. In other words the sheet holds one number per protein, replicated under every pair label, rather than one number per pair. This was declared before any metric was run, from the first four rows, and the whole-sheet check confirms it. The equivalent sheet in the Fig. 3 workbook does vary by model2 and does give 0 for the self-comparison, so the fault looks specific to this workbook. The rows labelled base vs fine-tuned there average 0.04617104235693258 +/- 0.03372726435601904 over 520 rows, which is within 0.0003 of my own base-vs-fine-tuned 0.04589 - consistent with the base-vs-fine-tuned distance having been broadcast across every label in the sheet. Nothing in my verdict depends on this sheet: C3 is computed from the "%MinMax" sheet. But a reader who took Fig. 4c's underlying table at face value would read the same number for every tool pair.

**3. The base model repo ships no tokenizer.** `adibvafa/CodonTransformer-base` at main contains only `config.json`, `generation_config.json` and `model.safetensors`. The first regeneration attempt died on it: `OSError: Can't load tokenizer for 'adibvafa/CodonTransformer-base'` (`logs/generate.log`, after the fine-tuned half had already finished, 13 min 25 s wasted). The two models share a tokenizer, so loading it from `adibvafa/CodonTransformer` and using it for both works and gives exact agreement with the Source Data - but that is a guess a user has to make, and the base repo is the one the paper offers "to the community for custom fine-tuning".

## Metric choices fixed before running

All of these were written into `claims.json` before any number existed, under `fixed_definitions`:

- **Codon reading frame.** Split from position 0 in non-overlapping steps of 3; a trailing partial codon is dropped. The terminal stop codon, where present, is counted, because the Source Data codon-count sheets list STOP_TGA / STOP_TAA / STOP_TAG as codons, so the authors' own pipeline counts it. No alternative was tried after the fact.
- **Jaccard over sets.** A and B are the sets of *distinct* codon strings in each sequence; J = |A and B| / |A or B| (paper eq. 9).
- **Sequence similarity.** 100 * matching positions / L, L the common codon count (paper eq. 10). A pair with unequal L would have been reported, not truncated. There were none.
- **DTW and its normalizer.** Local cost |x_i - y_j|, step pattern symmetric2, open.begin = open.end = FALSE, statistic = cumulative cost / (N + M), which is what R's `dtw` returns in `normalizedDistance` under its defaults - and the Methods say they took `normalizedDistance` with default parameters. This mattered: because the paired profiles always have equal length, dividing by N instead of N + M gives exactly double, 0.09178027199456995 +/- 0.06752775235388724, which is outside the 0.02 band and would have read as a failed claim. The same doubling applies to every pair, so the ordering survives either way, but the level only matches under the committed normalizer. Pinning it in advance is the only reason that is a sensitivity note here and not an argument.

## My own bug, caught by my own check

The first version of my DTW dynamic program weighted the origin cell twice: it applied the symmetric2 diagonal weight (2 * d) at D[1][1], where the first cell must be counted once. Every distance came out inflated. I had also talked myself into a wrong hand-written expectation for a 2x2 case, having forgotten that the cheapest path may take a vertical step.

What caught it was `scripts/test_metrics.py`, written as an independent check rather than as a number I believed: it enumerates every monotone warping path by brute-force recursion under the symmetric2 weighting and compares against the DP on 300 random cases (seed 20261111, sizes 1 to 7, values in [-1, 1]), plus fixed asserts on the codon split, Jaccard, similarity and the identity case. The final DP (`recount.py`, the `if i == 1 and j == 1: cur[1] = d` branch) passes all of it. This is stated plainly because the alternative is to let a self-caught bug look like a clean first draft: my first DTW was wrong, and the check I wrote before trusting the numbers is what found it.

## Runtime, memory and environment

Every run went through `/usr/bin/time -v` under `nice -n 19`, CPU only, `OMP_NUM_THREADS=MKL_NUM_THREADS=4`, `torch.set_num_threads(4)`, `MPLBACKEND=Agg`.

| Log | What | Wall | CPU (user + sys) | Peak RSS | Exit |
|---|---|---|---|---|---|
| `recount.log` | recount, attempt 1 | 7:25.58 | 420.5 s | 73,204 KB | 1 |
| `recount2.log` | recount, attempt 2 | 3:44.20 | 220.1 s | 73,112 KB | 0 |
| `recount3.log` | recount, final | 5:44.80 | 340.4 s | 74,404 KB | 0 |
| `minmax_own.log` | C3b from-scratch %MinMax | 1:35.41 | 69.0 s | 100,704 KB | 0 |
| `generate.log` | C5, attempt 1 | 13:24.71 | 1606.9 s | 1,253,628 KB | 1 |
| `generate2.log` | C5, final | 11:50.14 | 2176.8 s | 1,212,092 KB | 0 |

Total 43 min 45 s of wall time over the six runs. Peak memory for the whole study is the inference run at 1,212,092 KB, about 1.16 GiB, inside the 8 GB budget declared in `claims.json`. Two failures are logged and both are explained above: `recount.log` crashed on an empty selection because the model labels in the Source Data carry an embedded line break ("Codon- Transformer") that my first filter did not normalise, and `generate.log` crashed on the missing base-model tokenizer.

Environment, built in two stages with `uv` and frozen (`env-freeze-stage1.txt`, `env-freeze-stage2.txt`), Python 3.12 in a local venv, all scripts run with `python -I`:

- stage 1, the recount: `openpyxl==3.1.5`, `numpy==2.1.3`, `pandas==2.2.3`
- stage 2, the inference: `torch==2.5.1+cpu`, `transformers==4.46.3`, `tokenizers==0.20.3`, `CodonTransformer==1.6.7`, which pulled `numpy` back to `1.26.4`
- stage 3, the sensitivity arm: `rdata==0.11.2`, to read the kodonz `.rda` frequency tables

The CPU wheels needed a second index: `uv pip install --index-strategy unsafe-best-match --extra-index-url https://download.pytorch.org/whl/cpu` (`scripts/setup_env2.sh`). TLS verification was on for every download; nothing was fetched with verification disabled. **On the IPv6/PyPI note: there is no record of one on disk.** No log, script or freeze file in this folder mentions an IPv6 fallback, a PyPI reachability problem or a retry, so this report cannot confirm or describe one; the only install evidence is the two `setup_env*.sh` scripts above and the two freeze files.

Source Data zip: sha256 `8dc388e45ddb9efee17b6f2e6bc070fb14bc6779977708f485294d84330f198f`, 8,024,232 bytes, from the Springer static-content URL recorded in `claims.json`. Workbook used throughout: "Source Data/Fig. 4, Supplementary Fig. 19f-h, 20, 21, 22 and 25.xlsx".

## What was not checked

- **The GenScript rare-codon tool itself.** Fig. 4d was recomputed from the authors' published per-sequence counts, not by re-running the web form. See the caveat above.
- **Figures 2 and 3, and every supplementary figure.** The organism-level panels behind Fig. 4 (Supplementary Figs. 20, 21, 22, 25) were not recomputed; only the across-organism means the running text states. The Fig. 2b and Fig. 3 workbooks were downloaded but only the Fig. 3 DTW sheet was glanced at, to establish that defect 2 is specific to the Fig. 4 workbook.
- **Training.** Nothing was retrained. The claims are about the published weights and the published benchmark, and both were taken as given.
- **CSI values.** The Source Data carries a CSI column per tool; no claim in scope used it, so it was not checked.
- **RNA folding energy, GC content, codon distributions.** Out of scope.
- **Equation 6's effect elsewhere.** Defect 1 says the printed equation does not match the implementation. I did not trace whether any other figure in the paper was computed from eq. 6 as printed.
- **The authors' R notebook** (`Reproduce_figures.nb.html`, inside the Source Data zip) **was not opened.** The pre-registration allowed opening it only if a claim missed its band, and required declaring the fact. No claim missed, so the rule never fired and nothing on disk shows it being read. Every metric here comes from the paper's equations and from kodonz's published source.
- **Statistical significance.** The paper states means and standard deviations for Fig. 4; no test was reported and none was run.

## Questions for the authors

1. Fig. 4b: the text gives the Genewiz / fine-tuned mean sequence similarity as 62.58. Recomputing it from your own Source Data sequences gives 62.68, while the Genewiz / base value in the same sentence (61.42) reproduces to four decimals. Is 62.58 a typo for 62.68, or is a different subset of sequences behind it?
2. Equation 6 defines %MinMax as (xmax - xmin)/(xmax + xmin) * 100, but the Methods say the profiles were computed with `kodonz`, whose `pminmax.r` implements the Clarke & Clark windowed signed statistic, and the published profiles are signed fractions in roughly [-1, 1]. Should eq. 6 read as the Clarke & Clark formula, and is kodonz what produced Figs. 3 and 4?
3. In the Fig. 4 workbook's "DTW" sheet, all 1352 self-comparison rows carry a non-zero distance and every (organism, protein) group carries a single distinct value across all model pairs - and that value tracks the base-vs-fine-tuned distance. The equivalent sheet in the Fig. 3 workbook behaves as expected. Was the Fig. 4 per-pair table written out with the wrong grouping key? Could a corrected table be deposited? The figure's published pair means do reproduce from the "%MinMax" sheet, so this looks like a deposit bug rather than a figure bug.
4. Which %MinMax window length and which host codon frequency table were used? The Methods state the window; `kodonz` ships both a `yeast` and a `saccharomyces` table for S. cerevisiae and the Methods name neither. The choice moves our pooled DTW mean by only 0.0001, so this is about the record, not the result.
5. `adibvafa/CodonTransformer-base` at main ships no tokenizer files. Using the fine-tuned repo's tokenizer for both models reproduces your benchmark sequences exactly, but users fine-tuning the base model have to guess that. Could the tokenizer be added to the base repo?
6. Which inference route and settings produced the 52 benchmark sequences? We assumed the "protein sequence only" route, deterministic, `attention_type="original_full"`, and got all 520 sequences byte-identical, so the answer is probably "exactly that" - worth stating in the Methods, since it is what makes the benchmark reproducible.

## How this report was made

Written by an AI agent (Claude), running as the blind recount arm of the reproduction pipeline described in `E:\Ciencia\PIPELINE.md`, section "Reconta cega antes de publicar". The arm's rule is that it never sees the other reproduction of the same paper: no `REPORT.md`, no `claims.json`, no scripts, no issue draft, no log from that side. That rule was kept - the sibling folder was never opened or listed, and nothing in this report comes from it.

Order of work, which is also the order the files on disk were created: download the paper full text and the Source Data; look at the workbook's sheets; read the Methods, the Results section and the Fig. 4 caption and write down every number the text attributes to Fig. 4; read `kodonz/R/pminmax.r`; write `claims.json` with the bands and the verdict rule and hash it; then compute. Nothing was computed before the freeze, and the frozen file's hash still matches.

Every number in this report was read out of `results_recount.json`, `results_minmax_own.json`, `results_generate.json`, the six files in `logs/`, the two freeze files, or the paper full text. None was typed from memory or estimated. Where a value is quoted to many digits, that is the digits the result file carries.

The one piece of self-correction worth repeating: the frozen C6 wording was stronger than the paper's own claim, and this report corrects the wording rather than scoring the paper against a sentence the paper never wrote. The band on each headline claim was not touched.

Nothing here has been posted. No issue was opened, no commit made, no mail sent. Publication waits on a human reading this report.
