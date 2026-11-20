# Adversarial review of the draft

Read `REPORT.md` against the files it cites, the authors' code at both tags, the paper's full
text, and Figure 4 fetched fresh. The accusation itself survives, and more cleanly than the
draft argues it. What does not survive is the precision the draft claims for its load-bearing
evidence, the independence it claims for its two runs, and one summary sentence in the Verdict.

Twelve findings. Three are blockers, six are fixes, three stand. A list of things the draft
could say and does not comes after them, before what the review could not settle.

## 1. "to about three decimals" is wrong, and it carries the whole case — blocker

Section 3, after the figure table: *"The violin printed as 'Young' carries the old group's
numbers, to about three decimals, and vice versa."*

Check the table's own rows. Blue at fractional occupancy state 4 is read as ~0.115, our old
group's **mean** is 0.1239. That is a 7% gap in the second decimal, not agreement in the third.
Switching rate: ~1.85 against 1.9676. And the mean-interval row compares a *centre* ("compact,
~1.3 and ~0.8") against a *tail extent* ("long tails to ~5.8 and ~4.3") and then sets both
beside group means of 1.47/0.99 and 2.07/1.49. Those are not the same quantity. A violin's
visible bulk is a KDE of the sample, its tails run past the data, and nothing in it is readable
to three decimals.

The fix is easy and it makes the match better, not worse. A split violin's bulge sits near the
median, so compare medians:

| starred cell | figure, blue "Young" | our old median | figure, orange "Old" | our young median |
|---|---|---|---|---|
| fractional occupancy, state 4 | ~0.115 | 0.1214 | ~0.155 | 0.1517 |
| switching rate, state 4 | ~1.85 | 1.8932 | ~2.4 | 2.4725 |
| mean interval, state 1 | ~1.3 | 1.3968 | tail to ~5.8 | max 5.152 |
| mean interval, state 8 | ~0.8 | 0.8395 | tail to ~4.3 | max 3.323 |

(medians recomputed here from `../2024-gohil-osl-dynamics-cego/runs/run01/sum_stats.npy`.)

Every centre lands within about 0.01 of our old group's median, and the orange tails sit just
past our young group's maxima, which is what a KDE does. Say that: the violin centres match our
old group's medians and the tails match our young group's range. Two decimals on a median, and
it is honest.

## 2. The two runs share a fit — blocker

The header says *"Two independent runs reached this, from the same public data and nothing else
in common."* Section 5 says *"No state in any of the four fits..."*. The cost line says *"the
blind trained three more"*.

`runs/out/train_seed01.json` gives free energy **110.20281682757752**. The blind run's
`runs/run01/free_energy.npy` gives **110.20281683**, and its copes match ours to every printed
digit: fractional occupancy state 4 cope +3.17262132e-02 in both. Both scripts call
`tf.keras.utils.set_random_seed(1)` — ours inside `scripts/03_train.py`, the blind run's inside
`run_hmm.py` — and TensorFlow handed them the same model. So there are **three distinct fits in
this project, not four**, our only fit is the blind run's run01, and the blind run trained two
new ones, not three.

This does not touch the finding: runs 02 and 03 are genuinely different draws and agree. But the
independence is in the protocol and in the reading, not in the model, and the draft has to say
so in those words. As written, a reader who checks the free energies will think we hid it.

Secondary, and worth keeping: `scripts/03_train.py` goes through `run_pipeline`, `run_hmm.py`
builds the `Config` by hand. Two code paths, one bit-identical answer. That is the real value of
the duplicate and it is currently going unused.

## 3. "The same states come out significant, at the same metrics" — blocker

Verdict, first paragraph. It is true for three cells of five and false for two, and the draft's
own section 2 says so four paragraphs later. It is also incomplete in the other direction: the
published Figure 4BI carries **five stars** (FO 4, LT 6, MI 1, MI 8, SR 4) and our fit has **six
significant cells** — `runs/out/stats_seed01.json` puts switching rate at state 3 at
p = 0.047 / 0.053 / 0.044, which the figure does not star.

The Verdict needs the honest version: the two cells the paper calls sensorimotor and visual come
out significant at the same metric and the same index with the sign inverted; the two
mean-interval cells come out at different indices, which is expected; and one extra
switching-rate cell appears that the figure does not have.

## 4. The p-values do not agree to the third decimal — fix

Section 2: *"every test was run three times; the three agree to the third decimal everywhere
below."* The table printed immediately under that sentence has 0.029 / 0.026 / 0.022 and
0.833 / 0.789 / 0.817. The copes agree exactly, because they are deterministic. The p-values
spread by up to 0.044. Say what is true: all three land on the same side of 0.05 in every cell,
which is what the frozen rule asks for.

## 5. The DyNeMo cost is understated by about 40% — fix

Section 5: *"~25 min/epoch x 40 epochs = 16 h per run on CPU."*

`../2024-gohil-osl-dynamics-cego/dynemo_throughput.txt` holds the only measurement:

```
Epoch 1/40:  10%|9  | 18/189 [03:23<30:12, loss=113.2, kl=0, ll=113.2]
```

203 s for 19 batches is 10.7 s per batch; 189 batches is **2020 s, about 34 min per epoch**, and
tqdm's own ETA on that line says 3:23 + 30:12, which is the same 34 min. Forty epochs is **about
22 h**, not 16. The blind report has the same slip ("about 11 s per batch, about 25 minutes per
epoch") and the draft inherited it. The conclusion gets stronger, not weaker.

## 6. Section 2.5 is argued against the wrong sentence — fix

The draft quotes *"This is a complementary explanation for the increase in static beta-power ...
as a larger contribution from the sensorimotor network"* and then argues about the HMM's
fractional occupancy. That sentence is about **DyNeMo mode 4**, not the HMM. The sentence the
argument actually needs sits one line earlier in the same paragraph:

> Looking at the dynamic network perspective provided by the TDE-HMM, we see an increase in the
> fractional occupancy of state 4 (Figure 4BI) ... the increase in static beta-power and
> connectivity with age can be linked to a larger fraction of time spent in the sensorimotor
> network.

That is the claim r = +0.43 against r = −0.38 contradicts, and it names Figure 4BI, the figure
with the swapped legend. Swap the quote.

## 7. The code comment does not say what the draft says it says — fix

Section 3: *"Its own comment says so: **1 is young, 2 is old**."* The comment reads:

```python
    # Subjects with age > 34 are assigned to the old group
    # and age <= 34 are assigned to the young group
```

It states the rule, not the numbering. The numbering follows from `assignments = np.ones_like(age)`
plus `assignments[i] += 1`, which the draft should spell out rather than put words in a comment.
Same paragraph: "`load_group_assignments`, eleven lines above" — the function is defined at line
30 of the v2.0.0 file and the swap is at line 48, eighteen lines below it. The `+= 1` is the
thing eleven lines above. Write the line numbers.

## 8. The discarded deposited-model control should be named — fix

Section 5 says *"no check that depends on it was used as evidence here."* True, and the stated
reason is good. But the check was **run**, and its outputs sit in
`../2024-gohil-osl-dynamics-cego/runs/deposit12/`. Recomputed here: the deposited 12-state model,
applied to a re-derived PCA basis, puts its most sensorimotor state at fractional occupancy
young 0.0956 vs old 0.0940, p = 1.000, r(age) = −0.07, and its only two significant cells are
mean lifetimes with no sensorimotor character. Its mean lifetimes are ~36 ms, well under the
paper's own 50–100 ms, which is independent evidence the model is scrambled in that basis and
that the exclusion is right.

Say it that way. "We ran it, it came out null, and here is why the null is an artefact of the
rotation" is a stronger position than "we did not use it", which reads like a buried result.

## 9. Which PCA the subspace was compared to — fix

Section 5 says re-deriving the PCA *"recovers the subspace almost exactly"* without saying
against what. `deposit_model_check.py` line 48 compares against
`deposit/tde_dynemo_20_runs/pca_components.npy` — a **different model's** deposited basis, used
as a proxy because the HMM archive carries none. That is a reasonable proxy and the draft should
say it is one. The numbers themselves (60 of 80 cosines above 0.99, median 0.15) go to stdout and
were saved nowhere, so this review could not re-verify them; see the last section.

## 10. The code reading — stands, and is tighter than the draft knows

Checked both files at both tags, fetched from `raw.githubusercontent.com`:

- v2.0.0 `ctf_rest/tde_hmm_networks.py` line 48 and `main` line 50:
  `group = ["Old" if a == 1 else "Young" for a in assignments]`. The identical line is at
  v2.0.0 `tde_dynemo_networks.py` line 46.
- The numeric `assignments` go to `group_diff_max_stat_perm` (v2.0.0) and to `stats.group_diff`
  (main). `group` goes only to `plotting.plot_summary_stats_group_diff`.
- That function, read in full at both tags, puts `assignments` into a `"Group"` column and hands
  it to `sns.violinplot(..., hue="Group", split=True)`. It sorts nothing, reorders nothing,
  remaps nothing. The stars come from `pvalues`, the heights from `summary_stats`. The only
  difference between the two tags is a `TestResult` unwrap and type hints.
- `stats.group_diff` defaults to `correction="max_stat"` with `pooled_dims=None`, documented as
  "all of them, i.e. the FWER is controlled across every target". So "max-statistic over states
  and metrics" is right, and the Figure 4 caption uses those same words.

One thing the draft does not check and should: seaborn orders a string hue by **first
appearance**, not alphabetically. `subject00` is 39 years old, so it is assigned 2, so the
swapped line labels it "Young", so "Young" is hue level 0, so it is blue and it is the left half.
That is exactly the legend the published figure shows. The legend order is not a coincidence we
observed — it is derivable from the code and one row of `demographics.csv`.

## 11. The figure reading — stands, and one more cell fits

Downloaded `fig4-v1.tif` at 2400 px from the eLife IIIF endpoint, 537 kB. (Note the blind run's
`figs/fig4.jpg` is a 5,570-byte Cloudflare challenge page; its `figs/f4.jpg` is the real one.)

- The legend reads **Young = blue, Old = orange**, in that order. Confirmed by eye.
- Stars: FO state 4; LT state 6; MI states 1 and 8; SR state 4. Five cells across four panels,
  all single, and the legend defines a single star as p < 0.05.
- FO state 4: orange clearly above blue. SR state 4: orange clearly above blue. Both as the
  draft says.
- **Mean lifetime state 6, which the draft's table leaves out, also fits.** Blue sits at about
  0.067 and orange at about 0.057. Our old group's lifetime is 0.0672 and our young group's is
  0.0602. Blue carries the old numbers again. Put the row in; it is a free third cell and the
  only one where the inverted direction points downward, so it rules out a reading where orange
  is simply "the bigger half".
- Mean interval: blue compact at both starred states, orange with the long tail. Our young group
  is the wider one, sd ratios 0.42 and 0.62 in blind run03. Consistent.

Also worth quoting, and the draft does not: the Figure 4 caption names the script itself.

> The script used to generate the results in this figure is here:
> https://github.com/OHBA-analysis/osl-dynamics/blob/main/examples/toolbox_paper/ctf_rest/tde_hmm_networks.py

The paper points at the file that carries the swapped line. That is the single strongest sentence
available and it belongs in section 3.

## 12. The static-beta control — stands, and the paper corroborates it itself

Recomputed from `../2024-gohil-osl-dynamics-cego/static_beta_sm.npy` against
`training_data/demographics.csv`: young 0.1428, old 0.1815, t = 3.501, p = 0.000858, Pearson r
with age = +0.4332, p = 0.000313. Every figure in the draft reproduces. The matching
fractional-occupancy correlation is r = −0.3812 (p = 0.0017) in our fit and −0.3910 in blind
run03, so the draft's "−0.38" is right.

Does the control do what it claims? Yes, and for a reason the draft does not spell out: a
misalignment between `demographics.csv` and the file order would **destroy** this effect, not
reverse it, so p = 0.0009 in the expected direction is evidence the assignment vector is aligned
with the data — which is the one way the inversion could have been ours. The group means in
section 2 are computed from `assignments == 2` directly, not from `group_diff`'s contrast, so the
table's direction does not depend on the contrast convention either. Both facts are worth a
sentence each.

And the paper corroborates the control **inside itself**, which the draft misses. The static
script, `ctf_rest/static_networks.py`, codes the groups the other way round:

```python
# Get group assignments (old = 1, young = 2)
...
    if a < 34:
        assignments[i] += 1
...
pow_diff = result.copes  # pow_diff is group 1 (old) minus group 2 (young)
```

So Figure 6's contrast really is old minus young, and the text reports *"a significant reduction
in temporal delta-power and an increase in sensorimotor beta-power"*. The authors' own
correctly-oriented analysis puts beta rising with age, exactly where our control puts it. That is
better evidence than "the well-known ageing effect" — though the outside literature does back the
phrase for sensorimotor beta over this span (Rossiter 2014 and the Cam-CAN work; the full-lifespan
picture is non-linear, so do not generalise past 21–60).

Two of their own scripts define group 1 oppositely. That is the kind of thing that produces a
swap, and it is worth one line.

## Under-claims: four things the draft could say and does not

1. **The state index is checkable, so stop having it both ways.** Recomputing the blind run's
   `label_states` from `runs/run01/state_psd.npy`: state 4 is sensorimotor beta (ROI excess
   +0.081, peak 19 Hz), state 6 is visual (+0.084), state 3 is the highest-power state and state
   2 the lowest-power, i.e. suppressed. So in our fit the sensorimotor-beta state really does
   carry index 4 and a visual state index 6, which is why three cells line up by index. The draft
   calls numbering arbitrary for the mean-interval cells and meaningful for the others, and it
   does not need to: rest everything on the anatomy, which holds in all three fits, and the index
   match becomes a coincidence worth one line instead of a load-bearing claim.

2. **Figure 5 is readable the same way.** `tde_dynemo_networks.py` carries the same swapped line,
   the first subject is the same, and Figure 5BI shows the same legend with Young first. At the
   double-starred mode 4 of the Mean panel the orange half sits above the blue; at the
   double-starred mode 5 of the Standard Deviation panel orange sits below. So both DyNeMo
   direction claims in section 2.4 rest on the same swapped legend as the HMM ones. Their numbers
   still cannot be checked, but "the DyNeMo claims cannot be checked at all" is too absolute — the
   *mechanism* reaches them, and that can be said without one epoch of training.

3. **The paper claims agreement with prior work on the inverted directions.** The sentence right
   after the four claims reads *"The age-related differences we observe here are consistent with
   existing studies (Coquelet et al., 2020)."* Under the swap that sentence is attached to the
   wrong set of directions.

4. **Everything checkable in the draft checks out.** Every number in the section 2 table matches
   `runs/out/stats_seed01.json` cell for cell — 0.1556 / 0.1239 / +0.0317 and p 0.028971,
   0.025974, 0.021978 for FO state 4, and likewise for the other four rows. Group sizes, the seven
   banded ages, 271–305 s recordings, 8 of 8 lifetimes inside 50–100 ms, free energies 110.2028 /
   110.2020 / 110.2018, 1802 s, (20, 6, 80, 80) for the DyNeMo covariances, `n_states: 12` and
   `# osl-dynamics version: 2.0.dev3` inside `trained_tde_hmm.zip`, `alp.pkl` alone in the
   5-subject archive, the Europe PMC quotes word for word, `claims.json` hashing to `e1df8bd2…`
   and the blind pre-registration to `ed8343e5…`. Nothing was invented. Worth knowing after the
   DES review, where something was.

## What the review could not settle

**Whether the published figure was made by exactly this script.** The caption names the file, the
legend is what the file produces down to the hue order, the group sizes match, the panel values
match our fit with the names exchanged, and the deposited model says 2.0.dev3 while the line is
present at v2.0.0. That is as close as inference gets, but the alternative — that they plotted a
corrected version and our fit happens to put young and old the other way round from theirs on
every starred cell at once — cannot be formally excluded. Write "consistent with", not "produced
by".

**Version drift.** The figures came out of 2.0.dev3. Both our runs used osl-dynamics 3.8.2 with
TensorFlow 2.19.1, and the published call `group_diff_max_stat_perm` has since become
`stats.group_diff`. Nobody checked that 3.8.2's preparation and training are numerically what
2.0.dev3's were. Our fit landing on the paper's own eight networks, at the paper's own indices,
suggests the drift is small, but it is unmeasured.

**The PCA principal angles.** `deposit_model_check.py` prints them and saves nothing, so the
"60 of 80 cosines above 0.99, median per-component 0.15" figures could not be re-verified here.
The conclusion they support is independently backed by the 36 ms lifetimes in finding 8, so the
report does not hang on them — one `np.save` would close it.

**That the blind run was blind.** `FREEZE.txt` is timestamped 08:34:45 local and the first
computation starts at 08:46, so the pre-registration is genuinely prior to the work. Whether its
author had seen the first run is a procedural claim no artefact can settle. The duplicate seed in
finding 2 is at least consistent with two people independently reaching for `seed = 1`.

## Standing at the end of the review

The accusation holds. The swapped line is in both scripts at both tags, it reaches the legend and
only the legend, the legend in the published figure is what that line produces, the violins under
each name carry the other group's numbers, and a model-free control plus the authors' own static
analysis both put the older group where we put it. Three phrasings in the Verdict have to come
down a notch and one quote has to be replaced. The finding underneath does not move.
