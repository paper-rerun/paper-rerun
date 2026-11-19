# nellie — segmentation benchmark, Extended Data Fig. 2a/b

- Paper: Lefebvre, A.E.Y.T. et al. *Nellie: automated organelle segmentation, tracking and hierarchical feature extraction in 2D/3D live-cell microscopy.* Nature Methods (2025). The published values come from the article's Source Data, Supplementary Data 16; the article itself is the publisher's and is not redistributed here.
- Data: none deposited. The benchmark is written by the authors' own `multi_grid.py`, 9.9 GB, no RNG seed — see `data/README.txt`.
- Code: `aelefebv/nellie` 0.4.1 from PyPI and `aelefebv/nellie-supplemental` at `7a639bca9b426a1addbf358fe8fffb389949b30d`, both unmodified. Scoring is their `check_IoU`, imported rather than reimplemented.
- Target: the eight values frozen in `claims.json` — Nellie F1 and IoU at σ = 8, 1024, 8192 and 32768.
- Verdict: **Partially reproduced** — 6 of 8 inside the frozen band on the slice the figure exports. Nine defects in the benchmark, two of which change the published comparison.
- Date: 2026-11-18
- Hardware: Ryzen 9 3900X, 64 GB, native Windows, CPU only, one process per level under `nice -n 19`. The GPU was not touched.
- Wall clock: 2 h 03 min of segmentation across the three timed levels (25, 30 and 68 min), a fourth level timed before the timings file existed, and 83 min more in the Hierarchy stage that died. Published folder 326 KB; what it regenerates is the 9.9 GB benchmark plus about 5.5 GB of intermediates per level, and none of that is in the repository.

Frozen claims: `claims.json`, SHA-256
`68617898061165b7c1725f17de8207fdcbe54aaa01cafb2552fddc781c4664a4`, frozen before the
benchmark was generated. `REVIEW.md` is an adversarial review of a first draft of this
report; `blind/` is an independent run that never saw any of it. Both found real errors in
that draft, including one that invalidated its whole comparison table. What they caught is
listed at the end.

## What this run is

The figure plots F1 and IoU against Gaussian noise for Nellie and four other methods, over
a simulated volume the repository regenerates. We regenerated it with the authors'
unmodified `multi_grid.py`, segmented four of the thirteen noise levels with Nellie 0.4.1,
and scored them with the authors' own `check_IoU`. So this checks the whole path: generate,
segment, measure, summarise.

The summarising step is where almost everything we found lives.

## Verdict against the frozen rule

| level | metric | ours (lv5 slice) | published | delta | band | |
|---|---|---|---|---|---|---|
| 8 | F1 | 0.9800 | 1.0000 ± 0.0000 | −0.0200 | 0.0100 | **fails** |
| 8 | IoU | 0.7329 | 0.7341 ± 0.1869 | −0.0011 | 0.1869 | ok |
| 1024 | F1 | 0.9815 | 0.9810 ± 0.1335 | +0.0006 | 0.1335 | ok |
| 1024 | IoU | 0.7652 | 0.7704 ± 0.1631 | −0.0052 | 0.1631 | ok |
| 8192 | F1 | 0.7946 | 0.8036 ± 0.3650 | −0.0091 | 0.3650 | ok |
| 8192 | IoU | 0.6096 | 0.6199 ± 0.2987 | −0.0103 | 0.2987 | ok |
| 32768 | F1 | 0.3624 | 0.1300 ± 0.1135 | +0.2324 | 0.1135 | **fails** |
| 32768 | IoU | 0.4045 | 0.3131 ± 0.2966 | +0.0913 | 0.2966 | ok |

Six of eight inside the band, two outside. Read it as a summary and the run looks fine with
two outliers; read finding 1 and six of those passes are against a bar that is 50 to 600
times too wide.

The frozen self-check passed: the noiseless volume has exactly 1000 connected components.

**The population matters and we had it wrong at first.** The exported files are named
`lv5`, and `visualize.py` reduces with `stats[...][:, level, :]` — one 10×10 slice of the
grid, 100 cells, at index 5 of axis 1. Our first draft averaged all 1000 cells. The slice
is closer to print on all eight pairs, and on the IoU rows it is not close: −0.0011 against
−0.0324 at σ = 8, −0.0052 against −0.0393 at 1024 (`runs/logs/verify_review.log`). The
table above is the slice.

## Finding 1 — N = 10 cannot be the N those numbers were computed over

Every row of both files carries **N = 10**. F1 and IoU are bounded in [0, 1], so for ten
values with a given mean there is a largest achievable sd: pile them at the ends. Three F1
rows print an sd above that ceiling (`runs/logs/verify_review.log`):

| noise | mean | printed sd | ceiling at n=10 | ceiling at n=100 |
|---|---|---|---|---|
| 1024 | 0.9809523810 | 0.1335032930 | 0.057143 | 0.133503 |
| 2048 | 0.9466666667 | 0.2196967607 | 0.160000 | 0.219697 |
| 4096 | 0.9475000000 | 0.2129994131 | 0.157500 | 0.218789 |

This needs no model of the pipeline. Ten numbers in [0, 1] averaging 0.98098 cannot have an
sd of 0.1335. All three sit under the n = 100 ceiling, and two reconstruct exactly as 100
cells, to the tenth decimal the files are printed to
(`runs/logs/reconstruction.log`):

- σ = 1024: 98 cells scoring 1, one scoring 2/21, one scoring 0 (residual 5e−11)
- σ = 2048: 94 cells scoring 1, one scoring 2/3, five scoring 0 (residual 3e−11)

2/21 and 2/3 are not arbitrary numbers. Per-cell F1 in `check_IoU` can only ever be 0 or
2/(2+fp), so those are single cells with 19 and with 1 false positive. The composition is
the code's own arithmetic, read back out of the printed summary.

So mean and sd are over the 100 cells of the slice, and our own per-cell sd over that same
slice agrees (`runs/logs/slice_spread.log`):

| level | metric | our sd over the 100 cells | printed sd | ratio |
|---|---|---|---|---|
| 8 | IoU | 0.1913 | 0.1869 | 1.02 |
| 1024 | F1 | 0.1297 | 0.1335 | 0.97 |
| 1024 | IoU | 0.1668 | 0.1631 | 1.02 |
| 8192 | F1 | 0.3940 | 0.3650 | 1.08 |
| 8192 | IoU | 0.3116 | 0.2987 | 1.04 |
| 32768 | IoU | 0.3418 | 0.2966 | 1.15 |
| 32768 | F1 | 0.3459 | 0.1135 | 3.05 |

Six of seven within 8%. The one that misses is σ = 32768 F1, which is also the row where
our mean disagrees — finding 7.

**What the bar is, and what it is not.** The 100 cells of a slice are 100 different
simulated objects in one frame of one noise draw: the grid sweeps thickness and brightness
across them by construction. So the bar is object heterogeneity. For comparison,
`multi_grid.py` writes three timepoints per file, each an independent unseeded draw over
the same clean volume — and `FileInfo.select_temporal_range` takes an *inclusive* end
(`t_end` defaults to `shape − 1`), so the authors' own recipe, `(0, 1)`, already segments
two of them and `analysis.py` discards the second at `[0]`. The second draw was in files we
had already written, so this cost no segmentation:

| level | metric | draw 0 | draw 1 | spread | printed sd |
|---|---|---|---|---|---|
| 8 | IoU | 0.7329 | 0.7334 | 0.0003 | 0.1869 |
| 1024 | F1 | 0.9815 | 0.9831 | 0.0011 | 0.1335 |
| 1024 | IoU | 0.7652 | 0.7691 | 0.0028 | 0.1631 |
| 8192 | F1 | 0.7946 | 0.7845 | 0.0071 | 0.3650 |
| 8192 | IoU | 0.6096 | 0.6063 | 0.0023 | 0.2987 |
| 32768 | F1 | 0.3624 | 0.3980 | 0.0252 | 0.1135 |
| 32768 | IoU | 0.4045 | 0.4064 | 0.0014 | 0.2966 |

The printed bar is 4.5× to 623× that spread. **This is n = 2**, one degree of freedom, and
we are not calling it an sd estimate — two draws bound the spread loosely, and at σ = 32768
F1 the factor of 4.5 is within what two points can produce by luck. On the other six the
gap is 50-fold or more and n = 2 is enough to see it.

It matters because of how the figure reads. Wide overlapping bars say "these methods are
hard to tell apart at this noise level". They are wide because the benchmark holds both
easy and hard objects, which is equally true of every method plotted and says nothing about
how well any of them is pinned down. And if the bar is divided by √10 for a confidence
interval, as N = 10 invites, the arithmetic breaks: 0.9810 + 1.96 × 0.1335/√10 = 1.064,
above the maximum F1 can take.

## Finding 2 — a cost guard zeroes an entire competitor row

In `check_IoU`:

```python
unique_labels = np.unique(label_partial)
if len(unique_labels) < 100:  # skip this, it's bad
    for label in unique_labels:
        ...
```

When a cell holds 100 or more labels the matching loop is skipped, `tp_label` stays `None`,
and the cell scores F1 = 0 and max_iou = 0 — even when one of those labels is an exact copy
of the ground-truth object. We built that case: at 50 extra labels the cell scores max_iou
1.000, at 120 it scores 0.000, with the same perfect match present both times
(`scripts/06_checkiou_probes.py`).

The comment says what it is: a guard against an O(labels) loop with an `argwhere` inside.
But it is in the scoring path, and it fires asymmetrically. Counting labels per cell the way
`check_IoU` counts them (`runs/logs/verify_shortcut.log`):

| method | σ=8 | σ=1024 | σ=8192 | σ=32768 |
|---|---|---|---|---|
| Nellie, max labels in a cell | 18 | 51 | 52 | 63 |
| Nellie, cells ≥ 100 | 0 | 0 | 0 | 0 |
| Otsu, cells ≥ 100 | 0 | 0 | 0 | 0 |
| Triangle, cells ≥ 100 | 0 | 0 | **1000** | 27 |

Nellie never reaches the guard, at any level we ran. Triangle at σ = 8192 reaches it in
**every one of the 1000 cells**, with up to 1113 labels in a single cell — and the published
Triangle row at σ = 8192 is exactly 0.0000 ± 0.0000 for both metrics. The whole row is the
guard, not a measurement.

The fingerprint shows again one level up. Published Triangle IoU runs 0.0000 at σ = 2048,
4096, 8192 and 16384, then **rises to 0.0396 at σ = 32768** — better scoring at more noise,
which nothing physical explains. At σ = 32768 only 27 of 1000 cells trip the guard. The
bump is the guard switching off.

We did not segment σ = 2048, 4096 or 16384, so for those rows we have the published zeros
and no label counts, and we are not claiming them. Otsu is a useful control the other way:
it never trips the guard at any level we ran, so its published zeros at σ = 16384 and 32768
are genuine failures, not artifacts.

The mechanism is not inferred — we reproduced both rows. Scoring the baselines on the same
slice (`runs/logs/baseline_slice.log`) returns Triangle IoU 0.0000 at σ = 8192 against
0.0000 printed, and 0.0396 at σ = 32768 against 0.0396 printed, to four decimals. So the
zero and the bump that follows it are both ours too, and the label counts above say why.

This is one-directional. The method under evaluation never meets the guard; a baseline it is
being compared against has a row produced entirely by it.

## Finding 3 — fp goes negative, scoring a correct match zero

Also in `check_IoU`:

```python
fp = len(unique_labels[unique_labels != tp_label])-1  # -1 to account for 0 label
```

The −1 removes the background label, assuming it is in the crop. When one label fills the
crop, it is not, so fp = −1, `tp + fp == 0`, the guard below sets precision = 0, and F1 = 0
for a correct match. Measured through the authors' unmodified function
(`runs/logs/verify_defects.log`): one label placed exactly on the object scores F1 1.0000;
the same label extended to fill the crop scores F1 0.0000 with max_iou 0.3554.

Like finding 2 this can only hurt a method that saturates — a threshold baseline at high
noise. It cannot hurt Nellie, whose branch labels never fill a cell.

## Finding 4 — the level axis is labelled with the wrong variable

`multi_grid.py` places thickness on axis 0, length on axis 1 and intensity on axis 2.
Measured from the clean volume (`runs/logs/verify_defects.log`): per-cell peak intensity is
flat along axes 0 and 1 and runs 6553 → 58982 along axis 2, matching the generator's
`intensity_vector`; voxel count is constant along axis 2 and varies along the other two.

`check_IoU` indexes `[thickness, intensity, length]`, and `visualize.py` slices
`[:, level, :]` calling it an intensity level. Axis 1 is length. So the exported `lv5`
series is a fixed **length**, not a fixed intensity, and a figure or caption describing the
points as intensity values names the wrong variable. The numbers are unaffected; the label
is wrong. Our own `claims.json` repeated the authors' naming and called the frozen primary
reduction a spread across brightness. That was wrong too, for the same reason.

## Finding 5 — the release cannot reproduce this figure

Three gaps, each independent:

- **No script runs Nellie on these simulations.** `comparisons/segmentation_comparisons/`
  holds `mitograph_batch.py`, `mitograph_runtime.py`, `mitometer.py`,
  `mitometer_runtime.py` and `otsu_triangle_only.py` — one per competing method, none for
  Nellie. The recipe we used came from a commented-out block at the bottom of
  `nellie/run.py` in the main package. Nellie's parameters for this figure are not in the
  release.
- **No seed anywhere.** `multi_grid.py` calls `add_noise` three times per level with no RNG
  seed, so the exact volumes behind the figure cannot be regenerated.
- **The two pin sets contradict each other.** The supplemental's `requirements.txt` pins 139
  packages including `scikit-image==0.23.1` and `scipy==1.13.0`. Nellie 0.4.1's own metadata
  *requires* `scikit-image==0.22.0` and `scipy==1.12.0`, as hard `==` pins. Both cannot hold.
  pip resolved ours in nellie's favour, so we ran skimage 0.22.0 against a file pinning
  0.23.1. Nellie itself appears in neither pin list.

That last one is sharper than "the version under test is unpinned". The frozen environment
and the software it evaluates are mutually unsatisfiable, so no installation satisfies the
release as published, and which combination produced the figure is unrecoverable.

## Finding 6 — the noise axis is half-normal plus a background ramp

`utils.add_noise` does `frame += np.clip(normal_noise, 0, 65535)` — the clip is on the
noise, not on the noisy frame. The negative half of the Gaussian is removed before adding,
so "Gaussian std σ" is a positive-only draw whose mean is σ/√(2π). Measured
(`runs/logs/verify_defects.log`):

| nominal σ | added mean | σ/√(2π) | added sd |
|---|---|---|---|
| 256 | 103.0 | 102.1 | 151.0 |
| 8192 | 3278.3 | 3268.1 | 4795.6 |
| 32768 | 12715.9 | 13072.5 | 18104.3 |

The added mean tracks σ/√(2π) to about 3%. So the x axis sweeps background level and noise
together, and the effective sd is about 0.58σ. Every method in the plot sees the same
volumes, so the comparison is unaffected; the axis label is what overstates.

## Finding 7 — at the highest noise level we score 2.8× the published F1, and it is not the noise draw

Published F1 at σ = 32768 is 0.1300. We get 0.3624 and 0.3980 on the two draws. A failed
reproduction normally cannot reach the published number; we are overshooting by 0.23.

The unseeded noise is the obvious suspect and does not cover it: two draws move the number
by 0.025, and the gap to print is nine times that. The measurement is the authors' own
`check_IoU`, called as `analysis.py` calls it, and findings 2 and 3 both run against
Nellie's favour here rather than for it. That leaves the segmenter, and finding 5 is why we
cannot say which version or which parameters.

The published row is also the only one where F1 (0.1300) falls below IoU (0.3131); every
other level has F1 above. Per-cell F1 collapses when a cell fills with spurious labels, so
that inversion is the signature of heavier over-segmentation than ours — consistent with a
different version, and not evidence for one.

## Finding 8 — seven consecutive levels print a perfect score

Published F1 is exactly 1.0000 ± 0.0000 at σ = 8, 16, 32, 64, 128, 256 and 512 — seven
levels with not one object missed or split. On the lv5 slice we get 0.9800 on both draws, so
2 of 100 cells fail for us; over the whole grid, 26 of 1000 are imperfect.

A perfect row means no cell anywhere held a spurious label at that noise level. Published
IoU at those levels is about 0.74, so objects were found and matched at 74% overlap — self
consistent, and we are not claiming the row is wrong. We cannot reproduce it, and finding 5
is why we cannot say whether that is the version or us.

## Finding 9 — one defect that turns out not to matter

`check_IoU` gates candidate labels with
`np.sum(np.isin(gt_partial_coords, label_coords).all(axis=1)) == 0`. `np.isin` is
elementwise over the whole array, not a row lookup, so a coordinate passes when each of its
three numbers appears anywhere in `label_coords`, in any column, from any row: `[1, 2, 3]`
against `[[3, 1, 9], [7, 2, 8]]` shares no row and is counted as overlapping
(`scripts/06_checkiou_probes.py`).

It cannot change any score. The broken gate is only ever too permissive, an added label's
true intersection with the object is zero so `iou > max_iou` is never satisfied, and `fp`
counts every label without consulting the gate. It is a cost bug. A first draft of this
report said the `max_iou < 0.1` floor was what kept it harmless; that was the wrong reason,
and the review caught it.

## The benchmark geometry

Five of the ten length levels are degenerate. `create_skeleton_sub_volume` clips its
sinusoid with `np.clip(y, 0, length-1)` rather than against the 50-voxel cell, so for short
lengths the filament collapses to a straight rod in the low corner. Measured curvature span
by level (`runs/logs/verify_shortcut.log`): 0 voxels at levels 0–4, then 3, 7, 10, 10, 10.

The exported series is lv5, which is the first non-degenerate level and barely so — 3 voxels
of curvature against 10 at the top. So the published panel is close to the straight-rod end
of the sweep without being in it. A blind run of this paper reported lv5 as degenerate; it
is not, and we checked every level rather than take that.

## Everything the release let us check

- The clean volume regenerates from `multi_grid.py` with exactly 1000 components, matching
  the frozen gate.
- The reference numbers come from the Supplementary Data (MOESM16), read from the
  tab-separated files, not from the figure image.
- **Otsu and Triangle reproduce print to four decimals**, which is the control that makes
  finding 7 attributable. They ran from the authors' `otsu_triangle_only.py`, imported
  rather than reimplemented, and share the regenerated volume, the ground truth, the noise
  draw and `check_IoU` with our Nellie run. On the lv5 slice, 14 of 16 numbers land within
  0.0027 of print and 8 of them are exact at four decimals: Otsu F1 0.7800 against 0.7800 at
  σ = 8 and 1024, Otsu IoU 0.6296/0.6301/0.6127/0.0369 against 0.6294/0.6303/0.6117/0.0370,
  Triangle F1 1.0000 against 1.0000 at σ = 8. The one real miss is Otsu F1 at σ = 8192,
  0.7290 against 0.7483. So everything upstream of the segmenter is sound, and the Nellie
  gaps in findings 7 and 8 cannot be put on the volume, the noise, the ground truth or the
  scoring (`runs/logs/baseline_slice.log`).
- The pipeline stop after `Network` is safe: `analysis.py` reads only
  `*skel_relabelled.ome.tif[0]`, only `networking.py` writes that file, and `Hierarchy` and
  `VoxelReassigner` open it `r+` but write elsewhere. Verified by the review.

## Where the run departed from the frozen route

- **Four of thirteen levels**, chosen in `claims.json` before the benchmark existed, to span
  the curve. The nine others are dropped for cost — 25 to 68 minutes of segmentation each.
- **The pipeline stops after `Network`.** `Hierarchy`, the feature-extraction stage, did not
  complete: on the first level it ran 83 minutes past segmentation and died allocating
  8.67 GiB for a 19697 × 19697 × 3 array in `_get_branch_stats`
  (`runs/logs/hierarchy_oom.log`). It produces nothing the frozen claims use. Reported, not
  worked around.
- **σ = 8 was segmented differently from the rest.** It went through the full `run()` before
  the OOM; the other three ran Filter → Label → Network directly. Same stages up to the file
  that is scored, so no number changes, but it is not an identical invocation.
- **Memory forced one level per process.** Nellie does not release its 510³ volumes between
  levels inside a process; σ = 8192 died asking for 127 MiB, which is exhaustion rather than
  a large request.
- **The frozen band is badly sized**, for the reason finding 1 gives: it is built on a
  published sd that measures object heterogeneity. We report the verdict as frozen anyway,
  because resizing a rule after seeing the data turns a recount into an argument. A band
  built on the replicate spread would fail most of these rows.
- **One wasted step.** `scripts/05_timepoints.py` looked for an output tagged `t1_to_2` and,
  not finding one, tried to segment the second timepoint from scratch — it was already in
  the `t0_to_1` file, because `t_end` is inclusive. About 20 minutes of CPU, no number
  affected. `scripts/07_replicate_spread.py` replaced it.

## What the review and the blind run caught in the first draft

Listed because the errors were ours and two of them were material:

- **The population.** The draft compared against all 1000 cells; the published row is the
  100-cell lv5 slice. Every delta in the verdict table was wrong, some by 30×.
- **The reduction scan.** The draft said it had scanned every candidate and that nothing in
  the released code produced the published reduction. `visualize.py` produces it directly —
  `np.nanmean` and `np.nanstd` over a 10×10 slice. The scan is gone from this report; the
  impossibility bound replaces it and needs no scan.
- **Finding 9 overstated** as a defect that could affect scores. It cannot.
- **Finding 2 inverted.** The draft said the guard "only fires where the published curve
  falls", meaning Nellie's curve. Nellie never fires it at all. It fires on a baseline, which
  the draft never checked, and that is the stronger finding.
- **Four arithmetic slips**: 22 failing cells where 26 are imperfect, 30-to-68 minutes where
  25-to-68 is right, the voxel count described as covered by the frozen gate when it was
  not, and a `scripts/01_fetch.py` listed under reproducing that does not exist.
- **Axis naming**, repeated uncritically from the authors' code into our own `claims.json`.

Two claims from the blind run we checked and did not keep: that lv5 is among the degenerate
length levels (it is not), and that the σ = 4096 row reconstructs exactly at 100 cells (it
does not fit the one-partial-cell family; 1024 and 2048 do).

## Reproducing

Scripts run in order; each writes to `runs/`. The benchmark is 9.9 GB and the intermediates
about 5.5 GB per level, so nothing from `repo/` or `runs/out/*.npz` is published — see
`data/README.txt` for how to regenerate it.

```
scripts/02_run_methods.py 8 1024 8192 32768   # one level per process
scripts/03_analyse.py            # scores against the frozen band
scripts/06_checkiou_probes.py    # findings 2 and 9, no data needed
scripts/07_replicate_spread.py   # the replicate bar
scripts/08_verify_review.py      # finding 1, the impossibility bound and lv5
scripts/09_verify_defects.py     # findings 3, 4, 6
scripts/10_verify_shortcut.py    # finding 2, label counts per method
scripts/11_slice_spread.py       # the slice sd and the baseline rows
scripts/12_baseline_slice.py     # Otsu and Triangle on the slice
```

`04_aggregation_scan.py` and `05_timepoints.py` are in there too and are not part of the
argument. 04 scanned four candidate reductions before we found that `visualize.py` names
the right one outright; 05 is the attempt at the second timepoint that died twice, and
`07_replicate_spread.py` replaced it. Both are kept because the report says they ran.
