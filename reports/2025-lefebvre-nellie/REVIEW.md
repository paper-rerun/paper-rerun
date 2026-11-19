# Adversarial review of REPORT.md

Reviewed 2026-11-18 against `claims.json` (SHA-256 verified:
`68617898061165b7c1725f17de8207fdcbe54aaa01cafb2552fddc781c4664a4`), the grids in
`runs/out/*.npz`, the reference tables in `data/ref/seg_sim_exported_data/`, and the
authors' code in `repo/nellie-supplemental/` and `env/venv/.../nellie` (0.4.1).

Nothing was regenerated and nothing was re-segmented. My scripts are in `review/`, their
output in `review/*.log`. Every number below was recomputed here, not taken from the
report.

## Summary

| | |
|---|---|
| Finding 1, the claim that the published bar is within-grid spread, not replicate spread | **survives**, and is the strongest thing in the report |
| Finding 1's scan ("we scanned every candidate", "all 1000 cells wins") | **breaks**: a candidate it never tried fits better and is closer to the released code |
| Finding 1's axis labels ("per-intensity means", "spread across object brightness") | **breaks**: the axis `check_IoU` calls intensity is the generator's length axis |
| Finding 1's replicate bar | arithmetic correct; the n = 2 caveat is missing and one of the eight pairs does not survive it |
| Finding 2 | survives, and can be made sharper |
| Finding 3 | attribution is defensible, but the report left its own best supporting evidence unused and ignored a second version axis |
| Finding 4 | mechanism correct, impact overstated: the defect provably cannot change any score |
| Finding 5 | mechanism correct; the separation the report called impossible is cheap, I did it, and it says the shortcut fires in **zero** Nellie cells — but it decides an entire published row for Triangle |
| Finding 6 | survives as "cannot reproduce"; the cell count is wrong and one mechanism went unexamined |
| Pipeline stopping after `Network` | survives, verified in code and in file mtimes |
| Arithmetic | all eight verdict rows, the scan column, the zero counts, the voxel count and the ratios reproduce; four smaller numbers do not |

---

## 1. Finding 1

### 1.1 The scan is not exhaustive, and the candidate it missed fits better

The report says "we scanned every candidate instead of picking one. ... That is four
candidates". It is four *mean* reductions. `visualize.py` does not only write a mean per
`(noise, intensity)` pair: it writes a mean **and an `np.nanstd`** per pair (`std_att =
np.nanstd(vals)` on the `[:, intensity_num, :]` slice). claims.json itself says so
("reduces it to a mean and an sd over those 100 values"). The obvious unreleased last step
is therefore to average the ten (mean, sd) pairs, which yields exactly mean ± sd with
N = 10. The scan never tried it.

It fits better than the 1000-cell reading, on the report's own scoring rule
(`review/01_arith.log`, section C; mean |our sd − published sd|):

| candidate | 8 pairs | the 6 pairs whose mean reproduces |
|---|---|---|
| mean of the 10 within-slice sds, axis 1 (= averaging visualize.py's sds) | **0.0598** | **0.0128** |
| all 1000 cells (ddof 0, the report's winner) | 0.0625 | 0.0146 |
| all 1000 cells (ddof 1) | 0.0626 | 0.0146 |
| sd of the 100 cells in one middle axis-1 slice | 0.0644 | 0.0176 |
| mean of the 10 within-slice sds, axis 0 | 0.0679 | 0.0357 |
| sd of the 10 means over axis 2 | 0.0759 | 0.0654 |
| mean of the 10 within-slice sds, axis 2 | 0.1066 | 0.1116 |
| sd of the 10 means over axis 0 | 0.1278 | 0.1615 |
| sd of the 10 means over axis 1 | 0.1613 | 0.2062 |
| sem over 1000 cells | 0.1877 | 0.2326 |

Per pair for the winner: 8 IoU −0.0041, 1024 F1 −0.0054, 1024 IoU +0.0059, 8192 F1
+0.0086, 8192 IoU −0.0039, 32768 IoU +0.0488.

Two consequences. First, "all 1000 cells wins" is wrong as stated, and "nothing in the
released code performs that last reduction" is too strong — the released code performs
all of it except an average over ten numbers it has already computed. Second, and this is
the important part, **the substance of finding 1 is untouched**: the within-slice sd is
still a spread over 100 objects of different thickness and brightness inside one
simulation, not over replicates. The report should present the family of within-grid
readings as indistinguishable (0.0128 to 0.0176 over the six good pairs) and stop claiming
to have identified *the* reduction. The separation that matters — any within-grid reading
versus the replicate spread — is three orders of magnitude, not 0.002.

### 1.2 The axis names are swapped

`multi_grid.py` places each sub-volume at `large_image[start_x:…, start_y:…, start_z:…]`
with `start_x` from the thickness loop, `start_y` from the length loop and `start_z` from
the intensity loop. In NumPy order that is axis 0 = thickness, axis 1 = length,
axis 2 = intensity. `check_IoU` names axis 1 "intensity" and axis 2 "length".

Measured on the regenerated clean volume (`review/02_volumes.log`), per-cell peak
intensity averaged along each axis:

```
axis0 (check_IoU: thickness)  [32767 ... 32767]      flat
axis1 (check_IoU: intensity)  [32767 ... 32767]      flat
axis2 (check_IoU: length)     [6553 12378 ... 58982] = multi_grid's intensity_vector
```

and per-cell marked voxels are constant (1222) along axis 2, which is what varying
brightness alone does. The scores agree: mean IoU along axis 2 at σ = 32768 runs
0.006 → 0.816 (`review/06_where_fail.log`).

So:

- the report's scan table rows "mean over length" (0.0759) and "mean over intensity"
  (0.1613) must swap labels;
- the primary reduction frozen in claims.json — "mean of the 10 per-intensity means" —
  is in fact the mean of the ten per-**length** means, and the ±0.0092, ±0.0022, ±0.0315,
  ±0.0696 in the verdict table are spreads across length, not brightness;
- claims.json's note and the report's "the published error bar is the spread across object
  brightness" are wrong in the specific axis they name. "Spread across the objects in the
  grid" is right and is all the report needs;
- the defect is the authors', not the report's — but the report repeats it without
  noticing, and if this goes to the authors naming the wrong axis will be the first thing
  they see. It is also a defect worth reporting in its own right: every
  per-"intensity" curve `visualize.py` writes is a per-length curve.

### 1.3 The replicate spread is measured on what it claims, with one gap

Verified:

- `add_noise` is called once per timepoint inside `for t in range(3)` over the same
  `large_image`, with `np.random.normal` / `np.random.poisson` and no seed: three
  independent draws over one clean volume ✓.
- `select_temporal_range`'s end is inclusive: `verifier.py:506` builds
  `range(self.t_start, self.t_end + 1)` ✓, so `(0, 1)` writes two timepoints, and the
  second was already on disk ✓.
- the two draws were segmented inside one process, so I checked for coupling. `Filter`,
  `Label` and `Network` all loop `for t in range(self.num_t)` and read
  `self.im_memmap[t, ...]`; the thresholds in `Label._get_labels` are computed from that
  frame alone. The only cross-frame state is `max_label_num`, which offsets label values
  and cannot change a per-cell unique count. The draws are independent measurements ✓.
- `grid_N.npz` and `grid_N_t0.npz` are bit-identical, so the verdict table and "draw 0"
  are the same numbers ✓ (`review/01_arith.log`, section A).
- the eight pairs, the per-draw means, the sds and the "10× to 542×" range all reproduce:
  10.5 to 542.1 (`review/01_arith.log`, section E).

The gap: **the report never says n = 2.** An sd from two numbers has one degree of
freedom; the 95% interval for σ runs from 0.45 s to 31.9 s. Applying that:

| pair | replicate sd | 95% upper bound on σ | printed sd | printed bar still excluded? |
|---|---|---|---|---|
| 1024 F1 | 0.000246 | 0.0079 | 0.1335 | yes |
| 8192 F1 | 0.001908 | 0.0609 | 0.3650 | yes |
| 32768 F1 | 0.010830 | 0.3456 | 0.1135 | **no** |
| 8 IoU | 0.001041 | 0.0332 | 0.1869 | yes |
| 1024 IoU | 0.003495 | 0.1115 | 0.1631 | yes |
| 8192 IoU | 0.001398 | 0.0446 | 0.2987 | yes |
| 32768 IoU | 0.001721 | 0.0549 | 0.2966 | yes |

Six of seven survive on their own; the 10.5× pair does not, and that is the one the
report quotes as the low end of its headline range. The honest version is "on six of the
seven pairs the printed bar is above anything two draws can support, by 47× to 542×; at
σ = 32768 F1 the two draws differ by enough that n = 2 cannot settle it". The sentence
"The honest replicate bar would be thinner than the line" is not supported by two draws;
"thinner than the line on six of the seven pairs, with n = 2" is.

### 1.4 Three presentation faults in the same section

- "Pair by pair: 0.1335 against our 0.1290, 0.3650 against 0.3758, 0.2987 against 0.2982,
  0.1869 against 0.1926." Those are four of the six good pairs — the four closest. The
  two it omits are the two worst: 1024 IoU 0.1631 against 0.1791 and 32768 IoU 0.2966
  against 0.3465. The mean it quotes (0.015) is right; the list is selected. A report that
  is this strict about the authors' error bar cannot quote only its own best four pairs.
- "no per-axis reduction gets within 0.076 of it" mixes scopes: 0.0759 is the eight-pair
  score for the axis-2 reduction, while 0.015 is a six-pair score. On the six pairs the
  axis-2 reduction scores 0.0654, which *is* within 0.076. The margin is still 4.5× in the
  1000-cell reading's favour, so the conclusion holds; the sentence does not.
- "Six of those 'ok' verdicts are passes against a bar that is 10 to 542 times too wide."
  The 10.5× pair is σ = 32768 F1, which is one of the two **failures**, not one of the six.
  For the six ok rows the range is 46.7× to 542×.

---

## 2. Arithmetic

Recomputed from `runs/out/*.npz` and `data/ref/` (`review/01_arith.log`). These come back
exactly as printed: all eight means and primary sds, all eight deltas, all eight bands and
the six-of-eight verdict; the whole 32-row aggregation scan and its four-candidate summary
column (0.0625 / 0.0759 / 0.1278 / 0.1613); the six-pair figure 0.015 (0.0146); the
zeroed-cell counts 10 / 0 / 33 / 58; the replicate table and the 10×–542× range; 1000
connected components and 1,223,550 marked voxels; the 9.9 GB benchmark (9873 MB for the
13 noisy files) and about 5.5 GB per level (5573 MB).

What does not come back:

1. **"22 of 1000 cells fail for us" (finding 6).** 22 is the number of cells scoring
   F1 exactly 0. The number of cells that are not perfect is **26** in draw 0 and 24 in
   draw 1; the mean 0.9760 implies a deficit of 24 F1 points spread over those 26 cells.
   Say "26 of 1000 cells are imperfect, 22 of them score zero".
2. **"At roughly 30 to 68 minutes of segmentation each".** `runs/out/timings.json` has
   1475.9 s (24.6 min), 1816.9 s (30.3 min), 4057.1 s (67.6 min); σ = 8 was reused from an
   earlier run and has no timing. The low end should be 25 minutes, and the ten-hour
   extrapolation rests on three measured levels.
3. **"matching the frozen gate"** applied to both 1000 components and 1,223,550 voxels.
   The frozen gate is the component count only; the voxel count matches nothing published
   and is a report-side observation. Both numbers are correct.
4. **`scripts/01_fetch.py` is listed under Reproducing and does not exist.** The scripts
   directory holds 02 through 07 only.

One more consistency note, in the report's favour: the sd column of the verdict table is
the per-axis-1 reduction, which after §1.2 is a spread across length. The numbers are
right; the label is not.

---

## 3. Findings 4 and 5

### 3.1 Finding 4: the mechanism is real, the impact is zero, and the stated reason is wrong

`np.isin(gt_partial_coords, label_coords).all(axis=1)` is elementwise membership in the
flattened label coordinate array, so probe A in `scripts/06_checkiou_probes.py` does
demonstrate what it claims: a coordinate passes when its three numbers each appear
anywhere in `label_coords`. Confirmed.

But the report's impact sentence is wrong twice. "The `max_iou < 0.1` floor further down
catches the worst of them, so this will not usually flip a score": the floor is not what
makes this harmless. The gate only ever *adds* candidates, and for an added candidate the
loop computes the true `iou = |gt ∩ label| / |gt ∪ label|`, which is 0 for a label that
does not touch the object, so `iou > max_iou` is never satisfied and neither `max_iou` nor
`tp_label` can change. `fp` is computed from `unique_labels` and never looks at the gate.
So the defect **cannot flip any score at all**, under any data; it only wastes the
intersection and union work it was written to avoid.

I checked that empirically rather than only by argument: `review/05_gate_probe.py` runs
the authors' `check_IoU` and a copy whose gate is a real row lookup over six random
scenes built to include exact matches, partial matches with a disjoint intruder, and cells
whose only label is disjoint. Both F1 and IoU arrays are identical in all six
(`review/05_gate_probe.log`).

Recommendation: keep finding 4 as "a line that does not do what it is written to do, with
no effect on any published number — a cost bug, not a measurement bug". As written ("will
not usually flip a score") it invites the reader to think some numbers moved. Going to the
authors, that is the kind of sentence that costs the report credit it does not need to
spend.

### 3.2 Finding 5: the separation was cheap, I did it, and it changes the finding

The report: "That count is an upper bound on how many the shortcut could have zeroed, not
a measure of it … Doing so needs a per-cell label count we did not keep."

The segmentations are still on disk (`repo/.../nellie_necessities`, 38 GB). The per-cell
label count is `len(np.unique(cell))` on the same 48³ blocks `check_IoU` slices — exactly
what the function itself computes. `review/02_volumes.py` does it for all four levels in
about a minute per level, reading one timepoint through zarr, no re-segmentation
(`review/02_volumes.log`):

| σ | cells with ≥ 100 labels | max labels in a cell | median | F1 = 0 and IoU = 0 | of those, shortcut-zeroed | genuinely missed |
|---|---|---|---|---|---|---|
| 8 | 0 | 18 | 2 | 10 | **0** | 10 |
| 1024 | 0 | 51 | 2 | 0 | **0** | 0 |
| 8192 | 0 | 52 | 2 | 33 | **0** | 33 |
| 32768 | 0 | 63 | 4 | 58 | **0** | 58 |

The shortcut never fires anywhere in this run. Nellie's output is a relabelled skeleton,
which never accumulates a hundred labels in one 48³ cell even at the collapse level. So
the report's "it only fires where cells fill with noise labels, which is exactly where the
published curve falls" is, for Nellie, contradicted by data the report already had.
Finding 5 as written implies a relevance to the published Nellie curve that cannot be
supported, and it is the one place where the report does less work than it could and
leaves the slack as an insinuation against the authors.

**Where the shortcut does bite is the baselines, and the report never looked.** The same
`check_IoU` scores Otsu, Triangle, MitoGraph and Mitometer with `is_label=False`, which
labels the thresholded mask — and a thresholded noisy volume is exactly the thing that
puts thousands of components in a cell. Counting the way `check_IoU` counts (global
`ndi.label` with full connectivity over the 500³ crop, then unique per cell:
`review/04_global_labels.py`, `review/04_global_labels.log`):

| method, σ | occupancy | global labels | cells with ≥ 100 | median | our score | published |
|---|---|---|---|---|---|---|
| Triangle, 8192 | 0.024 | 1,134,942 | **1000 of 1000** | 1014 | F1 0.0000, IoU 0.0000 | F1 0.0000 ± 0.0000, IoU 0.0000 ± 0.0000 |
| Triangle, 32768 | 0.233 | 96,462 | 37 | 82 | IoU 0.0394 | IoU 0.0396 |
| Triangle, 1024 | 0.019 | 36,869 | 0 | 33 | F1 0.0611, IoU 0.4959 | F1 0.0577, IoU 0.5013 |
| Otsu, 8192 | 0.007 | 2,789 | 0 | 2 | F1 0.7472, IoU 0.6085 | F1 0.7483, IoU 0.6117 |
| Otsu, 32768 | 0.261 | 51,718 | 0 | 44 | F1 0.0029, IoU 0.0370 | F1 0.0000, IoU 0.0370 |

Read the Triangle rows together. At σ = 8192 every one of the 1000 cells trips the
shortcut, so every cell is scored `fn = 1`, F1 = 0, IoU = 0 by the guard rather than by the
segmentation — and the published Triangle row at 8192 is exactly 0.0000 ± 0.0000 for both
metrics, as are 2048, 4096 and 16384. At σ = 32768 the mask becomes dense, the specks merge
into few global labels, only 37 cells trip the shortcut, and both our IoU (0.0394) and the
published IoU (0.0396) come back off zero. That non-monotonic bump after four exact-zero
rows is the shortcut switching off, and it is visible in the published Source Data itself
(`data/ref/.../IoU_Multigrid_F1_lv5_triangle.txt`). Mitometer's published column has the
same signature: exactly 0.0000 ± 0.0000 from 1024 to 32768.

That is a real, demonstrated defect in the benchmark that makes the baselines look worse
than they are, and because it never fires for Nellie the error is one-directional in
Nellie's favour. It is a stronger claim than finding 5's, it is supported rather than
speculative, and the report's own `results.json` plus files already on disk were enough to
find it. Caveat to keep: Otsu at 32768 is *not* the shortcut (0 of 1000 cells), its near
zero is genuine; I did not count labels for MitoGraph or Mitometer, which were never run
here.

---

## 4. Findings 3 and 6, and whether "version" is a parking space

The attribution is defensible but underargued, and it is missing two things.

**What supports it, which the report does not use.** The controls reproduce the published
curve almost exactly: Otsu F1 0.7800 at σ = 8 and 1024 against a published
0.7800000000, Otsu IoU 0.6268 / 0.6275 / 0.6085 / 0.0370 against 0.6294 / 0.6303 /
0.6117 / 0.0370, Triangle IoU 0.0394 against 0.0396 at σ = 32768, and Triangle's exact
zero rows reproduced exactly. Otsu and Triangle share the regenerated volume, the
regenerated ground truth, the noise draw and the authors' `check_IoU` with Nellie, and
differ only in the segmenter. Their agreement is direct evidence that the generator, the
ground truth and the measurement path are faithful, which is precisely the argument
finding 3 needs in order to narrow the discrepancy to the segmenter. The report instead
says only "we did not freeze claims about them and make none here" — fine for the verdict,
wasteful as evidence. Use it as a diagnostic.

**A second version axis the report ignores.** Finding 2 says Nellie is unpinned. It does
not say that this run also violates the one pin the authors *did* give:

| package | supplemental `requirements.txt` | installed in `env/venv` |
|---|---|---|
| scikit-image | 0.23.1 | **0.22.0** |
| scipy | 1.13.0 | 1.12.0 |
| tifffile | 2024.2.12 | 2026.3.3 |
| ome-types | 0.5.1.post1 | 0.5.2 |
| numpy | 1.26.4 | 1.26.4 ✓ |

And the pin conflict is not the run's fault: `nellie-0.4.1.dist-info/METADATA` requires
`scikit-image==0.22.0`, which contradicts the supplemental's `scikit-image==0.23.1`. Nellie
0.4.1 cannot be installed into the environment the benchmark repository specifies. That is
a much sharper statement of finding 2 than "Nellie is not one of them" — the release is
not merely silent about the version under test, it is internally inconsistent about it —
and it is a second candidate for findings 3 and 6 that has nothing to do with Nellie's own
code: `multi_grid.py` builds the ground truth with `skimage.morphology.skeletonize_3d` and
`binary_dilation`, and `Network` uses `skimage.measure.label` and `regionprops`. The report
should name scikit-image 0.22.0 vs 0.23.1 as a second unpinned axis, and can retire it
cheaply in a throwaway venv by regenerating the clean volume under 0.23.1 and comparing
the voxel count and the component count — no segmentation needed. Until then "a version
difference would explain it" is two hypotheses presented as one.

**A mechanism finding 6 leaves unexamined.** Our σ = 8 failures are not scattered
(`review/06_where_fail.log`): all 26 imperfect cells sit at intensity index 0, the 10%
brightness column, and within it at thickness indices 0–1 and 8–9. At σ = 1024 all 20
imperfect cells sit at intensity index 0 and thickness 8–9. This is not a noise story — it
is the dimmest objects, plus the fattest ones, where the skeleton of a thick blob can
carry more than one branch label and `fp` becomes 1. That is a testable, named mechanism
(threshold behaviour at 10% intensity; branch relabelling of thick objects in `Network`),
and it is also the mechanism a version change would act through. Finding 6 as written
stops at "we cannot reproduce it and finding 2 is why", which is honest but thinner than
what is on disk.

**On the honesty of the attribution overall.** Finding 3 does rule out the noise draw with
a measurement (0.015 against a 0.29 gap) and does name the measurement and the segmenter
as the remaining suspects. It is not a parking space in the sense of being asserted
without work. It is incomplete: the regenerated ground truth is dismissed by implication
rather than by the control evidence that would settle it, and "version" is left as one
bucket when there are at least two.

---

## 5. The stop after `Network`

Verified, and the report's reasoning holds.

- `analysis.py` selects Nellie outputs by `file.endswith('skel_relabelled.ome.tif')` and
  reads `tifffile.imread(nellie_output)[0]` — one file, first timepoint. Nothing else from
  the Nellie output tree is read for this figure (the other methods read their own files;
  the ground truth comes from `noiseless/no_noise.ome.tif`).
- `im_skel_relabelled` is written only in `networking.py` (lines 521–639). `Hierarchy`
  (`hierarchical.py:127`) and `VoxelReassigner` (`voxel_reassignment.py:389`) open it, but
  only read: every occurrence is an index on the right-hand side, and the reassignment
  writes into `reassigned_memmap`, a separate file. The `get_memmap` default mode is `r+`,
  so a write *could* happen; it does not.
- Empirical confirmation, which matters for σ = 8 where the first attempt ran the full
  `run()` and died in `Hierarchy`: the σ = 8 `im_skel_relabelled` has mtime 16:03 while
  `voxel_matches.npy` from the later stages is 17:32. The file the metric reads was not
  touched after `Network`.
- Stage order is strictly forward (`Filter` → `Label` → `Network`), each reading the
  previous stage's output file; no earlier stage reads anything a later stage writes.

One disclosure gap, not an error: σ = 8 was segmented by a different code path (the full
`run()`, per `runs/logs/hierarchy_oom.log` and the extra `im_marker`, `im_distance`,
`flow_vector_array` and `voxel_matches` files that exist only for that level) from the
three others (`Filter`/`Label`/`Network` only). The report mentions the Hierarchy crash but
not that the level is the odd one out procedurally. Given the mtime and code evidence it
changes no number, and saying so costs one sentence.

## 6. Overclaiming and tone

Harsher on the authors than the facts warrant:

1. Finding 4, "this will not usually flip a score" — it cannot flip one. Fix to "no effect
   on any score; a cost bug".
2. Finding 5, "it only fires where cells fill with noise labels, which is exactly where
   the published curve falls" — true of the baselines, false of Nellie, whose published
   curve this report is about. With the count now in hand the sentence must go.
3. Finding 1, "Nothing in the released code produces that reduction" — the released code
   produces everything except an average of ten numbers it has already written.
4. Finding 6, "a perfect row means no spurious label anywhere in the volume at that noise
   level" — anywhere in the 1000 measured 48³ cells. The 5-voxel border and the 2-voxel
   gaps between cells are never looked at. Smaller claim, same force.
5. Finding 1, "The bar measures how much the score varies with what you are looking at" is
   fair; "the spread across object brightness" (claims.json, repeated in the report) names
   the wrong axis.

Softer on itself than on the authors:

6. The four-of-six pair list in finding 1 (§1.4).
7. The 0.076 scope mix (§1.4).
8. n = 2 is never stated, and the one pair it cannot carry is the one quoted as the
   headline low end (§1.3).
9. "We scanned every candidate" (§1.1).
10. Finding 5's "Doing so needs a per-cell label count we did not keep" — the count is one
    `np.unique` per cell over files that are still on disk, which is less work than the
    probes the report did write (§3.2).
11. The environment violates the authors' only pin, and the report does not say so while
    making a finding of the missing one (§4).

Fair and well calibrated, for the record: the "A caveat about our own band" section; the
refusal to re-cut the frozen band after seeing the data; reporting the wasted
`05_timepoints.py` run; reporting the Hierarchy OOM instead of working around it; stating
plainly that 0.4.1 was the reviewer's choice; and finding 6's refusal to call the published
row wrong.

## 7. Two defects in the benchmark the report did not look for

Both are in `comparisons/simulations/utils.py` and affect every method in the figure
equally, which is the same ground finding 4 stands on (`review/07_noise_model.py`,
`review/07_noise_model.log`):

- **The PSF is 2D.** `add_noise` loops `for frame_num, frame in enumerate(noisy_image)` and
  applies `gaussian_filter(frame, sigma=psf_sigma)` to each slice. `multi_grid.py` hands it
  a 3D volume, so the loop runs over z and each z slice is blurred in-plane with no axial
  blur at all. A 60000 delta blurred at σ_psf = 0.85 gives `[0, 0, 13217, 0, 0]` along
  axis 0 and `[829, 6615, 13217, 6615, 829]` along axes 1 and 2. The comment says "PSF
  assume isotropic for comparisons purposes"; the objects in the benchmark are axially
  sharp, which is not what a diffraction-limited 3D acquisition looks like and is kind to
  any method that works slice-wise.
- **The Gaussian noise is not zero-mean.** `frame += np.clip(normal_noise, 0, 65535)`
  clips the negative half before adding, so "Gaussian noise, std σ" is a positive-only
  background offset with mean σ/√(2π): measured 12763 at σ = 32768 against a predicted
  13073, and the real file's first slices have mean 12800 with median 16. The x-axis of
  Extended Data Fig. 2 is therefore a joint sweep of background level and noise, and the
  signal ceiling (58982) is less than five times the mean background at the last point.
  Worth one paragraph, because it changes how the collapse at the right-hand end should be
  read.

## 8. What survives

The central claim survives intact and is worth publishing: the published N = 10 bar is a
spread over the 1000 objects of the grid, not over replicates, and the replicate spread is
smaller by one to nearly three orders of magnitude on six of seven pairs. Finding 2
survives and gets sharper. Finding 4's mechanism survives with its impact corrected to
zero. Finding 5's mechanism survives and moves to where it demonstrably decides a
published row. Findings 3 and 6 survive as failures to reproduce with an incomplete
account. The stop after `Network` is correct. The arithmetic is sound except for the four
items in §2.

Fix list, in the order a reader of the final report would hit it: the swapped axis names
(§1.2), the "every candidate" claim and the better-fitting reduction (§1.1), the n = 2
caveat (§1.3), finding 5's rewrite with the real counts (§3.2), finding 4's impact
sentence (§3.1), the four arithmetic items (§2), the control evidence and the scikit-image
pin for findings 2 and 3 (§4), and the two simulator defects if the authors are being
written to anyway (§7).
