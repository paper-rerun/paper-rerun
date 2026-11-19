# Independent blind check — Nellie, Extended Data Fig. 2a/b (noise sweep)

Lefebvre, A.E.Y.T. et al., "Nellie: automated organelle segmentation, tracking and
hierarchical feature extraction in 2D/3D live-cell microscopy", Nature Methods (2025),
doi:10.1038/s41592-025-02612-7.

Target: Extended Data Fig. 2, panels **a** (IoU) and **b** (F1) — score against Gaussian
noise level for Nellie and four other methods on the simulated multi-grid volume.
Numbers checked: `Multigrid_F1_lv5_nellie.txt` and `IoU_Multigrid_F1_lv5_nellie.txt`
from Supplementary Data (MOESM16).

**Independence.** Blind. Nothing from the other team's directory, the project log, the
pipeline doc, the queues or `paper-rerun/reports/` was opened, listed or searched at any
point. No accidental exposure occurred: no path from any of those locations appeared in
any error message or tool output during this run.

**Freeze.** `claims.json`, SHA-256 `6c9de4db5ce212be8344252dc06759399e7ea71d74dc4123c570671a096fea23`
(`claims.sha256`), frozen at 2026-11-18T21:59:03-03:00 (`claims.frozen_at.txt`) — before
the Supplementary Data was downloaded or read. Claims C1-C13 and the declared
non-checks are as frozen; two of them (C2, C4) came out differently from what I predicted,
and that is reported below rather than rewritten.

## Inputs

| file | sha256 |
|---|---|
| `41592_2025_2612_MOESM16_ESM.zip` | `2999fc44a949187fdb0cbd1d59b1114026ae7b237678ef1e396b9e109c6ce3e5` |
| `Multigrid_F1_lv5_nellie.txt` | `95ca7aa7e9cf4b93f9903ea34dbd49db0b6601656c90af23966e6fda2273ef65` |
| `IoU_Multigrid_F1_lv5_nellie.txt` | `76ac25c96ea1e543ebf99cdbb1c99e86db7a3debac38a27935702110e3ae2c6d` |
| `multi_grid/analysis.py` | `515ec3ed9f3962e06e82f91425c408675679bb5d71ff5f0afdc87b6a5981bf5a` |
| `multi_grid/multi_grid.py` | `a4f3ad68a142b1709602c4fa4e34fba078a0dfd5e8ff3348c799ea5b5616c59c` |
| `multi_grid/visualize.py` | `be1fd115e3ab5f18710fa7d0385859fa562f09e0dfbeb9e6d9d40fc895321a04` |
| `simulations/utils.py` | `9726e487aea882c2a2f5e54ff0a02e31d516584c9b0c166b5dba326732a84e66` |

Source repo `aelefebv/nellie-supplemental` at `7a639bca9b426a1addbf358fe8fffb389949b30d`
(fetched file-by-file from the commit tree: a full clone dies with
`fatal: Out of memory, malloc failed (tried to allocate 2843738112 bytes)`, and
`--depth 1 --filter=blob:none` fails the same way). Nellie package: GitHub `main`
plus the PyPI sdist, latest release v1.0.4.

Scripts: `scripts/check_code.py` (loads the released functions by path and exercises them),
`scripts/check_data.py`, `scripts/decompose.py`. Outputs in `runs/`. Everything ran in a
local venv pinned to the released `numpy==1.26.4` / `scipy==1.13.0`.

## The headline finding

**The published N does not match the dispersion published next to it, and for three of
the thirteen Nellie F1 rows the pair (mean, sd) is arithmetically impossible at N = 10.**

Both Nellie files carry `N = 10` in every row, and the figure caption says "N = 10, where
each point is the mean score at a different intensity value. ... All data points are mean
+/-95% confidence intervals."

F1 and IoU are bounded in [0, 1]. For n values in [0, 1] with a fixed mean m, the largest
possible sd is reached by the extremal configuration (k values at 1, one at the remainder,
the rest at 0). Comparing that ceiling with the published sd (`runs/data_checks.txt`):

| noise | published mean | published sd | max sd at N=10 | max sd at N=100 |
|---|---|---|---|---|
| 1024 | 0.9809523810 | **0.1335032930** | 0.057143 | 0.133503 |
| 2048 | 0.9466666667 | **0.2196967607** | 0.160000 | 0.219697 |
| 4096 | 0.9475000000 | **0.2129994131** | 0.157500 | 0.218789 |

The sd exceeds what ten values in [0, 1] can possibly have — by 2.3x, 1.4x and 1.4x —
and the gap survives the ddof=1 variant. So the mean and sd were not computed over ten
numbers.

They were computed over one hundred. Two of the three rows sit exactly on the N=100
ceiling, and the exact configuration is recoverable (`runs/decompose.txt`):

- noise 1024: 98 sections at F1 = 1, one at **2/21**, one at 0 -> mean 0.9809523810,
  population sd 0.1335032930 — both match the published 10-decimal values exactly.
- noise 2048: 94 sections at F1 = 1, one at **2/3**, five at 0 -> mean 0.9466666667,
  population sd 0.2196967607 — exact match.

2/21 and 2/3 are not arbitrary: the released `check_IoU` can only emit F1 = 0 or
F1 = 2/(2+fp), so 2/3 is one false positive in that section and 2/21 is nineteen. The
reconstruction is self-consistent with the released measurement code, down to the
false-positive count, at N = 100 sections.

That is also what the code route predicts: `visualize.py` aggregates
`stats[stat][key][:, level, :]` with `np.nanmean` / `np.nanstd`, i.e. a 10x10 slice of the
10x10x10 per-section array — 100 section scores, population sd (ddof = 0). My frozen C2
predicted N = 100 for this reason; the dispersion in the data agrees with the code and the
published N column does not.

Consequence for the figure: the error bars are drawn as 95% CIs. With sd and N as
published, the half-width is 1.96*sd/sqrt(10), which puts the upper bound **above 1.0 —
above the ceiling of the metric — for noise levels 1024, 2048, 4096 and 8192** (e.g.
0.9810 + 0.0827 = 1.064 at noise 1024). With the N the sd actually belongs to, the same
rows give 0.0262 instead of 0.0827, i.e. bars about 3.2x smaller. Either N = 10 is wrong,
or the sd is; they cannot both be right.

The same test on the other four methods' F1 files: mitograph 2 impossible rows, mitometer
1, nellie 3, otsu and triangle 0 (their means sit lower, where the N=10 ceiling is loose
enough to hide the problem). Every file carries N = 10. So this is one systematic mismatch
across the panel, not a typo in the Nellie row.

A second, smaller point about N: the 100 sections are 100 different simulated objects in
one frame of one noise realisation, not independent replicates of a measurement. The three
time frames generated by `multi_grid.py` are not used — the analysis reads frame 0 only
(`tifffile.imread(...)[0]`, `frame_0` for mitograph). Whatever the N, the interval
describes heterogeneity across simulated objects, not run-to-run uncertainty.

## What reproduced

- **C1 — yes.** Both files have exactly 13 rows, noise = 8, 16, ..., 32768, matching
  `std_vector` in `multi_grid.py`, and 4 columns (`Noise` plus three repeats of the method
  name). The three value columns read as mean, sd, N.
- **C3 — yes.** The two files agree row for row on noise ordering and on the N column, as
  expected from a single `check_IoU` call per level.
- **C4, first half — yes.** Every mean is in [0, 1].
- **C5 — yes.** The seven lowest-noise F1 rows are mean 1.0 with sd 0.0 (all 100 sections
  perfect); no row has mean 0 with sd > 0, and no row has sd 0 with a mean other than 0/1.
- **C4, second half — passes as frozen but is the wrong test.** I had frozen the bound
  sd <= sqrt(m(1-m)), the continuum/Bernoulli case; all 26 rows satisfy it (noise 1024
  misses it by 0.0032). That bound is far too loose for a sample of ten. The tighter
  finite-N ceiling is what exposes the problem above. My frozen tolerance was not wrong,
  it was not sharp enough — I report both.
- **C6 — yes.** Nothing in the released `analysis.py` or `visualize.py` computes or writes
  an N. `visualize.py` writes only mean and std columns to `multigrid_all_vals.csv`. The N
  column in the Source Data was added outside the released code, which is exactly how it
  ends up disagreeing with the sd beside it.
- **C10 — yes, and it is harmless.** `np.sum(np.isin(gt_partial_coords, label_coords).all(axis=1)) == 0`
  does not test coordinate-triple membership; `np.isin` flattens, so it tests whether each
  component value appears anywhere in the other array. Demonstrated: gt coord `[1,2,3]`
  against label coords `[[3,1,2],[2,3,1]]` shares no row, yet the filter reports a match
  and does not skip the label. It is only ever too permissive — a genuinely overlapping
  label always passes — and the IoU that follows is computed properly, so `max_iou` is
  unaffected. Run-time defect, not an accuracy one.
- **C13 — yes.** Both `requirements.txt` files are full pip freezes (numpy 1.26.4,
  scikit-image 0.23.1, scipy 1.13.0, tifffile 2024.2.12, napari 0.4.19.post1). Neither
  pins **nellie**, the software under test; no version appears anywhere in the repo. No RNG
  seed is set anywhere (grep for seed/RandomState/default_rng over the whole repo: nothing),
  so the noisy volumes cannot be regenerated bit-for-bit. And there is no script in the
  released supplemental repo that runs Nellie on these simulations — mitograph, mitometer,
  otsu and triangle each have one, Nellie does not. The parameters behind the Nellie row of
  this figure are not recoverable from the release.

## Defects in the measurement code

Demonstrated on hand-built arrays fed to the released `check_IoU` itself, not asserted
(`runs/code_checks.txt`; the demos use a 210^3 volume, which has the geometry the function
hardcodes — a 5-voxel pad and 10 sections per axis).

**1. `fp` goes negative when a section has no background voxel, and a perfect match then
scores F1 = 0.** Line 64 is

    fp = len(unique_labels[unique_labels != tp_label])-1  # -1 to account for 0 label

The -1 assumes label 0 is always present in the crop. When one label fills the whole
section crop, it is not, so `fp = -1`, `tp + fp == 0`, the guard at line 71 sets
`precision = 0`, and F1 comes out 0. Demonstration: gt fills half the crop, the output is
one label covering the crop. `check_IoU` returns max_iou = 0.5000 (matched, above the 0.1
gate) and **F1 = 0.0000**, where the correct answer is 1.0 (tp = 1, fp = 0, fn = 0). Add a
single background voxel to the same output and F1 jumps to 1.0000 — the score flips on one
zero voxel. This can only hurt methods whose labels saturate a section (the thresholding
baselines at high noise) and cannot hurt Nellie, whose branch labels leave background.

**2. The `len(unique_labels) < 100` bail-out reports IoU = 0 for a perfect segmentation.**
Line 47 skips the matching loop entirely for crowded sections, leaving `tp_label = None`
and `max_iou = 0`. Demonstration, same perfect object each time, only isolated
single-voxel specks added:

| section contents | F1 | IoU |
|---|---|---|
| perfect match alone | 1.0000 | 1.0000 |
| perfect match + 97 specks (99 unique labels) | 0.0202 | **1.0000** |
| perfect match + 98 specks (100 unique labels) | 0.0000 | **0.0000** |

The F1 column is the metric working as designed (2/(2+97)). The IoU column is not: the
identical, perfectly segmented object reports IoU 1.0 at 99 labels and 0.0 at 100. Panel
**a** of the figure is that IoU. For any method that fragments under noise, the reported
IoU is a step function of a label count, not a measurement of overlap — a 0 there means
"more than 99 components in this 48^3 crop", not "no overlap found". The comment on that
line is `# skip this, it's bad`.

**3. The grid axes are relabelled between generation and analysis, so the exported lv
series is a length level, not an intensity level.** `multi_grid.py` places each sub-volume
at `start_x, start_y, start_z = ix*50+5, iy*50+5, iz*50+5`, where `ix` drives thickness,
`iy` drives length and `iz` drives intensity. Re-running that placement logic at 2x2x2
scale confirms: axis 0 = thickness, axis 1 = **length**, axis 2 = **intensity**.
`check_IoU` indexes its output as `[thickness, intensity, length]` (axis 1 named
intensity), and `visualize.py` then slices `[:, level, :]` and calls `level` an intensity
value — as does the caption. The fixed level in `*_lv5_*.txt` is therefore a fixed
**length**, averaged over thickness and intensity. A mean over the whole array would be
unaffected by the swap; a single-level export is not.

**4. `add_noise` clips the Gaussian noise itself, so the sweep is half-normal noise plus a
growing background offset.** In `utils.py`:

    normal_noise = np.random.normal(gaussian_mean, gaussian_std, frame.shape)
    frame += np.clip(normal_noise, 0, 65535)

The clip is on the noise, not on the noisy frame, so only the positive half survives.
Measured: nominal std 8 -> as added mean 3.19, sd 4.7; std 256 -> mean 101.9, sd 149.4;
std 8192 -> mean 3267, sd 4784. The offset tracks std/sqrt(2pi) (3.19, 102.13, 3268.14).
The released function on an all-zero volume at std = 1000 gives min 0, mean 401 (expected
about 399). The x axis of Extended Data Fig. 2a/b is thus a joint sweep of noise and
background level, and the effective noise sd is 0.58x the nominal label on the axis. This
hits every method equally, but it is not the stated quantity.

**5. `create_skeleton_sub_volume` clips the curve to `length-1` instead of to the 50-voxel
cell.**

    y = (25 + curvature_factor * np.sin(x * frequency)).astype(int)
    y = np.clip(y, 0, length-1)

Measured coordinate ranges from the released function:

| length | axis 0 | axis 1 | axis 2 |
|---|---|---|---|
| 4 | 0-3 | 3-3 | 3-3 |
| 8 | 0-7 | 7-7 | 7-7 |
| 20 | 0-19 | 19-19 | 19-19 |
| 26 | 0-25 | 20-25 | 20-25 |
| 40 | 0-39 | 20-30 | 20-30 |

For every length below about 26 the sinusoid is pinned to the clip value: the object
becomes a straight rod jammed into the low corner of its cell instead of a curved filament
centred at 25. `length_vector` is `linspace(4, 40, 10)`, so six of the ten length levels
(4 to 24 px) are degenerate. Level 5 of that vector is 24 px, inside the affected range —
so the exported `lv5` series, under finding 3 a length level, is a partially flattened,
off-centre geometry. The shortest lengths also sit a voxel or two from the cell face, where
`populate_skeleton` truncates the thickening sphere against the cell boundary and the
+1/-1 section trim in `check_IoU` shaves the object's edge.

## What I did not check, and why

I did not regenerate the 510^3 volume and did not segment any noise level. The frozen
reasons stand: about 10 GB and 30-70 min of CPU per level on a machine shared with running
Unreal Editors; and, more decisively, **no seed is set and no Nellie run script is
released**, so my noise draw would differ from theirs by construction and my segmentation
parameters would be a guess. A number produced that way could not be compared to the
published row, so it would not be evidence. Instead I exercised the released measurement
function itself, which is where the checkable content of this figure turned out to live.

Not checked: the four competitor rows beyond the N-feasibility test; the plotted error bars
in the figure image (I verified the Source Data arithmetic, not the rendering); the
px_size and separation panels; whether the IoU ceiling of about 0.73-0.77 at the lowest
noise is fully explained by the PSF blur (the ground truth is the unblurred binary while
the methods see a volume blurred with sigma about 0.85 px, so an IoU below 1 is expected,
but I did not quantify how much of the deficit that accounts for); which Nellie version
produced the figure (unpinned, not stated; current release is v1.0.4).

## Bottom line

The 13 noise levels, the row alignment between the F1 and IoU files, and the internal
consistency of the means with the released F1 formula all hold up; two rows reconstruct to
the exact section-by-section composition, which is a strong sign the published means are
what the code computes.

The reported **N = 10 is wrong for the dispersion published beside it**: the sd of three of
the thirteen Nellie F1 rows is larger than any ten [0,1]-bounded values can produce, and it
matches a population of 100 per-section scores exactly — the 100 the released
`visualize.py` aggregates. The 95% CIs built on N = 10 extend above F1 = 1 on four rows.
The same mismatch appears in all five methods' files.

Separately, the released measurement function has two defects that distort the comparison
between methods — a false-positive count that goes negative and zeroes a correct match,
and a 100-label bail-out that reports IoU = 0 for a perfectly segmented object — both of
which penalise fragmenting or saturating methods and neither of which can penalise Nellie.
The simulated ground truth is degenerate at six of its ten length levels, the noise is
half-normal rather than Gaussian, and the axis labelled intensity in the export and the
caption is the length axis. Nothing is pinned for Nellie itself, no seed is set, and no
script that runs Nellie on these simulations was released, so the figure cannot be
reproduced from the release as published.
