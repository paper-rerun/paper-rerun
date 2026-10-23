"""Check: weighted auPRC on a 5% negative sample lands near the full-set auPRC on synthetic data"""
import sys, os
import numpy as np
from sklearn.metrics import average_precision_score
sys.path.insert(0, os.path.dirname(__file__))
from score_sample import WeightedAuprc

RandomGenerator = np.random.default_rng(1)
Labels = np.r_[np.ones(3000), np.zeros(2_000_000)].astype(int)
Scores = np.r_[RandomGenerator.normal(4.5, 1, 3000), RandomGenerator.normal(0, 1, 2_000_000)]
FullAuprc = average_precision_score(Labels, Scores)
Keep = (Labels == 1) | (RandomGenerator.random(len(Labels)) < 0.05)
SampledAuprc = WeightedAuprc(Labels[Keep], Scores[Keep], 0.05)
print(f"full={FullAuprc:.4f} weighted_sample={SampledAuprc:.4f} unweighted_sample={average_precision_score(Labels[Keep], Scores[Keep]):.4f}")
assert abs(FullAuprc - SampledAuprc) < 0.02
