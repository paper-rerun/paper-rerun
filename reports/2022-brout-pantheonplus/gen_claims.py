# Write claims.json for the Pantheon+ pre-registration (run once, then freeze with claims.sha256)
import datetime
import hashlib
import json
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
SOURCES = os.path.join(ROOT, "sources")


def sha256_of(path):
	return hashlib.sha256(open(path, "rb").read()).hexdigest()


source_files = [
	"arxiv_v2.pdf",
	"arxiv_v2_src.tgz",
	"arxiv_v2_src/main.tex",
	"arxiv_v2.txt",
	"tree.json",
	"fetch_sources.py",
	"fetch_manifest.json",
	"cobaya_pantheonplus.py",
	"cosmosis_gaussian_likelihood_main.py",
	"released_chain_stats.py",
	"released_chain_stats.json",
	"repo/5_COSMOLOGY/cosmosis_likelihoods/Pantheon+_only_cosmosis_likelihood.py",
	"repo/5_COSMOLOGY/cosmosis_likelihoods/Pantheon+SH0ES_cosmosis_likelihood.py",
	"repo/5_COSMOLOGY/chains/Pantheon+Only/Pantheon+only_FlatLambdaCDM.txt.gz",
	"repo/5_COSMOLOGY/chains/Pantheon+Only/Pantheon+only_LambdaCDM.txt.gz",
	"repo/5_COSMOLOGY/chains/Pantheon+Only/Pantheon+only_FlatwCDM.txt.gz",
	"repo/5_COSMOLOGY/chains/Pantheon+Only/Pantheon+only_Flatw0waCDM.txt.gz",
	"repo/5_COSMOLOGY/chains/Pantheon+SH0ES/Pantheon+SH0ES_FlatLambdaCDM.txt.gz",
	"repo/4_DISTANCES_AND_COVAR/README",
	"repo/5_COSMOLOGY/README",
]
source_files_sha256 = {"sources/" + f: sha256_of(os.path.join(SOURCES, f)) for f in source_files}

chain_stats = json.load(open(os.path.join(SOURCES, "released_chain_stats.json")))


def released(chain, parameter):
	entry = chain_stats[chain]
	return {
		"chain": "sources/repo/5_COSMOLOGY/chains/" + chain,
		"sampler": "emcee, 16 walkers, %d steps written" % entry["steps"],
		"no_burnin": entry["burnin_0"][parameter],
		"drop_first_30pct": entry["burnin_30pct"][parameter],
	}


ONLY = "Pantheon+Only/Pantheon+only_"

# Tolerance rules, fixed here before any fit is run
PRIMARY_TOL = {
	"mean": {"reproduced_abs": 0.003, "partial_abs": 0.009},
	"width": {"reproduced_abs": 0.002, "partial_abs": 0.004},
	"basis": "Paper value has 3 decimals (rounding 0.0005). PolyChord with 1000-3000 independent samples gives a Monte Carlo error on the mean of 0.018/sqrt(1000) = 0.0006. The authors' own released emcee chain for the same likelihood gives 0.3314-0.3319 (diff 0.0021-0.0026 from 0.334), so 0.003 (0.17 sigma) is the closest bound that the authors' own released run meets; 0.009 = 0.5 sigma is the partial bound, as proposed by triage. Width: std of the released chain is 0.0179 (30% burn-in) to 0.0208 (no burn-in); 0.002 is about 11% of 0.018, above the ~2% sampling noise of a std estimate from 1000 samples plus the 0.0005 rounding.",
}
SECONDARY_TOL = {
	"mean": {"reproduced_sigma": 0.25, "partial_sigma": 0.5},
	"width": {"reproduced_rel": 0.20, "partial_rel": 0.40},
	"basis": "Secondary posteriors are wide and non-Gaussian with prior edges, so the bound is in units of the paper's own 68% half-width sigma_p (for asymmetric errors, the side towards which our mean lies). The authors' released emcee chains differ from Table 3 by 0.17-0.18 sigma (LambdaCDM Omega_m), 0.17 sigma (LambdaCDM Omega_Lambda), 0.29 sigma (FlatwCDM Omega_m) and 0.11 sigma (FlatwCDM w), so 0.25 sigma is about the authors' own run-to-run spread; 0.5 sigma is partial. Widths: each error component (or the std for a symmetric +/-) within 20% of the paper's is reproduced, within 40% partial; the released chains match the paper widths to within 1-5%.",
}

definitions = [
	{
		"id": "D-DATA",
		"choice": "Distances: Pantheon+_Data/4_DISTANCES_AND_COVAR/Pantheon+SH0ES.dat at commit c447f0fea703fcd0fff57de5000947b5ca81286b (file unchanged since 7fc680548d, 05/07/2022), 579,283 B, md5 2049b142e6aad384470b3364aa10f3fa, git blob cce857db0c15e9ce7a0e0ce77452b6ff62af969a; 1701 data rows. Covariance: Pantheon+SH0ES_STAT+SYS.cov, same commit, 33,284,960 B, md5 041bdb6638841794fc2d7caa88dd66eb, git blob d1a1498154e7ba826df14bdbef35ebcb7f5efba1. Download from raw.githubusercontent.com and check size, md5 and git blob sha1 before use.",
		"quote": "the 1701 x 1701 systematic distance covariance matrix is shown in Fig. 6 (Sec. 4, arXiv v2 p. 14-15); the information used to create the Hubble diagram as well as the covariance matrix is publicly available (pantheonplussh0es.github.io)",
		"ambiguity": "The paper points to pantheonplussh0es.github.io without a version. The GitHub DataRelease repo is the authors' release; its files are dated 05/07/2022, before arXiv v2 (14/11/2022) whose numbers match the journal. arXiv v1 gave 0.338 +/- 0.018 (kept commented in the v2 LaTeX); a result near 0.338 would point to a data-version mismatch, not a sampler issue. VizieR J/ApJ/938/110 is a mirror and is not used.",
	},
	{
		"id": "D-COV",
		"choice": "First line is N = 1701; the next 1701^2 lines are the matrix elements read in row-major order and reshaped to (1701, 1701). Rows and columns are then subset with the same mask as the data (D-CUT). Use the full STAT+SYS covariance; never the *_err_DIAG columns.",
		"quote": "chi^2 = Delta D^T C_stat+syst^-1 Delta D (Eq. 9, Sec. 2.3, arXiv v2 p. 6); Unless otherwise stated, constraints on cosmological parameters include both statistical and systematic uncertainties. (Sec. 4, p. 15)",
		"ambiguity": "Read order confirmed by the authors' likelihood code (nested loops i, j over origlen, reading one value per line) and by the author in DataRelease issue #12. The STAT+SYS file already contains the Cepheid-host covariance for calibrator rows (issue #4); the 10 calibrators above z = 0.01 therefore enter the SN-only fit with that term, as in the authors' code.",
	},
	{
		"id": "D-CUT",
		"choice": "Pantheon+ only fits keep rows with zHD > 0.01 (strict inequality, on the zHD column, not zCMB). Expected 1590 rows. No upper redshift cut (max zHD in the file is 2.26). The Pantheon+SH0ES likelihood (optional claim O1) keeps rows with zHD > 0.01 OR IS_CALIBRATOR == 1.",
		"quote": "The nominal minimum redshift is 0.01 for Pantheon+ cosmology fits without SH0ES. ... The nominal maximum redshift is 2.4 for all fits. (Fig. 16 caption, arXiv v2 p. 24)",
		"ambiguity": "The text of Eq. 9 says 'the vector of 1701 SN distance modulus residuals' (p. 6), which describes the full file; the Fig. 16 caption and the released likelihood (self.ww = (data['zHD']>0.01)) both apply the 0.01 cut for SN-only fits, so the cut is used. The paper does not say strict vs inclusive or which redshift column; both are taken from the code. Cobaya's sn.pantheonplus names the column zcmb but reads zHD, same cut.",
	},
	{
		"id": "D-MODEL-MU",
		"choice": "Predicted observable for each kept row: m_model = 5 log10[(1+zHD)(1+zHEL) D_A(zHD) / Mpc] + 25 + M, compared to the m_b_corr column. D_A is the angular-diameter distance at zHD in the trial cosmology, so (1+zHD)(1+zHEL) D_A = (1+zHEL)/(1+zHD) x d_L(zHD).",
		"quote": "mu_model(z_i) = 5 log(d_L(z_i)/10 pc), where d_L is the model-based luminosity distance ... d_L(z) = (1+z) c int_0^z dz'/H(z') (Eqs. 11-12, Sec. 2.3, arXiv v2 p. 6)",
		"ambiguity": "The paper writes a single redshift; the released likelihood uses zHD for the cosmological distance and adds the heliocentric factor (1+zHEL)/(1+zHD) (theory_ynew = 5 log10((1+zcmb)(1+zhel) D_A(zcmb)) + 25 with zcmb = zHD). The code form is used, as in Cobaya and DataRelease issue #11. M here is the free offset (absolute magnitude), not the SALT2 M of Eq. 1.",
	},
	{
		"id": "D-LIKELIHOOD",
		"choice": "ln L = -chi^2/2 with chi^2 = r^T C^-1 r, r = m_b_corr - m_model, C the cut STAT+SYS covariance (inverted once, float64; Cholesky solve allowed as an exact equivalent). No log-determinant term (constant covariance). Out-of-prior points and cosmologies where the distance is undefined (E(z)^2 <= 0 for some z <= max zHD) get ln L = -inf.",
		"quote": "-2 ln(L) = chi^2 = Delta D^T C_stat+syst^-1 Delta D (Eq. 9, Sec. 2.3, arXiv v2 p. 6)",
		"ambiguity": "CosmoSIS GaussianLikelihood defaults to include_norm = False (checked in sources/cosmosis_gaussian_likelihood_main.py, current main; the 2022 version the authors ran is not pinned), which matches Eq. 9. The -inf rule for undefined cosmologies stands in for CAMB failing on those points in the authors' run.",
	},
	{
		"id": "D-BACKGROUND",
		"choice": "Main: analytic background, H(z)/H0 = E(z) = sqrt(Om (1+z)^3 + Ok (1+z)^2 + Ode f(z)), no radiation or neutrinos, Ode = 1 - Om - Ok; f(z) = 1 (Lambda), (1+z)^(3(1+w)) (wCDM), (1+z)^(3(1+w0+wa)) exp(-3 wa z/(1+z)) (w0waCDM, CPL). Comoving distance by numerical integration with relative error below 1e-6 at every data redshift; D_A = D_M/(1+z) with the curvature sinn for Ok != 0. Check (reported, not used for the verdict): CAMB background with the chain values.ini settings (omega_b 0.048, omnuh2 0.00083, 3 massive + 0.046 massless neutrinos, n_s 0.97, A_s 2.19e-9, tau 0.0697) for the primary claim, run only if it fits in 4 threads under nice; otherwise reported as not run.",
		"quote": "H(z) = H0 sqrt(Omega_M (1+z)^3 + Omega_Lambda (1+z)^(3(1+w))) (Eq. 13, p. 6); See Hogg for the forms of the expansion history H(z) used in the case that the assumption of flatness is relaxed. (p. 6)",
		"ambiguity": "The paper's Eq. 13 has no radiation; the authors' runs used CosmoSIS modules 'consistency camb pantheon' (chain headers), i.e. CAMB with radiation and massive neutrinos. The analytic form follows the paper's equation; the difference in E(z) is about 1e-4 over 0 < z < 2.3, expected to move Omega_m by well under 0.001. The paper writes w = w0 + wa(1+z) (p. 7); taken literally w diverges at high z. CosmoSIS/CAMB parameter wa is the CPL form w(a) = w0 + wa(1-a), so CPL is used and the paper formula is read as a typo.",
	},
	{
		"id": "D-PARAMS-PRIORS",
		"choice": "Sampled parameters and flat priors, from the [cosmological_parameters] and [supernova_params] blocks of the released chain headers: all models h0 in [0.55, 0.91] (H0 = 100 h0), M in [-20, -18]. FlatLambdaCDM: Om in [0.1, 0.9], Ok = 0, w = -1. LambdaCDM: Om in [0.1, 0.9], Ok in [-1, 1], OL = 1 - Om - Ok derived. FlatwCDM: Om in [0.1, 0.9], w in [-2, 0.5]. Flatw0waCDM: Om in [0.01, 0.9], w0 in [-2, 0.5], wa in [-4, 4] (main) and wa in [-2, 2] (variant). Flat models: OL = 1 - Om derived.",
		"quote": "FlatLambdaCDM: Omega_M is floated and we fix w = -1 and Omega_M + Omega_Lambda = 1. LambdaCDM: Omega_M and Omega_Lambda are floated and we fix w = -1. FlatwCDM: w and Omega_M are floated ... Flatw0waCDM: ... Omega_M, w0, wa are floated (Sec. 2.3, arXiv v2 p. 6-7)",
		"ambiguity": "The paper gives no prior ranges. They come from the released emcee chains, which are the only record of the authors' settings. For w0waCDM the two released chains disagree: Pantheon+only_Flatw0waCDM has wa in [-2, 2] and no use_ppf_w, while Pantheon+SH0ES_Flatw0waCDM has wa in [-4, 4] and use_ppf_w = T. The paper's own wa = -0.1 +0.9/-2.0 has its lower 68% edge at -2.1, outside [-2, 2], so the Table 3 run cannot have used [-2, 2]; [-4, 4] is the main choice. The released Pantheon+only w0waCDM chain gives Omega_m 0.213, w0 -0.82, wa 0.34, far from Table 3 (0.403, -0.93, -0.1); without PPF, CAMB cannot follow w crossing -1, which would cut the region wa < 0 with w0 > -1. That chain is not used as a reference for the w0waCDM claims. The LambdaCDM chains sample Omega_k (flat) rather than Omega_Lambda; the implied prior on OL at fixed Om is also flat, so this is followed as is.",
	},
	{
		"id": "D-NUISANCE-M-H0",
		"choice": "Main: sample M and h0 jointly with the cosmological parameters under the flat priors above and marginalise by ignoring them in the summaries (as in the released chains). Variant (reported): analytic marginalisation over M as in Cobaya sn.pantheonplus (C^-1 -> C^-1 - C^-1 1 (1^T C^-1 1)^-1 1^T C^-1), h0 fixed.",
		"quote": "The parameters M and H0 are degenerate when analyzing SNe alone. (p. 6)",
		"ambiguity": "Only the combination M - 5 log10(h0) enters. With bounded flat priors on both, the implied prior on that combination is a trapezoid, not flat; the analytic route uses an unbounded flat prior. Both are run; the main follows the authors' setup.",
	},
	{
		"id": "D-SAMPLER",
		"choice": "Main: nested sampling with PolyChord settings from the paper: 250 live points, num_repeats 30, precision criterion (evidence tolerance) 0.1, posterior weights from the sampler, boost_posteriors 10 as in the chain header ini. Implementation order: pypolychord if it builds in the uv environment; otherwise dynesty static NestedSampler with nlive 250, sample 'rslice', slices 30, dlogz 0.1. Seeds 1, 2, 3; the claim uses seed 1 and the spread over the 3 seeds is reported as Monte Carlo noise. Variant: emcee with 16 walkers and 10,000 steps (as in the chain header ini), first 30% of steps dropped as burn-in. All runs nice -n 19 with at most 4 threads/processes.",
		"quote": "We evaluate the likelihoods with the PolyChord sampler in the CosmoSIS package using 250 live points, 30 repeats, and an evidence tolerance requirement of 0.1. This resulted in converged chains containing 1000--3000 independent samples. (p. 6)",
		"ambiguity": "The released chains are emcee runs (headers: sampler = emcee, 16 walkers), not the PolyChord runs behind Table 3; they stop early (FlatLambdaCDM: 3100 of 10,000 steps) and give no burn-in. The 30% burn-in is our choice, fixed here, and the released-chain references are listed both with and without it. If neither PolyChord nor dynesty runs, the emcee variant becomes the main result and this is stated in the report.",
	},
	{
		"id": "D-SUMMARY",
		"choice": "Point value: weighted posterior mean. 68% interval: equal-tailed weighted 16th and 84th percentiles, reported as +(p84 - mean) / -(mean - p16). When the paper gives a symmetric +/- value, we compare that number to our weighted standard deviation, and also report the half-width (p84 - p16)/2. Rounded to the paper's number of decimals only for display; the comparison uses unrounded values.",
		"quote": "Summary of marginalized parameter constraints for Pantheon+ and other external probes. The mean and 68% confidence limit are provided for each cosmological parameter. (Table 3 notes, p. 17)",
		"ambiguity": "The paper does not say whether the 68% limits are equal-tailed or highest-density, nor whether symmetric +/- values are standard deviations. Equal-tailed percentiles around the mean is the main choice; a highest-density interval is also reported for the asymmetric claims.",
	},
	{
		"id": "D-TABLE-ROWS",
		"choice": "Omega_m, Omega_Lambda, w0, wa claims of Table 3 rows 1-4 are taken from the Pantheon+ only likelihood (no Cepheids); the H0 column is taken from the Pantheon+SH0ES likelihood.",
		"quote": "For a FlatwCDM model, from the SNe Ia alone (not including SH0ES Cepheid calibration) we find Omega_M = 0.309+0.063-0.069 and w = -0.90 +/- 0.14 as shown in the third row of Table 3 (Sec. 4, p. 15)",
		"ambiguity": "The Table 3 block is titled 'Pantheon+ & SH0ES - All Models', but the text and the LaTeX macro names (fLCDMOMPan vs fLCDMHPanSH, wwaOMPan vs wwaHPanSH) say Omega_m, w0 and wa come from SNe alone and H0 from the SH0ES run.",
	},
	{
		"id": "D-SH0ES-LIKELIHOOD",
		"choice": "Optional claim O1 only: rows with zHD > 0.01 or IS_CALIBRATOR == 1; for calibrator rows the prediction is CEPH_DIST + M; for the others it is D-MODEL-MU. Same STAT+SYS covariance subset, same priors as FlatLambdaCDM.",
		"quote": "Delta D'_i = mu_i - mu_i^Cepheid for i in Cepheid hosts, mu_i - mu_model(z_i) otherwise (Eq. 14, p. 6)",
		"ambiguity": "Eq. 15 adds C^Cepheid to the SN covariance; the released STAT+SYS file already contains it (README_4: 'also Cepheid host covariance'), so no extra matrix is added. Taken from Pantheon+SH0ES_cosmosis_likelihood.py.",
	},
]

claims = [
	{
		"id": "P1",
		"role": "primary",
		"quantity": "Omega_m, FlatLambdaCDM, Pantheon+ SNe Ia only, stat+syst",
		"paper_value": 0.334,
		"paper_error": {"plus": 0.018, "minus": 0.018, "form": "symmetric +/-"},
		"unit": "dimensionless",
		"location": "Table 3, row 'FlatLambdaCDM', column Omega_M (arXiv v2 p. 17); same value in abstract (p. 2), Sec. 4 (p. 15) and conclusions (p. 26)",
		"tolerance": PRIMARY_TOL,
		"conditions": {
			"model": "FlatLambdaCDM",
			"likelihood": "Pantheon+_only_cosmosis_likelihood.py logic (D-CUT, D-MODEL-MU, D-LIKELIHOOD)",
			"data": "D-DATA, 1590 rows after D-CUT",
			"checkpoint": "not applicable (Bayesian fit, no trained model)",
			"samples": "D-SAMPLER main, seed 1",
			"summary": "D-SUMMARY",
		},
		"derived_also_reported": "Omega_Lambda = 1 - Omega_m, paper 0.666 +/- 0.018",
		"authors_released_chain": released(ONLY + "FlatLambdaCDM.txt.gz", "omega_m"),
	},
	{
		"id": "S1",
		"role": "secondary",
		"quantity": "Omega_m, LambdaCDM (curvature free), Pantheon+ only",
		"paper_value": 0.306,
		"paper_error": {"plus": 0.057, "minus": 0.057, "form": "symmetric +/-"},
		"unit": "dimensionless",
		"location": "Table 3, row 'LambdaCDM', column Omega_M (p. 17); Sec. 4 text (p. 15)",
		"tolerance": SECONDARY_TOL,
		"conditions": {"model": "LambdaCDM, Om and Ok sampled (D-PARAMS-PRIORS)", "samples": "D-SAMPLER main, seed 1", "summary": "D-SUMMARY"},
		"authors_released_chain": released(ONLY + "LambdaCDM.txt.gz", "omega_m"),
	},
	{
		"id": "S2",
		"role": "secondary",
		"quantity": "Omega_Lambda, LambdaCDM, Pantheon+ only (derived 1 - Om - Ok)",
		"paper_value": 0.625,
		"paper_error": {"plus": 0.084, "minus": 0.084, "form": "symmetric +/-"},
		"unit": "dimensionless",
		"location": "Table 3, row 'LambdaCDM', column Omega_Lambda (p. 17)",
		"tolerance": SECONDARY_TOL,
		"conditions": {"model": "LambdaCDM", "samples": "same run as S1", "summary": "D-SUMMARY"},
		"authors_released_chain": released(ONLY + "LambdaCDM.txt.gz", "omega_lambda_derived"),
	},
	{
		"id": "S3",
		"role": "secondary",
		"quantity": "Omega_m, FlatwCDM, Pantheon+ only",
		"paper_value": 0.309,
		"paper_error": {"plus": 0.063, "minus": 0.069, "form": "asymmetric"},
		"unit": "dimensionless",
		"location": "Table 3, row 'FlatwCDM', column Omega_M (p. 17); Sec. 4 text (p. 15)",
		"tolerance": SECONDARY_TOL,
		"conditions": {"model": "FlatwCDM", "samples": "D-SAMPLER main, seed 1", "summary": "D-SUMMARY"},
		"derived_also_reported": "Omega_Lambda = 1 - Omega_m, paper 0.691 +0.069/-0.063",
		"authors_released_chain": released(ONLY + "FlatwCDM.txt.gz", "omega_m"),
	},
	{
		"id": "S4",
		"role": "secondary",
		"quantity": "w, FlatwCDM, Pantheon+ only",
		"paper_value": -0.90,
		"paper_error": {"plus": 0.14, "minus": 0.14, "form": "symmetric +/-"},
		"unit": "dimensionless",
		"location": "Table 3, row 'FlatwCDM', column w0 (p. 17); abstract (p. 2); Sec. 4 (p. 15)",
		"tolerance": SECONDARY_TOL,
		"conditions": {"model": "FlatwCDM", "samples": "same run as S3", "summary": "D-SUMMARY"},
		"authors_released_chain": released(ONLY + "FlatwCDM.txt.gz", "w"),
	},
	{
		"id": "S5",
		"role": "secondary_prior_sensitive",
		"quantity": "Omega_m, Flatw0waCDM, Pantheon+ only",
		"paper_value": 0.403,
		"paper_error": {"plus": 0.054, "minus": 0.098, "form": "asymmetric"},
		"unit": "dimensionless",
		"location": "Table 3, row 'Flatw0waCDM', column Omega_M (p. 17)",
		"tolerance": SECONDARY_TOL,
		"conditions": {"model": "Flatw0waCDM (CPL), wa prior [-4, 4] main, [-2, 2] variant", "samples": "D-SAMPLER main, seed 1", "summary": "D-SUMMARY"},
		"derived_also_reported": "Omega_Lambda = 1 - Omega_m, paper 0.597 +0.098/-0.054",
		"authors_released_chain_not_comparable": released(ONLY + "Flatw0waCDM.txt.gz", "omega_m"),
	},
	{
		"id": "S6",
		"role": "secondary_prior_sensitive",
		"quantity": "w0, Flatw0waCDM, Pantheon+ only",
		"paper_value": -0.93,
		"paper_error": {"plus": 0.15, "minus": 0.15, "form": "symmetric +/-"},
		"unit": "dimensionless",
		"location": "Table 3, row 'Flatw0waCDM', column w0 (p. 17); Sec. 4 (p. 15)",
		"tolerance": SECONDARY_TOL,
		"conditions": {"model": "Flatw0waCDM", "samples": "same run as S5", "summary": "D-SUMMARY"},
		"authors_released_chain_not_comparable": released(ONLY + "Flatw0waCDM.txt.gz", "w"),
	},
	{
		"id": "S7",
		"role": "secondary_prior_sensitive",
		"quantity": "wa, Flatw0waCDM, Pantheon+ only",
		"paper_value": -0.1,
		"paper_error": {"plus": 0.9, "minus": 2.0, "form": "asymmetric"},
		"unit": "dimensionless",
		"location": "Table 3, row 'Flatw0waCDM', column wa (p. 17); abstract (p. 2); Sec. 4 (p. 15)",
		"tolerance": SECONDARY_TOL,
		"conditions": {"model": "Flatw0waCDM", "samples": "same run as S5", "summary": "D-SUMMARY"},
		"note": "wa is close to prior-dominated; the paper value has one decimal, so its own rounding is +/-0.05.",
		"authors_released_chain_not_comparable": released(ONLY + "Flatw0waCDM.txt.gz", "wa"),
	},
	{
		"id": "O1",
		"role": "optional",
		"quantity": "H0, FlatLambdaCDM, Pantheon+SH0ES likelihood",
		"paper_value": 73.6,
		"paper_error": {"plus": 1.1, "minus": 1.1, "form": "symmetric +/-"},
		"unit": "km/s/Mpc",
		"location": "Table 3, row 'FlatLambdaCDM', column H0 (p. 17)",
		"tolerance": {
			"mean": {"reproduced_abs": 0.2, "partial_abs": 0.55},
			"width": {"reproduced_abs": 0.15, "partial_abs": 0.3},
			"basis": "Paper value has one decimal (rounding 0.05); the released Pantheon+SH0ES FlatLambdaCDM emcee chain gives 73.54 +/- 1.02, diff 0.06. 0.2 km/s/Mpc = 0.18 sigma; partial bound 0.5 sigma.",
		},
		"conditions": {"model": "FlatLambdaCDM", "likelihood": "D-SH0ES-LIKELIHOOD", "samples": "D-SAMPLER main, seed 1", "summary": "D-SUMMARY on H0 = 100 h0"},
		"authors_released_chain": released("Pantheon+SH0ES/Pantheon+SH0ES_FlatLambdaCDM.txt.gz", "h0"),
	},
]

document = {
	"stage": "pre-registration",
	"created_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
	"paper": {
		"title": "The Pantheon+ Analysis: Cosmological Constraints",
		"authors": "Brout, Scolnic, Popovic et al.",
		"venue": "ApJ 938, 110 (2022)",
		"doi": "10.3847/1538-4357/ac8e04",
		"preprint": "arXiv 2202.04077 v2 (14/11/2022), journal_ref ApJ 938 110; v1 (0.338) is not the target",
		"code": "https://github.com/PantheonPlusSH0ES/DataRelease @ c447f0fea703fcd0fff57de5000947b5ca81286b (main, 21/12/2022)",
		"likelihood_code": "Pantheon+_Data/5_COSMOLOGY/cosmosis_likelihoods/Pantheon+_only_cosmosis_likelihood.py (git blob 07d4ae5f24ae97b3416e12b17c666904b117156f)",
		"alternative_likelihood": "Cobaya sn.pantheonplus @ 9d087ab795240b416ebb3a2dd35868397b012d3c (git blob 3a29baf82bfe7ccbd1e16601963fb897cf1966dc)",
		"data_mirror": "VizieR J/ApJ/938/110 (not used)",
	},
	"target": "Table 3 (Results for Cosmological Models), mean and 68% interval, Pantheon+ SNe Ia only: FlatLambdaCDM Omega_m (primary), LambdaCDM Omega_m and Omega_Lambda, FlatwCDM Omega_m and w, Flatw0waCDM Omega_m, w0, wa; optional H0 from the Pantheon+SH0ES likelihood.",
	"source_files_sha256": source_files_sha256,
	"data_files_expected": {
		"Pantheon+_Data/4_DISTANCES_AND_COVAR/Pantheon+SH0ES.dat": {"bytes": 579283, "md5": "2049b142e6aad384470b3364aa10f3fa", "git_blob_sha1": "cce857db0c15e9ce7a0e0ce77452b6ff62af969a", "rows": 1701, "rows_after_cut": 1590},
		"Pantheon+_Data/4_DISTANCES_AND_COVAR/Pantheon+SH0ES_STAT+SYS.cov": {"bytes": 33284960, "md5": "041bdb6638841794fc2d7caa88dd66eb", "git_blob_sha1": "d1a1498154e7ba826df14bdbef35ebcb7f5efba1", "lines": 2893402},
	},
	"released_per_item_results_used": "The authors' released emcee chains (sources/repo/5_COSMOLOGY/chains, all 8 files, size and git blob sha1 checked in sources/fetch_manifest.json) were read for their ini headers (priors, sampler, CosmoSIS modules) and summarised in sources/released_chain_stats.json. They decided D-PARAMS-PRIORS and the tolerance bases. Nothing from our side was computed: no fit, no likelihood evaluation, data files not downloaded in this project yet.",
	"compute_budget": "Light mode: CPU only, nice -n 19, OMP/MKL/OPENBLAS/NUMEXPR threads = 4, MPI at most 4 ranks, no GPU. The CAMB check (D-BACKGROUND) runs only if it fits in that budget.",
	"definitions": definitions,
	"claims": claims,
	"verdict_rule": "Each claim is 'reproduced' when its mean and width both meet the reproduced bounds, 'partial' when both meet at least the partial bounds, otherwise 'not reproduced'. Overall: Reproduced = P1 reproduced and none of S1-S4 not reproduced. Partially reproduced = P1 partial, or P1 reproduced with at least one of S1-S4 not reproduced. Not reproduced = P1 not reproduced. S5-S7 (prior-sensitive w0waCDM) and O1 are reported one by one and do not change the overall verdict. Could not run = the main likelihood cannot be evaluated within the light-mode budget.",
	"out_of_scope": [
		"All Table 3 rows combining Pantheon+ with Planck or BAO (need external likelihoods and data)",
		"H0 for LambdaCDM, FlatwCDM and Flatw0waCDM with SH0ES (73.4, 73.5, 73.3); may be reported, not claims",
		"Stat-only contours (Fig. 8 dashed), systematic budget (Table 4), redshift-range scans (Fig. 16)",
	],
	"observations_from_paper_only": [
		"arXiv v2 LaTeX keeps older values commented out next to the active macros: FlatLambdaCDM Omega_m 0.338 (the v1 abstract value), LambdaCDM 0.277/0.570, Flatw0waCDM Omega_m 0.386, w0 -1.81, wa -0.4; a fit landing on these would point to older inputs.",
		"The text of Eq. 9 describes a vector of 1701 residuals while SN-only fits use the z > 0.01 subset (1590 rows).",
		"The w0waCDM definition in the text, w = w0 + wa(1+z), is not the CPL form used by CAMB.",
		"Released Pantheon+only Flatw0waCDM chain (wa prior [-2, 2], no PPF) sits about 2.5 sigma from the Table 3 Omega_m.",
	],
	"pre_registered": "2026-10-26, before any fit was run or any distance/covariance file was downloaded in this project",
}

with open(os.path.join(ROOT, "claims.json"), "w", encoding="ascii") as handle:
	json.dump(document, handle, indent=1)
print("written", os.path.join(ROOT, "claims.json"))
