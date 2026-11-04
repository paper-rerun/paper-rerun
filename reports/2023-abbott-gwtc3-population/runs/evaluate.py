# Score the pre-registered claims (claims.json) on our result files. Usage: evaluate.py result1.json [result2.json ...]
import json
import sys
import numpy as np

base = "/mnt/e/Ciencia/noturno/2023-abbott-gwtc3-population"
claims = json.load(open(base + "/claims.json"))
published = json.load(open(base + "/sources/analyses/PowerLawPeak/o1o2o3_mass_c_iid_mag_iid_tilt_powerlaw_redshift_result.json"))

def quantiles(values):
    return dict(zip(["p05", "p50", "p95"], np.percentile(values, [5, 50, 95])))

def columns(result):
    post = result["posterior"]["content"]
    return {
        "C1_mu_m": np.array(post["mpp"]),
        "C2_rate_z0.2": np.array(post["rate"]) * 1.2 ** np.array(post["lamb"]),
        "S1_alpha": np.array(post["alpha"]),
        "S2_beta_q": np.array(post["beta"]),
        "S3_kappa": np.array(post["lamb"]),
    }

published_quantiles = {key: quantiles(values) for key, values in columns(published).items()}
summary = {}
for path in sys.argv[1:]:
    result = json.load(open(path))
    ours = {key: quantiles(values) for key, values in columns(result).items()}
    print("=" * 100)
    print(path)
    print("n posterior samples", len(result["posterior"]["content"]["mpp"]), "sampling_time_s", result.get("sampling_time"),
          "n likelihood", result.get("num_likelihood_evaluations"), "run_statistics", result["meta_data"].get("run_statistics"))
    run_pass = {}
    for claim in claims["claims"]:
        key = claim["id"]
        q = ours[key]
        pub = published_quantiles[key]
        paper = claim["paper_value"]
        paper_p05 = paper["median"] - paper["minus"]
        paper_p95 = paper["median"] + paper["plus"]
        line = "%-13s ours %.3f +%.3f -%.3f [%.3f, %.3f] | released %.3f [%.3f, %.3f] | paper %s +%s -%s [%.2f, %.2f]" % (
            key, q["p50"], q["p95"] - q["p50"], q["p50"] - q["p05"], q["p05"], q["p95"],
            pub["p50"], pub["p05"], pub["p95"], paper["median"], paper["plus"], paper["minus"], paper_p05, paper_p95)
        print(line)
        tol = claim["tolerance"]
        if "vs_released_result" in tol:
            rel = tol["vs_released_result"]
            d = {"median": q["p50"] - pub["p50"], "p05": q["p05"] - pub["p05"], "p95": q["p95"] - pub["p95"]}
            ok_rel = all(abs(d[k]) <= rel[k] for k in d)
            vp = tol["vs_paper"]
            dp = {"median": q["p50"] - paper["median"], "p05": q["p05"] - vp["p05_paper_value"], "p95": q["p95"] - vp["p95_paper_value"]}
            ok_paper = all(abs(dp[k]) <= vp[k] for k in dp)
            print("    vs released: dmedian %+.3f (tol %.2f) dp05 %+.3f (tol %.2f) dp95 %+.3f (tol %.2f) -> %s" % (
                d["median"], rel["median"], d["p05"], rel["p05"], d["p95"], rel["p95"], "PASS" if ok_rel else "FAIL"))
            print("    vs paper:    dmedian %+.3f (tol %.2f) dp05 %+.3f (tol %.2f, paper p05 %.2f) dp95 %+.3f (tol %.2f, paper p95 %.2f) -> %s" % (
                dp["median"], vp["median"], dp["p05"], vp["p05"], vp["p05_paper_value"], dp["p95"], vp["p95"], vp["p95_paper_value"], "PASS" if ok_paper else "FAIL"))
            run_pass[key] = dict(released=ok_rel, paper=ok_paper)
        else:
            dm = q["p50"] - paper["median"]
            d05 = q["p05"] - paper_p05
            d95 = q["p95"] - paper_p95
            ok = abs(dm) <= tol["median"] and abs(d05) <= tol["edges"] and abs(d95) <= tol["edges"]
            dr = {"median": q["p50"] - pub["p50"], "p05": q["p05"] - pub["p05"], "p95": q["p95"] - pub["p95"]}
            ok_r = abs(dr["median"]) <= tol["median"] and abs(dr["p05"]) <= tol["edges"] and abs(dr["p95"]) <= tol["edges"]
            print("    vs paper: dmedian %+.3f (tol %.2f) dp05 %+.3f dp95 %+.3f (tol %.2f) -> %s | same tolerances vs released: dmedian %+.3f dp05 %+.3f dp95 %+.3f -> %s" % (
                dm, tol["median"], d05, d95, tol["edges"], "PASS" if ok else "FAIL", dr["median"], dr["p05"], dr["p95"], "PASS" if ok_r else "FAIL"))
            run_pass[key] = dict(paper=ok, released=ok_r)
        summary.setdefault(path, {})[key] = dict(ours=q, pass_=run_pass[key])
    primary = run_pass["C1_mu_m"]["released"] and run_pass["C2_rate_z0.2"]["released"]
    print("PRIMARY (C1 and C2 vs released):", "PASS" if primary else "FAIL")
json.dump(summary, open(base + "/runs/evaluation_summary.json", "w"), indent=1, default=float)
