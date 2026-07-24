"""
Erdős #458 — fast lcm-inequality counterexample scan.

Conjecture: lcm(1..p_{k+1} - 1) < p_k * lcm(1..p_k) for all k >= 1.
Equivalently, with psi(N) = log lcm(1..N):
    counterexample k  <=>  psi(p_{k+1} - 1) >= log(p_k) + psi(p_k).

The difference psi(p_{k+1}-1) - psi(p_k) is the sum of log q over prime
powers q = r^e (e >= 2) in the open-closed gap (p_k, p_{k+1}-1].

Speedup: precompute all prime powers up to a bound larger than any prime gap
we will encounter, sort them, then advance a pointer through the list while
sweeping consecutive primes.  This avoids repeatedly scanning primes up to
sqrt(pk1) for every k.
"""

import math
import os
import time

from sympy import nextprime, primerange

K_MAX = int(float(os.environ.get("K_MAX", 10**6)))
MAX_GAP_EST = int(os.environ.get("MAX_GAP_EST", 400))  # upper bound on gap size

t0 = time.time()

# Precompute prime powers r^e (e >= 2) up to MAX_GAP_EST, paired with log(r).
# For a gap (p_k, p_{k+1}) we need powers <= gap-1 (since gap ends at p_{k+1}-1).
# MAX_GAP_EST should exceed the maximal prime gap below p_{K_MAX}.
# By known bounds, maximal gap below x is O(log^2 x); for K_MAX=1e7, x~1.8e8,
# log^2 x ~ 400, so 400 is a safe overestimate.
powers = []  # list of (power, log(base))
for r in primerange(2, MAX_GAP_EST + 1):
    logr = math.log(r)
    rr = r * r
    while rr <= MAX_GAP_EST:
        powers.append((rr, logr))
        rr *= r
powers.sort()

pk = 2
psi_pk = math.log(2.0)
bad = 0
k = 1
min_margin = float("inf")
min_margin_k = 0
idx = 0  # pointer into powers
n_pow = len(powers)

while k <= K_MAX:
    pk1 = nextprime(pk)
    gap_end = pk1 - 1
    # advance idx to first power > pk
    while idx < n_pow and powers[idx][0] <= pk:
        idx += 1
    # sum log(base) for powers in (pk, gap_end]
    extra = 0.0
    j = idx
    while j < n_pow and powers[j][0] <= gap_end:
        extra += powers[j][1]
        j += 1
    margin = math.log(pk) - extra
    if margin < min_margin:
        min_margin = margin
        min_margin_k = k
        print(f"min margin {margin:.5f} at k={k} (p_k={pk}, gap={pk1-pk}) elapsed={time.time()-t0:.0f}s", flush=True)
    if margin <= 0:
        bad += 1
        print(f"*** COUNTEREXAMPLE k={k}: p_k={pk}, p_{{k+1}}={pk1}", flush=True)
    psi_pk += extra + math.log(pk1)
    pk = pk1
    k += 1

print(f"\ndone: k<= {K_MAX}, counterexamples={bad}, min margin={min_margin:.5f} at k={min_margin_k}, {time.time()-t0:.0f}s", flush=True)
