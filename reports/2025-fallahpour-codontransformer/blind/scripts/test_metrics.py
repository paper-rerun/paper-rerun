"""One runnable check on the metric code.

The DTW check is the one that matters: the DP in recount.py is compared against a
brute-force enumeration of every monotone warping path, with the symmetric2
weighting (diagonal step costs 2*d, horizontal and vertical cost d, first cell once).
My first hand-written expectation for a 2x2 case was wrong, because I forgot the
path may take a vertical step, so the check is an independent implementation now
rather than a number I talked myself into.
"""
import os
import random
import sys
from functools import lru_cache

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from recount import codons, jaccard, similarity, dtw

assert codons("ATGAAATAA") == ["ATG", "AAA", "TAA"]
assert codons("ATGAAATA") == ["ATG", "AAA"], "a trailing partial codon is dropped"

a, b = codons("ATGAAATAA"), codons("ATGAAGTAA")
assert jaccard(a, b) == 2 / 4, jaccard(a, b)  # shared {ATG,TAA}; union adds AAA,AAG
assert abs(similarity(a, b) - 100 * 2 / 3) < 1e-12
assert jaccard(a, a) == 1.0 and similarity(a, a) == 100.0

d, n, m = dtw([1.0, 2.0, 3.0], [1.0, 2.0, 3.0])
assert d == 0.0 and (n, m) == (3, 3), (d, n, m)


def brute(x, y):
    """Cheapest symmetric2 path cost, by exhaustive recursion."""

    @lru_cache(maxsize=None)
    def best(i, j):
        c = abs(x[i] - y[j])
        if i == 0 and j == 0:
            return c
        opts = []
        if i and j:
            opts.append(best(i - 1, j - 1) + 2 * c)
        if i:
            opts.append(best(i - 1, j) + c)
        if j:
            opts.append(best(i, j - 1) + c)
        return min(opts)

    return best(len(x) - 1, len(y) - 1)


rng = random.Random(20261111)
for _ in range(300):
    nx, ny = rng.randint(1, 7), rng.randint(1, 7)
    x = [round(rng.uniform(-1, 1), 3) for _ in range(nx)]
    y = [round(rng.uniform(-1, 1), 3) for _ in range(ny)]
    got, _, _ = dtw(x, y)
    want = brute(x, y)
    assert abs(got - want) < 1e-9, (x, y, got, want)

print("all metric checks passed (300 random DTW cases matched brute force)")
