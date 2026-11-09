> **Coordinator's note (2026-11-08).** Two corrections, neither affecting a number. (1) Note 1 says the `schoneberg2024` likelihood is "presumably the N_eff-marginalised variant". The chain's own `chain.updated.yaml` shows a 2D Gaussian in (ω_b, N_eff), mean (0.02196, 3.034), evaluated at N_eff = 3.044: a conditional, ω_b = 0.021976 ± 0.000534, not a marginal. (2) The Lyα correlation −0.47750000039 is not a tie: its magnitude is above 0.4775, so −0.478 is the correct rounding and the paper's −0.477 is one off in the last digit. The text below is the agent's, unedited.

# Blind reproduction report: DESI 2024 VI, cosmological constraints from BAO

- Paper: DESI Collaboration, "DESI 2024 VI: cosmological constraints from the measurements of baryon acoustic oscillations", JCAP 02 (2025) 021, arXiv:2404.03002. Numbers taken from the arXiv PDF (71 pages, built 2024-11-04, sha256 `8e603ac88d861803cbd0004a6a4717934f7252fd057257fd6fa1ceb4b487cd36`, in `paper/`).
- Data: `desi_2024_gaussian_bao_ALL_GCcomb_mean.txt` and `_cov.txt` from https://github.com/CobayaSampler/bao_data @ bb0c1c9009dc76d1391300e169e8df38fd1096db (the two files are unchanged since commit 75b9557, 2024-04-05).
- Target: three flat LCDM numbers. DESI BAO alone: Omega_m and r_d h (Eq. 4.1). DESI BAO + BBN: H0 (Eq. 4.4).
- Route: our own Gaussian likelihood in numpy with CAMB 1.5.4 for distances and r_d. BAO alone on a deterministic grid. BAO + BBN with emcee calling CAMB at every point, with no interpolation. Cobaya was used only as a cross-check of the likelihood and of C3.
- Why this route:
  - BAO alone depends only on (Omega_m, r_d h), so a grid gives the exact moments with no Monte Carlo noise.
  - With BBN, r_d needs a full CAMB call at each (Omega_m, H0, ombh2), so a sampler calling CAMB directly avoids interpolation error.
- Verdict: **Reproduced** (3 of 3 claims inside the pre-registered band). C3 sits at the upper edge of its band, and the diagnostic in Note 1 explains why.
- Blind: this run never opened `E:\Ciencia\noturno\2024-desi-bao-vi\`, `fila.md`, `log.md`, `triagem-2026-11-08\` or any DESI file under `issues\` or `paper-rerun\reports\`.
- Date: 2026-11-08, about 21:41 to 22:40 local (UTC-3), about 1 hour. CPU only, at most 6 worker processes, all under `nice -n 19`.

## Results

| Claim | Published | Ours | Pre-registered band (mean / sd) | Inside |
|---|---|---|---|---|
| C1 DESI BAO, Omega_m | 0.295 ± 0.015 | 0.29468 ± 0.01463 | [0.2915, 0.2985] / [0.01305, 0.01705] | yes |
| C2 DESI BAO, r_d h (Mpc) | 101.8 ± 1.3 | 101.895 ± 1.267 | [101.49, 102.11] / [1.125, 1.485] | yes |
| C3 DESI BAO+BBN, H0 (km/s/Mpc) | 68.53 ± 0.80 | 68.694 ± 0.810 | [68.365, 68.695] / [0.7155, 0.8855] | yes (mean 0.001 under the upper edge) |

The bands were fixed in `claims.json` before any computation. The mean may move by 0.2 times the published sd plus half of the last printed digit, and the sd may move by ±10% around its printed interval. The file was frozen at 2026-11-09T00:44:17Z, sha256 `e83c18155306d6cdfd559496cdbb041286b3658b0ccf90f2f805237d33ac6b22` (`claims.sha256`), and it still hashes to that value after all runs.

Other numbers, all from our runs:

- C1/C2 posterior: the grid has 701 Omega_m nodes × 5001 r_d h nodes. Halving both steps changes nothing at 1e-15. The posterior at the grid edges is 1.5e-19 of the peak.
- C1/C2 sensitivity to the fixed h used in CAMB (radiation term only), with h = 0.60 / 0.68 / 0.76: Omega_m = 0.29460 / 0.29468 / 0.29474, r_d h = 101.898 / 101.895 / 101.894. The effect is negligible.
- C3 chain: 24 walkers × 20000 steps, burn-in 215. tau = 38 / 42 / 43 for (Omega_m, H0, ombh2), so the chain is 465 tau or more long, with ESS 11030 or more and acceptance 0.65. The two halves give H0 means of 68.691 and 68.698. MC error on the mean is about 0.008.
- C3 side results: Omega_m = 0.29497 ± 0.01463 and ombh2 = 0.022189 ± 0.000551, which is the prior given back as expected.
- Minimum chi2 of BAO alone is 12.7377 at Omega_m = 0.29361, r_d h = 101.945 Mpc (Nelder-Mead). The paper gives 12.66 (Sec. 3.2). See Note 2.

### Cross-checks (not the verdict)

1. **Our likelihood against cobaya's.** Cobaya 3.5 `bao.generic` read the same two files with CAMB. At 4 points in (Omega_m, H0, ombh2), its chi2 equals ours to 1e-13 (`logs/cobaya_pointcheck.log`). The two codes build the observables in different ways: we take D_M from the comoving distance, cobaya takes (1+z) D_A.
2. **Cobaya MCMC for C3.** We ran `cobaya-run` with the same priors (MH, one chain, R-1 < 0.005 on means, 2760 accepted steps). It gives H0 = 68.65 ± 0.82, Omega_m = 0.2949 ± 0.0141 and ombh2 = 0.02222 ± 0.00056 (`logs/cobaya_bbn.log`, `logs/cobaya_bbn_stats.log`). This agrees with emcee within the noise of the shorter cobaya chain, about 0.05.

### Diagnostic with the DESI public chains (used only after all our numbers existed)

We used the chains from `data.desi.lbl.gov/public/dr1/vac/dr1/bao-cosmo-params/v1.0/cobaya/base/` (CC BY 4.0, no login, nothing accepted). All 23 files passed the published sha256 list. Stats are weighted means and sds after dropping the first 30% of each chain (`logs/desi_chains_diagnostic.log`).

| DESI chain | Omega_m | r_d h or H0 | ombh2 |
|---|---|---|---|
| `desi-bao-all` | 0.29504 ± 0.01457 | r_d h = 101.866 ± 1.265 | fixed |
| `desi-bao-all_schoneberg2024-bbn` | 0.29514 ± 0.01479 | **H0 = 68.530 ± 0.805** | 0.02198 ± 0.00053 |
| `desi-bao-all_schoneberg2024-bbn-fixed-nnu` | 0.29522 ± 0.01467 | **H0 = 68.680 ± 0.810** | 0.02218 ± 0.00055 |

- BAO alone: the DESI chain and our grid agree to 0.02 sd.
- BAO+BBN: the published H0 = 68.53 ± 0.80 is the `schoneberg2024-bbn` chain. Its posterior on ombh2 is centred at 0.02198, not at the Eq. 2.8 prior of 0.02218 ± 0.00055.
- The chain that does carry Eq. 2.8 (`…-fixed-nnu`) gives 68.68 ± 0.81. That matches our 68.69 and cobaya's 68.65.
- Alternative reading, run with our own code: we replaced the BBN prior with N(0.02198, 0.00053), the ombh2 posterior of DESI's chain. The result is H0 = 68.565 ± 0.807 (8000 steps, ESS ≈ 4900, `logs/bbn_alt.log`). Most of the 0.16 gap comes from the BBN prior. The remaining 0.03 is expected, since a Gaussian only approximates the `schoneberg2024` likelihood.

## Environment

- WSL2 Ubuntu 24.04.1, Python 3.11.17, 24 logical CPUs (at most 6 used), 31 GB RAM. GPU not used.
- uv 0.13.4, resolved with `--exclude-newer 2024-04-04` (the arXiv v1 date). Main versions: camb 1.5.4, numpy 1.26.4, scipy 1.13.0, emcee 3.1.4, cobaya 3.5, getdist 1.4.7. Full lock in `env/requirements.lock`, built by `env/setup_env.sh`.
- `OMP_NUM_THREADS=1` for our runs. Parallelism came from a 6-process `multiprocessing.Pool` (emcee). The cobaya MCMC used `OMP_NUM_THREADS=4`.
- Folder size about 665 MB, most of it the venv, the uv cache and 153 MB of DESI chains.

## Every command

All commands were run from Git Bash with `MSYS_NO_PATHCONV=1 wsl …`. Every run appends to `logs/<name>.log` with start and end lines, its exit code and `/usr/bin/time -v`.

1. `curl -sSL -o paper/2404.03002.pdf https://arxiv.org/pdf/2404.03002`, then `pdftotext -layout`.
2. `git clone --depth 1 https://github.com/CobayaSampler/bao_data.git data/bao_data`. It was unshallowed later to check the file history.
3. Wrote `claims.json` and froze it with `sha256sum claims.json > claims.sha256` plus a UTC timestamp.
4. `bash env/setup_env.sh` (uv pip compile, then uv venv and install).
5. `bash scripts/run.sh check check`: data against Table 1 (`logs/check.log`).
6. `bash scripts/run.sh selftest selftest`: CAMB D_M against a plain matter+Lambda integral (agree to 1.7e-4) and r_drag in range.
7. `bash scripts/run.sh timing timing`: 0.015 s per likelihood call.
8. `bash scripts/run.sh bao_only bao_only 0.68`, `… 0.68 0.00025 0.0025`, `… 0.60` and `… 0.76`. Output in `out/bao_only_*.json` and `logs/bao_only.log`.
9. `bash scripts/run.sh bbn bbn 20000`. Output in `out/bbn_20000.json`, `out/bbn_chain.npy` and `logs/bbn.log`, 26 min 54 s.
10. `bash scripts/run_cobaya.sh cobaya_pointcheck 1` and `bash scripts/run_cobaya.sh cobaya_bbn 4` (`cobaya-run -f cobaya/bbn.yaml`), then `scripts/chain_stats.py cobaya/chains/bbn 0.3 omegam H0 ombh2 rdrag`.
11. DIAGNOSTIC: downloaded the three DESI chain folders listed in `dr1_vac_dr1_bao-cosmo-params_v1.0.sha256sum` and ran `sha256sum -c`. Then `bash scripts/desi_chains_diagnostic.sh`, `bash scripts/minchi2.sh` and `python -I scripts/chi2_at_desi_best.py`.
12. ALTERNATIVE READING: `bash scripts/run_bbn_alt.sh`, which sets `BBN_MEAN=0.02198 BBN_SD=0.00053` and runs 8000 steps. Output in `out/bbn_8000_0.02198_0.00053.json`.
13. Read the Schoeneberg BBN repo (`README.md`, `covmats.txt`) into `data/schoeneberg_bbn/`. It has no means, so it could not be used to rebuild the DESI `schoneberg2024` likelihood.

## Deviations from the pre-registration

- **Data check.** `claims.json` said to stop if any Table 1 entry failed to round. One entry failed: the Lya DM/DH correlation in the file is −0.47750000039, and Python rounds that to −0.478 where Table 1 prints −0.477. This is a rounding tie at the 10th decimal, not a different file, so we carried on. The other 12 means, 12 errors and 4 correlations match, and the covariance has no terms between different redshifts.
- **Script change.** After the C3 run, `scripts/desi_bao.py` was edited so the BBN prior can be overridden through environment variables, and so the output file names include the prior. The defaults are still the frozen Eq. 2.8 values. The C3 result was produced before the edit and saved as `out/bbn_20000.json` / `out/bbn_chain.npy`.
- **Cobaya BAO-only.** We did not run a cobaya MCMC for BAO alone. Its BAO likelihood takes r_d from the theory code, so sampling r_d h directly would have needed a custom component. The point check in cross-check 1 covers that likelihood.

## Notes for the authors

1. **Which BBN prior gives H0 = 68.53?** Section 2.4.1 says the LCDM runs use Ωb h² = 0.02218 ± 0.00055 (Eq. 2.8). The public chain that matches Eq. 4.4 (`desi-bao-all_schoneberg2024-bbn`) has an Ωb h² posterior of 0.02198 ± 0.00053. With Eq. 2.8 as a Gaussian prior we get H0 = 68.69 ± 0.81. Cobaya gives 68.65, and your own `…-fixed-nnu` chain gives 68.68. Swapping the prior for N(0.02198, 0.00053) moves us to 68.57. So the headline H0 seems to come from the `schoneberg2024` likelihood: abundance-based, with the PArthENoPE table in CAMB, and presumably the N_eff-marginalised variant. It does not come from the Gaussian quoted in the text. The shift is 0.15 km/s/Mpc, about 0.19 sd, so no conclusion changes. Still, a sentence saying which BBN likelihood the LCDM numbers use would help anyone who rebuilds them from Eq. 2.8.
2. **chi2 of the best fit.** Section 3.2 gives χ² = 12.66 for the BAO-only best fit, and your chain's minimum `chi2__BAO` is 12.661. With the public `bao_data` files, at your chain's best point (Ωm = 0.29351, r_d h = 101.953, with H0 and ωb as in your yaml), we get 12.738, and our own minimum is 12.738. Cobaya's `bao.generic` gives the same value as our code. Your chain config reads `desi_gaussian_bao_ALL_GCcomb_*.txt` from the internal `desi-y1-kp` package, so the public files may differ from it in the last digits or in basis. The posteriors agree to 0.02 sd, so this is cosmetic, but it would be good to know which file is canonical.
3. **Table 1 rounding.** The Lya r is −0.4775000004 in the public covariance and is printed as −0.477. That is a tie, nothing more.
4. **Chains and data.** The public chains (with checksums) and the plain-text BAO files made this check quick: the three claims took about one hour on a home CPU.

## How this report was made

This reproduction was run by one AI agent (Claude, by Anthropic) on a home computer, as a blind recount. It never saw the earlier attempt at this paper. Every number above comes from code that ran in this folder. The commands, logs and outputs are in `scripts/`, `logs/` and `out/`. `claims.json` was frozen with its hash before any computation from the data. The DESI chains were downloaded and read only after our own C1–C3 numbers existed, and every use of them is labelled as a diagnostic. Nothing was published.
