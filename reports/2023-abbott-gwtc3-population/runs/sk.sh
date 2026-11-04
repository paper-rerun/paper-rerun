#!/bin/bash
# Compare sampler_kwargs, priors and metadata of both our result files against the published result
source /mnt/e/Ciencia/noturno/2023-abbott-gwtc3-population/env/activate.sh
cd /mnt/e/Ciencia/noturno/2023-abbott-gwtc3-population
python - <<'PY'
import json
name = "o1o2o3_mass_c_iid_mag_iid_tilt_powerlaw_redshift_result.json"
pub = json.load(open("sources/analyses/PowerLawPeak/" + name))
skip = {"live_points", "print_func"}
for seed in (101, 202):
    ours = json.load(open("runs/pp_seed%d/result/%s" % (seed, name)))
    print("=== seed", seed)
    n_diff = 0
    for k in sorted(set(pub["sampler_kwargs"]) | set(ours["sampler_kwargs"])):
        if k in skip: continue
        a, b = pub["sampler_kwargs"].get(k, "<absent>"), ours["sampler_kwargs"].get(k, "<absent>")
        if str(a) != str(b):
            n_diff += 1
            print("DIFF sampler_kwargs", k, "published", a, "ours", b)
    print("sampler_kwargs differences (excluding %s): %d" % (sorted(skip), n_diff))
    print("sampler_kwargs ours:", {k: v for k, v in ours["sampler_kwargs"].items() if k not in skip})
    print("priors equal:", pub["priors"] == ours["priors"])
    for k in sorted(set(pub["priors"]) | set(ours["priors"])):
        if pub["priors"].get(k) != ours["priors"].get(k):
            print("PRIOR DIFF", k, "\n  pub ", pub["priors"].get(k), "\n  ours", ours["priors"].get(k))
    print("models", ours["meta_data"]["models"], "n events", len(ours["meta_data"]["event_ids"]), ours["meta_data"]["event_ids"] == pub["meta_data"]["event_ids"])
    lm = ours["meta_data"]["loaded_modules"]
    print({k: lm.get(k) for k in ["gwpopulation", "gwpopulation_pipe", "bilby", "bilby_pipe", "cupy", "numpy", "scipy", "astropy", "dynesty", "pandas"]})
PY
