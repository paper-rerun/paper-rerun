# Print sampler kwargs (without live points), likelihood meta data and run statistics
import json
import sys
import numpy as np
with open(sys.argv[1]) as result_file:
    result = json.load(result_file)
sampler_kwargs = {key: value for key, value in result["sampler_kwargs"].items() if key != "live_points"}
print("sampler_kwargs", sampler_kwargs)
print("search keys", result["search_parameter_keys"], "fixed", result["fixed_parameter_keys"], "constraint", result["constraint_parameter_keys"])
print("likelihood meta", json.dumps(result["meta_data"]["likelihood"], default=str)[:3000])
print("run_statistics", json.dumps(result["meta_data"]["run_statistics"], default=str)[:1500])
print("loaded_modules", json.dumps(result["meta_data"]["loaded_modules"], default=str)[:3000])
print("information_gain", result.get("information_gain"), "log_bayes_factor", result.get("log_bayes_factor"))
