"""Pull the AP@0.5 numbers the paper plots out of the saved result files (same indexing as paper/3.0/figures.py)"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
results = {}


def mean_sem(ap_at_05):
    return float(ap_at_05.mean()), float(ap_at_05.std() / len(ap_at_05)**0.5)


# Fig 2b,c: Drosophila wing, noise levels 2%, 3%, 5% laser power, example image iex=10 at 2%
flywing_file = HERE / "data/care/Projection_Flywing/test_data/cp_masks.npy"
if flywing_file.exists():
    dat = np.load(flywing_file, allow_pickle=True).item()
    # figures.py plots noise levels in the order [0, 2, 1] = proj_C0, proj_C3, proj_C1 = 2%, 3%, 5%
    for nl, power in [(0, "2%"), (2, "3%"), (1, "5%")]:
        results[f"flywing {power} noisy"] = mean_sem(dat["ap_noisy"][nl][:, 0])
        results[f"flywing {power} denoised"] = mean_sem(dat["ap_denoised"][nl][:, 0])
    results["flywing example iex=10 2% noisy"] = float(dat["ap_noisy"][0][10, 0])
    results["flywing example iex=10 2% denoised"] = float(dat["ap_denoised"][0][10, 0])
    results["flywing n_images"] = len(dat["clean"])

# Fig 3c,d: Tribolium, stacks 0,1,2 of the test tifs (paper axis says 0.2/0.3/0.5 mW), example iex=0 at nl=1
tribolium_file = HERE / "data/care/Denoising_Tribolium/test_data/cp_masks.npy"
if tribolium_file.exists():
    dat = np.load(tribolium_file, allow_pickle=True).item()
    for nl in range(3):
        results[f"tribolium level{nl} noisy"] = mean_sem(dat["ap_noisy"][nl][:, 0])
        results[f"tribolium level{nl} denoised"] = mean_sem(dat["ap_denoised"][nl][:, 0])
    results["tribolium example iex=0 level1 noisy"] = float(dat["ap_noisy"][1][0, 0])
    results["tribolium example iex=0 level1 denoised"] = float(dat["ap_denoised"][1][0, 0])
    results["tribolium n_images"] = len(dat["clean"])

# Fig 2d,e: two-photon ribo, dense = images 0-11, sparse = 12-19, example iex=3 at 4 frames (nl=2)
ribo_file = HERE / "data/ribo/ribo_denoise.npy"
if ribo_file.exists():
    dat = np.load(ribo_file, allow_pickle=True).item()
    for n, navg in enumerate(dat["navgs"]):
        for name, ifr in [("dense", slice(0, 12)), ("sparse", slice(12, 20))]:
            results[f"ribo {name} {navg}fr noisy"] = mean_sem(dat["ap_noisy"][n, ifr, 0])
            results[f"ribo {name} {navg}fr denoised"] = mean_sem(dat["ap_dn"][n, ifr, 0])
    results["ribo example iex=3 4fr noisy"] = float(dat["ap_noisy"][2, 3, 0])
    results["ribo example iex=3 4fr denoised"] = float(dat["ap_dn"][2, 3, 0])

for key, value in results.items():
    if isinstance(value, tuple):
        print(f"{key:45s} {value[0]:.3f} +- {value[1]:.3f}")
    else:
        print(f"{key:45s} {value}")
json.dump(results, open(HERE / "logs" / "results.json", "w"), indent=1)
