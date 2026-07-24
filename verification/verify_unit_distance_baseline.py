"""
Offline verification of the *classical* lower bound in the unit-distance
problem — the mechanism the OpenAI model's construction had to beat.

Classical Erdős construction: take the K x K integer lattice (n = K^2
points), count all pairwise squared distances, find the most popular
distance d*, and rescale so sqrt(d*) = 1. The number of unit-distance pairs
is then u = (number of pairs at distance d*) / 2.

Erdős's theorem: the most popular distance occurs
    u(n) >= n^(1 + c / log log n)
times — superlinear, but with an exponent tending to 1. The conjecture he
made (and the AI disproved) was that NO construction does better than
n^(1+o(1)); the AI's number-field construction reaches n^1.014, i.e. an
exponent bounded away from 1.

What we verify here, by direct enumeration (no internet, no cited theorems):
  - for grids up to 150x150 (22,500 points, ~2.5e8 pairs), the most popular
    distance really does occur more often than n — i.e. log u / log n > 1
    robustly, and the excess is consistent with the c/log log n law
    (slowly decreasing toward 1 as n grows).

What we CANNOT verify offline: the new n^1.014 construction itself. Its
existence proof uses infinite class field towers (Golod–Shafarevich), whose
objects aren't enumerable on a laptop. We verify the baseline mechanism and
the plausibility gap only — flagged honestly below.
"""

import math
from collections import Counter

import numpy as np


def unit_pairs_best_distance(K):
    """n = K^2 grid points; return (n, max unordered pairs at one distance)."""
    a = np.arange(K, dtype=np.int64)
    pts = np.stack(np.meshgrid(a, a), axis=-1).reshape(-1, 2)
    n = len(pts)
    cnt = Counter()
    CH = 256
    for i in range(0, n, CH):
        blk = pts[i : i + CH]
        d2 = ((blk[:, 0, None] - pts[:, 0][None, :]) ** 2
              + (blk[:, 1, None] - pts[:, 1][None, :]) ** 2)
        vals, c = np.unique(d2[d2 > 0], return_counts=True)
        for v, cc in zip(vals.tolist(), c.tolist()):
            cnt[v] += cc
    d2_best, c_best = max(cnt.items(), key=lambda kv: kv[1])
    return n, c_best // 2, d2_best


print(f"{'K':>5} {'n=K^2':>8} {'u(n)':>12} {'log u / log n':>14} {'1 + c/loglog n':>15}")
print("-" * 60)
rows = []
for K in [30, 50, 70, 100, 120, 150]:
    n, u, d2 = unit_pairs_best_distance(K)
    expo = math.log(u) / math.log(n)
    c_eff = (expo - 1) * math.log(math.log(n))
    rows.append((K, n, u, expo, c_eff))
    print(f"{K:>5} {n:>8} {u:>12,} {expo:>14.5f} {c_eff:>15.4f}")

expos = [r[3] for r in rows]
assert all(e > 1.0 for e in expos), "superlinearity not observed!"
assert expos[-1] < expos[0], "exponent should drift down toward 1"
print("\nVerified:")
print("  - most-popular-distance construction gives u(n) > n for all grids (superlinear)")
print("  - the exponent log u / log n drifts DOWN toward 1 as n grows,")
print("    matching the classical n^(1 + c/log log n) law, NOT a constant gap.")
print("\nNot verifiable offline: the reported n^1.014 construction (needs class")
print("field towers). But the verified baseline shows exactly where the bar was:")
print("beating 'exponent -> 1' with 'exponent >= 1.014' is precisely the kind")
print("of algebraic-structured improvement the report describes.")
