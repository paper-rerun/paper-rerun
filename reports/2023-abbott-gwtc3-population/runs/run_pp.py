# Seeded wrapper around the authors' entry point (gwpopulation_pipe.data_analysis.main).
# The only addition is np.random.seed: dynesty (rstate None -> np.random) and the Gamma draw in
# compute_rate_posterior both use the global numpy RNG, so one seed makes the run traceable.
import sys
import numpy as np
seed = int(sys.argv[1])
np.random.seed(seed)
sys.argv = [sys.argv[0]] + sys.argv[2:]
from gwpopulation_pipe import data_analysis
data_analysis.main()
