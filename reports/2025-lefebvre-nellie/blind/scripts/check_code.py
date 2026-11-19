"""Blind check of the released Nellie multi_grid measurement code.

Run with:  python -I check_code.py <analysis.py> <multi_grid.py> <utils.py> <out.txt>
Loads the released functions verbatim by path so the demonstrations use their code,
not a paraphrase of it.
"""
import importlib.util
import sys
import io
import numpy as np
from scipy import ndimage as ndi

OUT = io.StringIO()


def say(*a):
    print(*a, file=OUT)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    # multi_grid.py imports comparisons.simulations.utils at module level; stub it.
    spec.loader.exec_module(mod)
    return mod


def main():
    analysis_path, multigrid_path, utils_path, out_path = sys.argv[1:5]

    import types
    for name in ("skimage", "skimage.morphology", "tifffile", "ome_types"):
        if name not in sys.modules:
            m = types.ModuleType(name)
            m.__path__ = []
            sys.modules[name] = m
    sys.modules["tifffile"].tifffile = sys.modules["tifffile"]
    sys.modules["skimage"].morphology = sys.modules["skimage.morphology"]

    analysis = load(analysis_path, "released_analysis")
    check_IoU = analysis.check_IoU

    # make `from comparisons.simulations.utils import ...` resolvable for multi_grid
    utils = load(utils_path, "released_utils")
    pkg = types.ModuleType("comparisons")
    pkg.__path__ = []
    sim = types.ModuleType("comparisons.simulations")
    sim.__path__ = []
    sys.modules["comparisons"] = pkg
    sys.modules["comparisons.simulations"] = sim
    sys.modules["comparisons.simulations.utils"] = utils
    multigrid = load(multigrid_path, "released_multigrid")

    # ---------------------------------------------------------------- C8
    # 500^3 is the measured volume; check_IoU strips 5 voxels each side and then
    # splits into 10 sections per axis. Build the smallest array with the same
    # geometry: 10 sections of 50 -> 500, plus the 5-voxel pad -> 510.
    # check_IoU hardcodes 10 sections per axis and strips a 5-voxel pad, so the
    # geometry is preserved by any 10*s+10 cube. s=20 -> 210^3, section crop 18^3.
    def blank():
        return np.zeros((210, 210, 210), dtype=np.int32)

    say("=== C8: fp = len(unique) - 1 goes negative when a section has no background ===")
    gt = blank()
    out = blank()
    # section (0,0,0) occupies [5:55] in each axis; its measured crop is [6:54].
    # gt: fill half of the crop. output: a single label covering the WHOLE crop,
    # so label 0 never appears in unique_labels for that section.
    gt[6:24, 6:24, 6:15] = 1
    out[6:24, 6:24, 6:24] = 7
    f1, iou = check_IoU(gt, out, is_label=True)
    say("section (0,0,0): measured crop is 18x18x18; gt fills 18x18x9 of it;")
    say("output is ONE label filling the whole crop (no background voxel left)")
    say(f"  true IoU  = {9/18:.4f} (gt is half the label)")
    say(f"  check_IoU max_iou = {iou[0,0,0]:.4f}  -> matched, above the 0.1 gate")
    say(f"  correct F1 = 1.0 (tp=1, fp=0, fn=0)")
    say(f"  check_IoU F1      = {f1[0,0,0]:.4f}   <-- WRONG")
    # same thing but leave one background voxel in the crop
    out2 = blank()
    out2[6:24, 6:24, 6:24] = 7
    out2[6, 6, 6] = 0
    f1b, ioub = check_IoU(gt, out2, is_label=True)
    say(f"  identical output with ONE background voxel added: F1 = {f1b[0,0,0]:.4f}, IoU = {ioub[0,0,0]:.4f}")
    say(f"  -> the score flips on the presence of a single zero voxel.")
    say("")

    # ---------------------------------------------------------------- C9
    say("=== C9: the 'len(unique_labels) < 100' bail-out forces F1=0 and IoU=0 ===")
    gt = blank()
    gt[6:24, 6:24, 6:15] = 1
    base = blank()
    base[6:24, 6:24, 6:15] = 1          # a perfect match, label 1
    f1, iou = check_IoU(gt, base, is_label=True)
    say(f"perfect single match:                    F1 = {f1[0,0,0]:.4f}  IoU = {iou[0,0,0]:.4f}")
    for n_specks in (97, 98, 99):
        frag = base.copy()
        lab = 2
        placed = 0
        # isolated single voxels inside the same crop, far from the object
        for z in range(7, 23, 2):
            for y in range(7, 23, 2):
                for x in range(17, 23, 2):
                    if placed >= n_specks:
                        break
                    frag[z, y, x] = lab
                    lab += 1
                    placed += 1
                if placed >= n_specks:
                    break
            if placed >= n_specks:
                break
        f1, iou = check_IoU(gt, frag, is_label=True)
        n_labels = len(np.unique(frag[6:24, 6:24, 6:24]))
        say(f"same match + {n_specks} specks (unique labels incl. 0 = {n_labels:3d}): "
            f"F1 = {f1[0,0,0]:.4f}  IoU = {iou[0,0,0]:.4f}")
    say("  -> at 100 unique labels the best match is never looked for: IoU is reported")
    say("     as 0 although the identical object is present and perfectly segmented.")
    say("")

    # ---------------------------------------------------------------- C10
    say("=== C10: np.isin(gt_coords, label_coords).all(axis=1) is not row membership ===")
    gt_coords = np.array([[1, 2, 3]])
    label_coords = np.array([[3, 1, 2], [2, 3, 1]])   # no row equals [1,2,3]
    test = np.sum(np.isin(gt_coords, label_coords).all(axis=1))
    say(f"gt coord {gt_coords.tolist()} vs label coords {label_coords.tolist()}")
    say(f"  rows actually shared: 0")
    say(f"  released pre-filter says shared = {test}  -> non-overlapping label is NOT skipped")
    # and an overlapping label always passes
    gt_coords = np.array([[4, 5, 6], [7, 8, 9]])
    label_coords = np.array([[7, 8, 9]])
    say(f"  overlapping case passes too: {np.sum(np.isin(gt_coords, label_coords).all(axis=1))} >= 1")
    say("  -> the filter is only ever too permissive, so max_iou is still correct;")
    say("     the defect costs run time, not accuracy.")
    say("")

    # ---------------------------------------------------------------- C7
    say("=== C7: which image axis carries which property ===")
    # Reproduce the generator's placement loop with distinguishable values,
    # 2x2x2 grid instead of 10x10x10.
    g = 2
    img = np.zeros((g * 50 + 10, g * 50 + 10, g * 50 + 10), dtype=np.uint16)
    thickness_v = [2.0, 10.0]
    length_v = [8.0, 40.0]
    intensity_v = [6553, 58982]
    placed = {}
    ct = 0
    for ix in range(g):
        cl = 0
        for iy in range(g):
            ci = 0
            for iz in range(g):
                thickness = thickness_v[ct]
                length = length_v[cl]
                intensity = intensity_v[ci]
                placed[(ix, iy, iz)] = (thickness, length, intensity)
                sx, sy, sz = ix * 50 + 5, iy * 50 + 5, iz * 50 + 5
                img[sx:sx + 50, sy:sy + 50, sz:sz + 50] = intensity
                ci += 1
            cl += 1
        ct += 1
    say("generator: cell (axis0=ix, axis1=iy, axis2=iz) -> (thickness, length, intensity)")
    for k in sorted(placed):
        say(f"  {k} -> {placed[k]}")
    varies = {0: set(), 1: set(), 2: set()}
    for axis, name in ((0, "axis0"), (1, "axis1"), (2, "axis2")):
        for prop_i, prop in enumerate(("thickness", "length", "intensity")):
            vals = {placed[k][prop_i] for k in placed if k[axis] == 0}
            vals1 = {placed[k][prop_i] for k in placed if k[axis] == 1}
            if vals != vals1 and len(vals) == 1 and len(vals1) == 1:
                varies[axis].add(prop)
    say(f"property determined by axis0: {sorted(varies[0])}")
    say(f"property determined by axis1: {sorted(varies[1])}")
    say(f"property determined by axis2: {sorted(varies[2])}")
    say("check_IoU loop order / array indices are [thickness, intensity, length],")
    say("i.e. axis1 is called 'intensity' and axis2 'length'; visualize.py then slices")
    say("stats[...][:, level, :] and calls `level` an intensity level.")
    say("")

    # ---------------------------------------------------------------- C11
    say("=== C11: the Gaussian noise is clipped to positive before being added ===")
    rng = np.random.default_rng(0)
    for std in (8.0, 256.0, 8192.0):
        n = rng.normal(0, std, 2_000_000)
        clipped = np.clip(n, 0, 65535)
        say(f"std={std:8.0f}: nominal mean 0, sd {std:8.1f} | "
            f"as added mean {clipped.mean():9.2f} sd {clipped.std():8.1f} | "
            f"std/sqrt(2pi) = {std/np.sqrt(2*np.pi):9.2f}")
    say("  -> half-normal. Background offset grows linearly with the nominal std,")
    say("     so the sweep changes background level and noise together.")
    # and confirm the released function does it
    frame = np.zeros((1, 32, 32, 32), dtype=np.uint16)
    noisy = utils.add_noise(frame[0], psf_sigma=0, gaussian_mean=0, gaussian_std=1000.0,
                            apply_poisson=False)
    say(f"  released add_noise on an all-zero volume, std=1000: min={noisy.min():.0f} "
        f"mean={noisy.mean():.1f} (expected ~{1000/np.sqrt(2*np.pi):.0f}, min 0)")
    say("")

    # ---------------------------------------------------------------- C12
    say("=== C12: create_skeleton_sub_volume clips to length-1, not to the volume ===")
    for length in (4, 8, 20, 26, 40, 50):
        sv = multigrid.create_skeleton_sub_volume(length=length)
        c = np.argwhere(sv)
        say(f"length={length:3d}: n_vox={len(c):3d} "
            f"axis0 {c[:,0].min():2d}-{c[:,0].max():2d}  "
            f"axis1 {c[:,1].min():2d}-{c[:,1].max():2d}  "
            f"axis2 {c[:,2].min():2d}-{c[:,2].max():2d}  "
            f"(uncentred: expected ~25 +/- 5 on axis1/2)")
    say("  -> for length < 26 the curve is pinned to the clip value length-1, i.e. the")
    say("     object sits at the corner of its cell and the curvature is destroyed.")
    say("     Cells with length < 11 also put voxels within 10 of the cell edge.")
    say("")

    open(out_path, "w", encoding="utf-8").write(OUT.getvalue())


if __name__ == "__main__":
    main()
