"""Per-seed distance from the paper in units of the paper's half-width, and emcee chain length in autocorrelation times"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
r = json.load(open(os.path.join(HERE, "results.json")))
for cid in ["S1", "S2", "S3", "S4", "S5", "S6", "S7"]:
    c = r[cid]
    out = []
    for m in c["seed_means"]:
        side = c["paper_error"]["plus"] if m > c["paper"] else c["paper_error"]["minus"]
        out.append("%.4f (%+.3f sigma)" % (m, (m - c["paper"]) / side))
    print(cid, " / ".join(out))
for run in ["flcdm", "lcdm", "fwcdm", "fw0wa4", "fw0wa2", "sh0esflcdm"]:
    d = json.load(open(os.path.join(HERE, "out", run + "_emcee_s1.json")))
    kept = d["nsteps"] - d["burnin_steps"]
    tau = d["autocorr_time"]
    print("%s emcee: tau %.0f-%.0f steps, kept %d steps = %.1f-%.1f tau, effective samples ~%.0f"
          % (run, min(tau), max(tau), kept, kept / max(tau), kept / min(tau), d["nwalkers"] * kept / max(tau)))
