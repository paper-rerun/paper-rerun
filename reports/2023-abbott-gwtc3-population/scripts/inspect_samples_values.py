# Check the per-event samples: redshift range, mass range, weights, how many identical rows
import sys
import h5py
import numpy as np
with h5py.File(sys.argv[1], "r") as samples_file:
    original = samples_file["original"]
    for key in original:
        values = original[key][()]
        print(key, "min %.4g max %.4g nan %d" % (np.nanmin(values), np.nanmax(values), np.isnan(values).sum()))
