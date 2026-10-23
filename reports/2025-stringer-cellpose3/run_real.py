"""Run the authors' real-data denoising analyses (paper/3.0/analysis.py) for Cellpose3 only.

real_examples() and real_examples_ribo() first run Cellpose3 (saving cp_masks.npy / ribo_denoise.npy)
and then train Noise2Self / Noise2Void baselines. We only want the Cellpose3 part, so the baseline
modules are replaced by an identity stub (no training). The resulting n2s_*/n2v_* files are NOT
baseline results and are deleted after the run.
"""
import sys
from pathlib import Path

# Headless: never open a window. The authors call plt.show(), which we turn into a savefig in logs/
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "repo" / "paper" / "3.0"))
import analysis

figure_count = [0]


def save_instead_of_show(*args, **kwargs):
    figure_count[0] += 1
    plt.savefig(HERE / "logs" / f"{sys.argv[1]}_ap_curves_{figure_count[0]}.png", dpi=100)
    plt.close("all")


plt.show = save_instead_of_show


class IdentityStub:
    # Return the noisy image unchanged, shaped like the real baseline output
    def __init__(self, add_axis):
        self.add_axis = add_axis

    def train_per_image(self, img, *args, **kwargs):
        if self.add_axis:
            return img[None]
        return img


analysis.noise2self = IdentityStub(add_axis=False)
analysis.noise2void = IdentityStub(add_axis=True)

which = sys.argv[1]
if which == "care":
    analysis.real_examples(str(HERE / "data" / "care"))
elif which == "ribo":
    analysis.real_examples_ribo(str(HERE / "data" / "ribo"))
