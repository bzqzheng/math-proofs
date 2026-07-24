"""
Erdős #458 — lcm inequality, counterexample scan.

Conjecture: lcm(1..p_{k+1} - 1) < p_k * lcm(1..p_k) for all k >= 1.
Via logs with Chebyshev psi(N) = log lcm(1..N):
    counterexample k  <=>  psi(p_{k+1} - 1) >= log(p_k) + psi(p_k).

Since no primes lie strictly between p_k and p_{k+1}, the difference
psi(p_{k+1}-1) - psi(p_k) = sum of log q over prime POWERS q^e (e >= 2)
in (p_k, p_{k+1}-1]  — bases q can be much smaller than p_k (e.g. 11^2=121
falls in the gap after 113). Danger zone is therefore small k.
"""

import math
import os
import time

from sympy import nextprime, primerange

K_MAX = int(float(os.environ.get("K_MAX", 10**6)))
t0 = time.time()

pk = 2
psi_pk = math.log(2)
bad = 0
k = 1
min_margin = float("inf")
min_margin_k = 0
while k <= K_MAX:
    pk1 = nextprime(pk)
    extra = 0.0
    # prime powers q^e (e >= 2) in (pk, pk1-1]; need q <= sqrt(pk1-1)
    for q in primerange(2, int(math.isqrt(pk1 - 1)) + 1):
        qq = q * q
        while qq <= pk1 - 1:
            if qq > pk:
                extra += math.log(q)
            qq *= q
    margin = math.log(pk) - extra  # > 0 iff conjecture holds at k
    if margin < min_margin:
        min_margin = margin
        min_margin_k = k
        print(f"min margin {margin:.5f} at k={k} (p_k={pk}, gap={pk1-pk})", flush=True)
    if margin <= 0:
        bad += 1
        print(f"*** COUNTEREXAMPLE k={k}: p_k={pk}, p_{{k+1}}={pk1}", flush=True)
    psi_pk += extra + math.log(pk1)
    pk = pk1
    k += 1

print(f"\ndone: k<= {K_MAX}, counterexamples={bad}, min margin={min_margin:.5f} at k={min_margin_k}, {time.time()-t0:.0f}s", flush=True)
