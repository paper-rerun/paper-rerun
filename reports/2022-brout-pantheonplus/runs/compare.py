"""Score every claim of claims.json against the fits in out/ and write results.json plus a markdown table.
Uses exactly the pre-registered tolerances and verdict rule; variants are reported, never scored.
"""
import json
import os
import numpy as np

ROOT = "/mnt/e/Ciencia/noturno/2022-brout-pantheonplus"
OUT = os.path.join(ROOT, "runs", "out")
claims = json.load(open(os.path.join(ROOT, "claims.json")))

# Claim id -> (config, parameter key in stats)
MAP = {"P1": ("flcdm", "Om"), "S1": ("lcdm", "Om"), "S2": ("lcdm", "OL"), "S3": ("fwcdm", "Om"),
       "S4": ("fwcdm", "w0"), "S5": ("fw0wa4", "Om"), "S6": ("fw0wa4", "w0"), "S7": ("fw0wa4", "wa"),
       "O1": ("sh0esflcdm", "H0")}


def load(run):
    p = os.path.join(OUT, run + ".json")
    return json.load(open(p)) if os.path.exists(p) else None


def grade(claim, st):
    pv = claim["paper_value"]
    pe = claim["paper_error"]
    tol = claim["tolerance"]
    sym = pe["form"] == "symmetric +/-"
    diff = st["mean"] - pv
    out = dict(diff=diff)
    if "reproduced_abs" in tol["mean"]:
        m_ok = abs(diff) <= tol["mean"]["reproduced_abs"]
        m_part = abs(diff) <= tol["mean"]["partial_abs"]
        dw = st["std"] - pe["plus"]
        out["width_diff"] = dw
        w_ok = abs(dw) <= tol["width"]["reproduced_abs"]
        w_part = abs(dw) <= tol["width"]["partial_abs"]
    else:
        sigma_p = pe["plus"] if diff > 0 else pe["minus"]
        out["diff_sigma"] = diff / sigma_p
        m_ok = abs(diff) / sigma_p <= tol["mean"]["reproduced_sigma"]
        m_part = abs(diff) / sigma_p <= tol["mean"]["partial_sigma"]
        if sym:
            rels = [st["std"] / pe["plus"] - 1.0]
        else:
            rels = [st["plus"] / pe["plus"] - 1.0, st["minus"] / pe["minus"] - 1.0]
        out["width_rel"] = rels
        w_ok = all(abs(r) <= tol["width"]["reproduced_rel"] for r in rels)
        w_part = all(abs(r) <= tol["width"]["partial_rel"] for r in rels)
    out["mean_grade"] = "reproduced" if m_ok else ("partial" if m_part else "not reproduced")
    out["width_grade"] = "reproduced" if w_ok else ("partial" if w_part else "not reproduced")
    if m_ok and w_ok:
        out["grade"] = "reproduced"
    elif m_part and w_part:
        out["grade"] = "partial"
    else:
        out["grade"] = "not reproduced"
    return out


def fmt(st, nd):
    return "%.*f +%.*f/-%.*f (std %.*f)" % (nd, st["mean"], nd, st["plus"], nd, st["minus"], nd, st["std"])


results = {}
rows = []
for c in claims["claims"]:
    cfg, key = MAP[c["id"]]
    main = load(cfg + "_dynesty_s1")
    r = dict(id=c["id"], quantity=c["quantity"], paper=c["paper_value"], paper_error=c["paper_error"])
    if main is None:
        r["status"] = "missing"
        results[c["id"]] = r
        continue
    st = main["stats"][key]
    r["ours"] = st
    r.update(grade(c, st))
    seeds = [load("%s_dynesty_s%d" % (cfg, s)) for s in (1, 2, 3)]
    r["seed_means"] = [s["stats"][key]["mean"] if s else None for s in seeds]
    r["seed_stds"] = [s["stats"][key]["std"] if s else None for s in seeds]
    em = load(cfg + "_emcee_s1")
    if em:
        r["emcee"] = em["stats"][key]
        r["emcee_grade"] = grade(c, em["stats"][key])["grade"]
    if cfg == "fw0wa4":
        v = load("fw0wa2_dynesty_s1")
        if v:
            r["wa_prior_2"] = v["stats"][key]
            r["wa_prior_2_grade"] = grade(c, v["stats"][key])["grade"]
        v = load("fw0wa2_emcee_s1")
        if v:
            r["wa_prior_2_emcee"] = v["stats"][key]
    if c["id"] == "P1":
        v = load("flcdmmargM_dynesty_s1")
        if v:
            r["margM"] = v["stats"]["Om"]
            r["margM_grade"] = grade(c, v["stats"]["Om"])["grade"]
        p = os.path.join(OUT, "camb_check_flcdm_dynesty_s1.json")
        if os.path.exists(p):
            cc = json.load(open(p))
            r["camb_check"] = dict(Om_camb=cc["Om_camb"], Om_analytic=cc["Om_analytic"],
                                   max_abs_dmu=cc["max_abs_dmu_mag_at_Om0334_h07"], ess_after=cc["ess_after"])
    results[c["id"]] = r
    nd = 1 if c["id"] == "O1" else 3
    rows.append("| %s | %s | %s | %s | %+.4f | %s |" % (
        c["id"], c["quantity"], "%s +%s/-%s" % (c["paper_value"], c["paper_error"]["plus"], c["paper_error"]["minus"]),
        fmt(st, nd + 1), r["diff"], r["grade"]))

g = {k: results[k].get("grade") for k in results}
if g.get("P1") is None:
    overall = "incomplete"
elif g["P1"] == "not reproduced":
    overall = "Not reproduced"
elif g["P1"] == "partial":
    overall = "Partially reproduced"
elif any(g.get(k) == "not reproduced" for k in ("S1", "S2", "S3", "S4")):
    overall = "Partially reproduced"
elif all(g.get(k) is not None for k in ("S1", "S2", "S3", "S4")):
    overall = "Reproduced"
else:
    overall = "incomplete"
results["overall"] = overall
json.dump(results, open(os.path.join(ROOT, "runs", "results.json"), "w"), indent=1)
print("| Claim | Quantity | Paper | Ours (mean +p84/-p16, std) | Diff | Grade |")
print("|---|---|---|---|---|---|")
print("\n".join(rows))
print("overall:", overall)
for k, r in results.items():
    if k == "overall":
        continue
    print(k, {kk: vv for kk, vv in r.items() if kk not in ("quantity", "paper_error", "ours")})
