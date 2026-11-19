# Blind reproduction check: Table S4 of Sicho et al. 2023 (DrugEx), the two RNN rows in scope

Independent re-measurement of two rows of Supporting Information Table S4 ("Sampling
statistics") of:

> Sicho M., Luukkonen S., van den Maagdenberg H.W., Schoenmaker L., Bequignon O.J.M.,
> van Westen G.J.P. *DrugEx: Deep Learning Models and Tools for Exploration of Drug-like
> Chemical Space.* J. Chem. Inf. Model. 2023, 63(12), 3629-3636. DOI 10.1021/acs.jcim.3c00434

Authors' code: https://github.com/CDDLeiden/DrugEx

Everything below was produced in this folder on 2026-11-19, CPU only, 4 threads, one heavy
process at a time, peak resident memory 410 MB. Nothing was published anywhere.

## 1. Pre-registration

`claims.json` holds the targets, the definitions I chose, the tolerance and the falsifiers
I committed to testing. It was written and hashed before a single molecule was sampled.

```
sha256(claims.json) = 465e1bd17fdb2b55fb88a31c661ee3893632ea27522b29548d1df2e9453af9da
```

The same hash is in `claims.json.sha256`. The pre-registered verdict rule: *reproduced* if
all four in-scope numbers land within 0.010 absolute, *partially reproduced* if some but
not all do, *not reproduced* if none do. 0.010 is the run-to-run deviation the paper itself
claims ("below 1.00%").

## 2. What I had to work out

**Where the weights are.** The repository README carries a table of pretrained models.
ChEMBL 27 LSTM RNN is Zenodo 10.5281/zenodo.7096837 (`DrugEx_v2_PT_ChEMBL27.zip`), ChEMBL 31
GRU RNN is Zenodo 10.5281/zenodo.7550739 (`DrugEx_v2_GRU_PT_ChEMBL31.zip`). Each zip holds a
`.pkg` state dict and the `.vocab` it was trained with; both load with `strict=True`, so the
vocabularies and the checkpoints match. Hashes in `logs/provenance.txt`.

**What the two metrics have to mean to be computable at all.** The released sampler
(`SequenceRNN.generate`) keeps drawing batches until it holds `num_samples` molecules
*after* filtering, and by default it drops invalid molecules and duplicates. The default
output of the published command is therefore valid and unique by construction, and neither
metric can be computed from it. Both are only computable from the raw sample, which the
release exposes through `--keep_invalid` (API: `drop_invalid=False`). So I sampled exactly
100,000 raw sequences per model at batch size 600 and computed everything from those.

For **validity** I used the only validity computation in the package,
`drugex.training.scorers.smiles.SmilesChecker.checkSmiles(..., no_multifrag_smiles=True)`:
a sampled string is valid if it contains no `.` and `Chem.MolFromSmiles` returns a molecule.
`no_multifrag_smiles=True` is hard-coded on this code path in `drugex/generate.py`, so this
is the release's own rule, not my invention.

For **uniqueness** I used distinct RDKit canonical SMILES among the valid molecules divided
by the number of valid molecules, canonicalising exactly as `Generator.filterNewMolecules`
does. Reasoning: "the ratio of unique molecules" is a statement about molecules, and a
string RDKit cannot parse is not a molecule; and the release itself de-duplicates only after
canonicalising the valid set. Three secondary variants were pre-registered and are reported
in section 5.

**Sample size.** Uniqueness falls as n grows, so both claims were judged only at
n = 100,000. The 1,800-molecule pilots were used only to check the code runs and to estimate
runtime.

## 3. Does the published command run as released?

No. Two defects, both still present in the newest release (v3.4.8, December 2024).

1. `python -m drugex.generate` imports `drugex.train`, which executes
   `from qsprpred.models.interfaces import QSPRModel` at module level. `qsprpred` is
   commented out of `setup.cfg`, so a plain install of DrugEx cannot run DrugEx's own CLI
   (`logs/cli_attempt.log`). The README does call QSPRPred optional "if you want to use the
   command line interface", but the paper-era QSPRPred (v1.3.1) then pulls in a chain of
   further undeclared, unpinned packages before that single import succeeds: `mordred`,
   `PaDEL_pywrapper`, `Mold2_pywrapper`, `pystow`, `fake_useragent`, `sklearn_json`,
   `chembl_structure_pipeline`, plus `setuptools<81` for `pkg_resources`. Two of them pin
   backwards: `mordred` needs `numpy<2`, `sklearn_json` needs scikit-learn below 1.2.
   Installing the chain the obvious way upgrades numpy to 2.x and breaks mordred. Eight
   packages and two pins to satisfy one import.
2. With the chain satisfied, the CLI still dies on a CPU-only host:
   `RuntimeError: Invalid device string: 'cuda:-1'` (`logs/cli_attempt2.log`).
   `Model.updateDevices` correctly sets `gpus = (-1,)` for CPU, but `SequenceRNN.__init__`
   then calls `self.attachToGPUs(self.gpus)` unconditionally, and `SequenceRNN.attachToGPUs`
   hard-codes `torch.device(f'cuda:{gpus[0]}')`. There is no CLI flag asking for CPU; `-gpu`
   only takes GPU indices. The README states the basic sequential RNN should be usable on a
   suboptimal configuration. It is not.

I worked around defect 2 with a four-line monkeypatch in `scripts/sample_rnn.py` that leaves
the model on the CPU when the device is CPU, and drove the model through the Python API (the
path the package's own tutorial uses) instead of the CLI. `SequenceRNN.sample` and
`VocSmiles` are byte-identical from v3.4.0 through v3.4.8 (diffs in section 6), so the
version choice cannot move any number below. I used v3.4.4 (2023-05-15), the release
contemporaneous with the paper.

## 4. Results

Primary definitions, n = 100,000 raw sampled sequences per model, batch size 600, seed 1.

| model | metric | published | mine | difference | within 0.010? |
|---|---|---|---|---|---|
| ChEMBL 27 LSTM RNN | validity | 0.999 | 0.6856 | -0.313 | **no** |
| ChEMBL 27 LSTM RNN | uniqueness | 0.600 | 0.5718 | -0.028 | **no** |
| ChEMBL 31 GRU RNN | validity | 1.000 | 0.9140 | -0.086 | **no** |
| ChEMBL 31 GRU RNN | uniqueness | 0.996 | 0.9967 | +0.001 | yes |

### Verdict: partially reproduced, 1 of 4

One of the four in-scope numbers lands inside the pre-registered tolerance: the ChEMBL 31
GRU uniqueness. The other three miss, and both validity numbers miss by a wide margin, in
the paper's favour. Section 6 shows the misses are not mine.

## 5. Secondary definitions, on the same two samples

| model | definition | mine |
|---|---|---|
| ChEMBL 27 LSTM RNN | validity: valid / 100,000 (primary) | 0.68558 |
| ChEMBL 27 LSTM RNN | validity: multi-fragment SMILES allowed | 0.68558 |
| ChEMBL 27 LSTM RNN | validity: non-empty decoded string / 100,000 | 0.99916 |
| ChEMBL 27 LSTM RNN | uniqueness: distinct canonical / n_valid (primary) | 0.571779 |
| ChEMBL 27 LSTM RNN | uniqueness: distinct canonical / 100,000 | 0.392000 |
| ChEMBL 27 LSTM RNN | uniqueness: distinct raw strings / n_valid | 0.575542 |
| ChEMBL 27 LSTM RNN | uniqueness: distinct raw strings / 100,000 (post-hoc) | 0.661790 |
| ChEMBL 31 GRU RNN | validity: valid / 100,000 (primary) | 0.91398 |
| ChEMBL 31 GRU RNN | validity: multi-fragment SMILES allowed | 0.91398 |
| ChEMBL 31 GRU RNN | validity: non-empty decoded string / 100,000 | 1.00000 |
| ChEMBL 31 GRU RNN | uniqueness: distinct canonical / n_valid (primary) | 0.996652 |
| ChEMBL 31 GRU RNN | uniqueness: distinct canonical / 100,000 | 0.910920 |
| ChEMBL 31 GRU RNN | uniqueness: distinct raw strings / n_valid | 0.996783 |
| ChEMBL 31 GRU RNN | uniqueness: distinct raw strings / 100,000 (post-hoc) | 0.997060 |

Not a single reading of "validity" that counts molecules gets near 0.999 or 1.000. The only
definition that does is the non-empty-string fraction, and that is not what the legend says.
The "multi-fragment allowed" variant changes nothing, because these models essentially never
emit a `.`: validity is identical with and without that rule.

The two rows marked post-hoc were added after section 6 and were not pre-registered; they
are labelled as such here and in `scripts/extra_variants.py`.

## 6. Where the published numbers come from

Before concluding, I tested my own code against the authors' own data. The paper cites a
second deposit for exactly this table: Zenodo 10.5281/zenodo.7928362, *"Sampling timings and
molecules of DrugEx pretrained models"*, whose description states it is "the underlying data
of TableS4 and Figure S3". It holds the Table S4 spreadsheet (per-machine values from six
machines, plus the legend verbatim) and a per-molecule dump of 100,000 sampled SMILES per
model per machine carrying `Valid`, `Unique` and `Novel` flags.

My numbers agree with that dump to within the dump's own machine-to-machine spread:

| model | quantity | mine | authors' dump (M01) |
|---|---|---|---|
| ChEMBL 27 LSTM RNN | RDKit validity (valid / n) | 0.68558 | 0.68577 |
| ChEMBL 27 LSTM RNN | non-empty string fraction | 0.99916 | 0.99910 |
| ChEMBL 27 LSTM RNN | distinct canonical / n_valid | 0.571779 | 0.572466 |
| ChEMBL 27 LSTM RNN | distinct raw strings / n | 0.661790 | 0.664180 |
| ChEMBL 31 GRU RNN | RDKit validity (valid / n) | 0.91398 | 0.91401 |
| ChEMBL 31 GRU RNN | non-empty string fraction | 1.00000 | 1.00000 |
| ChEMBL 31 GRU RNN | distinct canonical / n_valid | 0.996652 | 0.996455 |
| ChEMBL 31 GRU RNN | distinct raw strings / n | 0.997060 | 0.996890 |

Validity agrees to 0.0002 and 0.00003. My sampling is not the problem: I reproduce the
authors' own per-molecule output. What disagrees is Table S4 itself, against the data the
authors deposited for it.

### The validity column of the RNN rows is not validity

In the dump, the fraction of sampled sequences RDKit can parse is 0.686 (ChEMBL 27 LSTM) and
0.914 (ChEMBL 31 GRU). Table S4 says 0.999 and 1.000. The published values are the fraction
of sampled sequences that decoded to a **non-empty string**, parseable or not:

| dataset / model | published | dump: non-empty / n, machines M01-M04 | dump: RDKit valid / n |
|---|---|---|---|
| ChEMBL 27 LSTM RNN | 0.999 | 0.99910, 0.99917, 0.99931, 0.99932 | 0.686 |
| ChEMBL 31 GRU RNN | 1.000 | 1.00000 (x4) | 0.914 |
| ChEMBL 31 LSTM RNN | 1.000 | 1.00000 (x4) | 0.962 |
| Papyrus 05.5 GRU RNN | 1.000 | 1.00000 (x4) | 0.915 |
| Papyrus 05.5 LSTM RNN | 1.000 | 1.00000 (x4) | 0.957 |

Twenty rows out of twenty, the lone 0.999 included, are explained exactly by the
non-empty-string fraction and by nothing else. My own ChEMBL 27 sample gives 0.99916, which
rounds to the published 0.999, while its real validity is 0.686. The legend's definition
("the ratio of molecular representations that make valid molecular structures") is not what
that column reports for the RNN rows. One note of caution: the transformer rows of the same
column do carry values below 1.000 (0.944 to 0.964 for the SMILES transformer), so the two
halves of the column appear not to have been computed the same way. The transformer rows are
out of scope here and I did not check them.

### The uniqueness column is the raw-string ratio, and the ChEMBL 27 row still misses it

The dump's `Unique` flag reproduces exactly as (distinct raw sampled strings) / (all 100,000
rows), invalid strings included:

- ChEMBL 31 GRU: 0.99689. Published 0.996. Match, and my own sample gives 0.99706.
- ChEMBL 27 LSTM: 0.66418, 0.66105, 0.66301, 0.66308 on M01-M04. Published 0.600. No match,
  and my own sample gives 0.66179 under the same rule.

So the one uniqueness number I could reproduce is the GRU one, and it reproduces under both
my primary definition (0.9967) and the authors' operational one (0.9971). The ChEMBL 27
uniqueness of 0.600 matches none of the candidates I could construct: 0.662 (authors' own
rule), 0.572 (distinct canonical over valid), 0.576 (distinct raw over valid), 0.392
(distinct canonical over 100,000). The published value sits between them and is reported as
0.599-0.601 across six machines, so it is not sampling noise either. That number I cannot
account for, and I am saying so rather than picking the nearest candidate.

### Falsifiers I had declared, and what they showed

- **Definitions.** All pre-registered variants plus the authors' own operational rule were
  tested (sections 5 and 6). None rescues validity; none produces 0.600.
- **DrugEx version.** `SequenceRNN.sample` and the whole `VocSmiles` class are byte-identical
  across v3.4.0, v3.4.4, v3.4.5 and v3.4.8 (`diff` of the released files). The version cannot
  move the result.
- **Authors' own output.** Cross-checked above; it matches me, not the table.
- **CPU vs GPU.** Sampling is multinomial draws from a softmax, so the distribution is
  device-independent, and the 0.0002 agreement with the authors' GPU-produced dump settles it
  empirically.
- **Truncation.** Only 51 of my 100,000 ChEMBL 27 sequences hit `max_len` without emitting
  EOS, and only 43 of the 31,442 invalid strings. The v2 ChEMBL 27 model simply emits 31%
  chemically invalid SMILES, many very short (10th percentile 11 tokens, 84 empty strings).
  See `logs/lstm_invalid_analysis.txt`.

## 7. What I could not check

- **The Supporting Information PDF itself.** `pubs.acs.org` serves an HTML interstitial in
  place of `ci3c00434_si_001.pdf`, and the EuropePMC `supplementaryFiles` endpoint for
  PMC10306259 returns only the article figures. I read the Table S4 values and the legend
  from the authors' own deposit for that table (Zenodo 10.5281/zenodo.7928362), which carries
  the legend verbatim and whose values match the ones I was asked to check. If the SI PDF
  differs from its own deposited source spreadsheet, I would not have seen it.
- **The transformer rows and the accuracy column.** Out of scope: the input fragment split
  was never published.
- **The relative sampling time column.** Out of scope: wall clock on the authors' GPUs. For
  the record, on 4 CPU threads of a workstation that was also running the user's own work I
  measured 7.24 ms/molecule for the ChEMBL 27 LSTM (724 s for 100,000) and 26.90 ms/molecule
  for the ChEMBL 31 GRU (2690 s). That ratio is the reverse of the published one (the paper
  has the GRU faster than the LSTM), but a loaded CPU is not a test of a dedicated GPU and I
  make no claim from it.
- **Run-to-run spread on my side.** One run of 100,000 per model, as pre-registered. The
  authors' six machines spread by 0.002 on uniqueness; the gaps I report are 0.03 to 0.31, so
  a second run would not change the verdict.

## 8. Defects found in the release

1. `drugex.generate` cannot run without QSPRPred, which is not a declared dependency, and
   the paper-era QSPRPred needs eight further undeclared packages and two backwards version
   pins before DrugEx's single import of it succeeds.
2. `SequenceRNN` cannot be constructed on a CPU-only host: `SequenceRNN.attachToGPUs`
   hard-codes `cuda:{gpus[0]}` and is called unconditionally from `__init__`, after the base
   class has already set `gpus = (-1,)` for CPU. Present in v3.4.4, unchanged in v3.4.8. No
   CLI option selects CPU.
3. Neither metric in Table S4 is computable from the default output of the released sampling
   command, because `generate()` resamples until it holds `num_samples` molecules that have
   already survived the invalid and duplicate filters. Measuring either one requires
   `--keep_invalid`, which the paper's description of the sampling run does not mention.
4. `drugex/generate.py` logs "Ignoring droping of duplicates because invalides are kept" when
   `--keep_invalid` is passed, yet still forwards `drop_duplicates=not args.keep_duplicates`
   to `generate()`. Harmless only because `drop_invalid=False` makes the whole filter block
   unreachable, but the warning and the argument it describes contradict each other.
5. Table S4's validity column, for all five RNN rows, reports the fraction of non-empty
   decoded strings, not the fraction that make valid molecular structures as the legend
   states. The real validities, from the authors' own deposited molecules, are 0.686 to
   0.962, not 0.999 to 1.000.
6. Table S4's uniqueness for ChEMBL 27 LSTM RNN (0.600, given as 0.599-0.601 across six
   machines) is not recoverable from the authors' own deposited molecules under any
   definition I could construct, including the one their own `Unique` flag implements
   (0.661-0.664).

## 9. Files

- `claims.json`, `claims.json.sha256` - the pre-registration and its hash.
- `scripts/sample_rnn.py` - CPU sampler, raw output, no filtering.
- `scripts/score_sample.py` - primary and pre-registered secondary metrics.
- `scripts/extra_variants.py` - the post-hoc variants of section 5.
- `scripts/authors_file_stats.py`, `scripts/authors_forensics.py` - recomputation from the
  authors' per-molecule deposit.
- `scripts/read_xlsx.py` - dump of the Table S4 spreadsheet.
- `scripts/probe_cpu.py` - the CPU construction failure, reduced to five lines.
- `scripts/run_full.sh` - the two production runs as they were launched.
- `runs/full_*.smi` - the two 100,000-molecule raw samples, each with `.meta.json`,
  `.scores.json` and `.extra.json` beside it.
- `runs/pilot_*.smi` - the 1,800-molecule pilots.
- `runs/cli_test/` - the attempt to run the released CLI.
- `logs/` - provenance and hashes, `pip freeze`, both CLI failure logs, the deposit
  recomputations, the invalidity analysis.
- `downloads/` - everything fetched from the network, kept apart from the scripts.
