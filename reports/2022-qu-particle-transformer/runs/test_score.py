"""Self-check for the Rej reading in score.py on a hand-made ROC: python -I test_score.py"""
import sys

import numpy as np

sys.path.insert(0, '/mnt/e/Ciencia/noturno/2022-qu-particle-transformer/runs')
from score import roc_readings  # noqa: E402

# 4 signal jets at 0.9, 0.8, 0.7, 0.6 and 10 background jets, two of them above 0.75
y = np.array([1, 1, 1, 1] + [0] * 10)
score = np.array([0.9, 0.8, 0.7, 0.6, 0.85, 0.76, 0.5, 0.4, 0.3, 0.2, 0.1, 0.05, 0.02, 0.01])
r = roc_readings(y, score, 0.5)
main = r['main_first_point_tpr_ge_X']
# At TPR = 0.5 the cut sits at 0.8: background 0.85 passes, 0.76 does not, so k = 1, Rej = 10
assert main['tpr'] == 0.5, main
assert main['k_qcd'] == 1.0, main
assert abs(main['rej'] - 10.0) < 1e-9, main
assert r['n_jets_tied_at_threshold'] == 1
print('ok', main)
