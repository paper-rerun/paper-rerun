"""Compare our chi2 with cobaya's bao.generic chi2 at a few points (cross-check, not verdict)"""
import os
import sys

import numpy as np
import yaml
from cobaya.model import get_model

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import desi_bao  # noqa: E402

Info = yaml.safe_load(open(os.path.join(desi_bao.ROOT, "cobaya", "bbn.yaml")))
Info.pop("output")
Info.pop("sampler")
Model = get_model(Info)
Points = [(0.295, 68.53, 0.02218), (0.25, 65.0, 0.0215), (0.35, 72.0, 0.0230), (0.30, 68.0, 0.02218)]
for OmegaM, H0, Ombh2 in Points:
	Logp = Model.loglikes({"omegam": OmegaM, "H0": H0, "ombh2": Ombh2}, as_dict=True)[0]
	CobayaChi2 = -2.0 * Logp["bao.generic"]
	Out, Rdrag = desi_bao.DistancesTimesH0(H0, OmegaM, Ombh2, True)
	OurChi2 = desi_bao.Chi2(Out / Rdrag)
	print(f"Om={OmegaM} H0={H0} ombh2={Ombh2}: cobaya chi2 {CobayaChi2:.6f} ours {OurChi2:.6f} diff {CobayaChi2 - OurChi2:+.2e}")
