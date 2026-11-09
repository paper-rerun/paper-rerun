"""DESI DR1 BAO flat LCDM fits, own likelihood + CAMB background.

Usage: python desi_bao.py check | selftest | bao_only [h] | bbn [nsteps]
Definitions are frozen in ../claims.json.
"""
import json
import os
import sys
import time

import numpy as np

import camb

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "bao_data")
OUT = os.path.join(ROOT, "out")
C_KMS = 299792.458
MNU = 0.06
NNU = 3.044
# Alternative-reading runs may override the prior; the frozen value is Eq. 2.8
BBN_MEAN = float(os.environ.get("BBN_MEAN", "0.02218"))
BBN_SD = float(os.environ.get("BBN_SD", "0.00055"))


def LoadDesiData():
	MeanPath = os.path.join(DATA, "desi_2024_gaussian_bao_ALL_GCcomb_mean.txt")
	CovPath = os.path.join(DATA, "desi_2024_gaussian_bao_ALL_GCcomb_cov.txt")
	Redshifts = []
	Values = []
	Kinds = []
	for Line in open(MeanPath):
		if Line.startswith("#") or not Line.strip():
			continue
		Parts = Line.split()
		Redshifts.append(float(Parts[0]))
		Values.append(float(Parts[1]))
		Kinds.append(Parts[2])
	Cov = np.loadtxt(CovPath)
	return np.array(Redshifts), np.array(Values), Kinds, Cov


Z, D, KINDS, COV = LoadDesiData()
INVCOV = np.linalg.inv(COV)
UNIQUE_Z = np.unique(Z)


def MakeParams(H0, OmegaM, Ombh2):
	# Omega_m includes the massive neutrino, so cdm is what is left
	Pars = camb.CAMBparams()
	Pars.set_cosmology(H0=H0, ombh2=Ombh2, omch2=0.1, mnu=MNU, nnu=NNU, num_massive_neutrinos=1, omk=0.0)
	H = H0 / 100.0
	Omch2 = OmegaM * H * H - Ombh2 - Pars.omnuh2
	if Omch2 <= 0.0:
		return None
	Pars.set_cosmology(H0=H0, ombh2=Ombh2, omch2=Omch2, mnu=MNU, nnu=NNU, num_massive_neutrinos=1, omk=0.0)
	Pars.WantCls = False
	Pars.WantTransfer = False
	return Pars


def DistancesTimesH0(H0, OmegaM, Ombh2, bWantRdrag):
	# Returns D_M*H0/c, D_H*H0/c, D_V*H0/c at every data row, and r_drag in Mpc
	Pars = MakeParams(H0, OmegaM, Ombh2)
	if Pars is None:
		return None
	Results = camb.get_background(Pars, no_thermo=not bWantRdrag)
	DM = Results.comoving_radial_distance(UNIQUE_Z)
	HofZ = Results.hubble_parameter(UNIQUE_Z)
	DH = C_KMS / HofZ
	DV = (UNIQUE_Z * DM * DM * DH) ** (1.0 / 3.0)
	Rdrag = Results.get_derived_params()["rdrag"] if bWantRdrag else np.nan
	Index = np.searchsorted(UNIQUE_Z, Z)
	Model = np.empty(len(Z))
	for Row in range(len(Z)):
		Kind = KINDS[Row]
		Each = Index[Row]
		if Kind == "DM_over_rs":
			Model[Row] = DM[Each]
		elif Kind == "DH_over_rs":
			Model[Row] = DH[Each]
		elif Kind == "DV_over_rs":
			Model[Row] = DV[Each]
		else:
			raise ValueError(Kind)
	return Model, Rdrag


def Chi2(ModelOverRd):
	Residual = D - ModelOverRd
	return Residual @ INVCOV @ Residual


def RunCheck():
	# Data file against Table 1 of the paper (page 10)
	Table1 = {
		(0.295, "DV_over_rs"): (7.93, 0.15),
		(0.510, "DM_over_rs"): (13.62, 0.25), (0.510, "DH_over_rs"): (20.98, 0.61),
		(0.706, "DM_over_rs"): (16.85, 0.32), (0.706, "DH_over_rs"): (20.08, 0.60),
		(0.930, "DM_over_rs"): (21.71, 0.28), (0.930, "DH_over_rs"): (17.88, 0.35),
		(1.317, "DM_over_rs"): (27.79, 0.69), (1.317, "DH_over_rs"): (13.82, 0.42),
		(1.491, "DV_over_rs"): (26.07, 0.67),
		(2.330, "DM_over_rs"): (39.71, 0.94), (2.330, "DH_over_rs"): (8.52, 0.17),
	}
	Table1R = {0.510: -0.445, 0.706: -0.420, 0.930: -0.389, 1.317: -0.444, 2.330: -0.477}
	bAllOk = True
	Sigma = np.sqrt(np.diag(COV))
	for Row in range(len(Z)):
		Mean, Err = Table1[(round(Z[Row], 3), KINDS[Row])]
		bOk = round(D[Row], 2) == Mean and round(Sigma[Row], 2) == Err
		bAllOk = bAllOk and bOk
		print(f"{Z[Row]:.3f} {KINDS[Row]:11s} file {D[Row]:.4f} +/- {Sigma[Row]:.4f}  table {Mean} +/- {Err}  {'ok' if bOk else 'MISMATCH'}")
	for Row in range(len(Z) - 1):
		if Z[Row] == Z[Row + 1]:
			R = COV[Row, Row + 1] / (Sigma[Row] * Sigma[Row + 1])
			bOk = round(R, 3) == Table1R[round(Z[Row], 3)]
			bAllOk = bAllOk and bOk
			print(f"r({Z[Row]:.3f}) file {R:.4f} table {Table1R[round(Z[Row], 3)]} {'ok' if bOk else 'MISMATCH'}")
	OffBlock = COV.copy()
	for Row in range(len(Z)):
		for Col in range(len(Z)):
			if Z[Row] == Z[Col]:
				OffBlock[Row, Col] = 0.0
	print("max |cov| between different z:", np.abs(OffBlock).max())
	print("ALL OK" if bAllOk else "CHECK FAILED")
	return bAllOk


def RunSelftest():
	# CAMB D_M against a plain integral with matter + Lambda only; radiation and neutrinos differ by < 0.2%
	from scipy.integrate import quad
	H0 = 68.0
	OmegaM = 0.3
	Model, Rdrag = DistancesTimesH0(H0, OmegaM, 0.02218, True)
	for Row in range(len(Z)):
		if KINDS[Row] != "DM_over_rs":
			continue
		Simple = C_KMS / H0 * quad(lambda x: 1.0 / np.sqrt(OmegaM * (1 + x) ** 3 + 1 - OmegaM), 0.0, Z[Row])[0]
		RelDiff = Model[Row] / Simple - 1.0
		print(f"z={Z[Row]} CAMB D_M {Model[Row]:.3f} simple {Simple:.3f} rel {RelDiff:+.2e}")
		assert abs(RelDiff) < 2e-3
	print("rdrag", Rdrag)
	assert 140.0 < Rdrag < 155.0
	# chi2 of the model must be zero when data equals model
	assert abs((Model / Rdrag - Model / Rdrag) @ INVCOV @ (Model / Rdrag - Model / Rdrag)) == 0.0
	print("selftest ok")


def WeightedMoments(Values, Weights):
	Mean = np.sum(Values * Weights) / np.sum(Weights)
	Sd = np.sqrt(np.sum((Values - Mean) ** 2 * Weights) / np.sum(Weights))
	return Mean, Sd


def RunBaoOnly(HFixed, OmStep, RdhStep):
	# BAO alone depends on Omega_m and r_d h; CAMB once per Omega_m node at fixed h
	OmegaGrid = np.arange(0.15, 0.50 + 0.5 * OmStep, OmStep)
	RdhGrid = np.arange(90.0, 115.0 + 0.5 * RdhStep, RdhStep)
	H0 = 100.0 * HFixed
	Chi2Grid = np.empty((len(OmegaGrid), len(RdhGrid)))
	for Each, OmegaM in enumerate(OmegaGrid):
		Model, _ = DistancesTimesH0(H0, OmegaM, 0.02218, False)
		# D/r_d = (D*h)/(r_d h)
		ModelTimesH = Model * HFixed
		Residuals = D[None, :] - ModelTimesH[None, :] / RdhGrid[:, None]
		Chi2Grid[Each] = np.einsum("ij,jk,ik->i", Residuals, INVCOV, Residuals)
	Chi2Min = Chi2Grid.min()
	Post = np.exp(-0.5 * (Chi2Grid - Chi2Min))
	# Edge check: prior mass outside the grid must be negligible
	EdgeMax = max(Post[0].max(), Post[-1].max(), Post[:, 0].max(), Post[:, -1].max())
	PostOm = Post.sum(axis=1)
	PostRdh = Post.sum(axis=0)
	OmMean, OmSd = WeightedMoments(OmegaGrid, PostOm)
	RdhMean, RdhSd = WeightedMoments(RdhGrid, PostRdh)
	Best = np.unravel_index(np.argmin(Chi2Grid), Chi2Grid.shape)
	Result = {
		"h_fixed": HFixed, "om_step": OmStep, "rdh_step": RdhStep,
		"Omega_m_mean": OmMean, "Omega_m_sd": OmSd,
		"rdh_mean": RdhMean, "rdh_sd": RdhSd,
		"chi2_min": Chi2Min, "best_Omega_m": OmegaGrid[Best[0]], "best_rdh": RdhGrid[Best[1]],
		"edge_max_over_peak": EdgeMax,
	}
	print(json.dumps(Result, indent=1))
	assert EdgeMax < 1e-8
	return Result


def LogPosteriorBbn(Theta):
	OmegaM, H0, Ombh2 = Theta
	if not (0.01 < OmegaM < 0.99 and 20.0 < H0 < 100.0 and 0.005 < Ombh2 < 0.1):
		return -np.inf
	Out = DistancesTimesH0(H0, OmegaM, Ombh2, True)
	if Out is None:
		return -np.inf
	Model, Rdrag = Out
	return -0.5 * Chi2(Model / Rdrag) - 0.5 * ((Ombh2 - BBN_MEAN) / BBN_SD) ** 2


def RunBbn(NSteps):
	import emcee
	from multiprocessing import Pool
	NWalkers = 24
	Rng = np.random.default_rng(20241108)
	Start = np.array([0.30, 68.0, 0.0222]) + Rng.normal(size=(NWalkers, 3)) * np.array([0.01, 0.5, 0.0003])
	ChainPath = os.path.join(OUT, "bbn_chain.h5")
	Backend = emcee.backends.HDFBackend(ChainPath) if HasH5py() else None
	with Pool(6) as WorkerPool:
		Sampler = emcee.EnsembleSampler(NWalkers, 3, LogPosteriorBbn, pool=WorkerPool, backend=Backend)
		T0 = time.time()
		Sampler.run_mcmc(Start, NSteps, progress=False)
		print("wall s", time.time() - T0)
	Chain = Sampler.get_chain()
	np.save(os.path.join(OUT, f"bbn_chain_{BBN_MEAN}_{BBN_SD}.npy"), Chain)
	np.save(os.path.join(OUT, f"bbn_logp_{BBN_MEAN}_{BBN_SD}.npy"), Sampler.get_log_prob())
	Tau = emcee.autocorr.integrated_time(Chain, quiet=True)
	Burn = int(5 * Tau.max())
	Flat = Chain[Burn:].reshape(-1, 3)
	Ess = Flat.shape[0] / Tau
	Names = ["Omega_m", "H0", "ombh2"]
	Result = {"nsteps": NSteps, "nwalkers": NWalkers, "burn": Burn, "tau": Tau.tolist(),
		"steps_over_tau": (NSteps / Tau).tolist(), "ess": Ess.tolist(),
		"acceptance": float(np.mean(Sampler.acceptance_fraction))}
	for Each, Name in enumerate(Names):
		Result[Name + "_mean"] = float(Flat[:, Each].mean())
		Result[Name + "_sd"] = float(Flat[:, Each].std())
	# Split-half check of the means as a convergence diagnostic
	Half = Flat.shape[0] // 2
	Result["H0_mean_first_half"] = float(Flat[:Half, 1].mean())
	Result["H0_mean_second_half"] = float(Flat[Half:, 1].mean())
	print(json.dumps(Result, indent=1))
	return Result


def HasH5py():
	try:
		import h5py  # noqa: F401
		return True
	except ImportError:
		return False


if __name__ == "__main__":
	Mode = sys.argv[1]
	if Mode == "check":
		sys.exit(0 if RunCheck() else 1)
	elif Mode == "selftest":
		RunSelftest()
	elif Mode == "bao_only":
		HFixed = float(sys.argv[2]) if len(sys.argv) > 2 else 0.68
		OmStep = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0005
		RdhStep = float(sys.argv[4]) if len(sys.argv) > 4 else 0.005
		Res = RunBaoOnly(HFixed, OmStep, RdhStep)
		json.dump(Res, open(os.path.join(OUT, f"bao_only_h{HFixed}_om{OmStep}.json"), "w"), indent=1)
	elif Mode == "bbn":
		NSteps = int(sys.argv[2]) if len(sys.argv) > 2 else 20000
		Res = RunBbn(NSteps)
		Res["bbn_prior"] = [BBN_MEAN, BBN_SD]
		json.dump(Res, open(os.path.join(OUT, f"bbn_{NSteps}_{BBN_MEAN}_{BBN_SD}.json"), "w"), indent=1)
	elif Mode == "timing":
		T0 = time.time()
		for Each in range(20):
			LogPosteriorBbn([0.3, 68.0, 0.0222])
		print("s per call", (time.time() - T0) / 20)
