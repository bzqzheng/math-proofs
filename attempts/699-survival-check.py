"""
Erdős #699 — direct gcd survival check.

For each (n, i) with 1 <= i < n/2, verify that for every j in (i, n//2]
gcd(C(n,i), C(n,j)) has a prime factor >= i.

Also reports whether the necessary predicate `∃ p >= i : n mod p < i`
matches the full gcd condition.

Usage: N_MAX=5000 .venv/bin/python attempts/699-survival-check.py
"""

import math
import os
import sys
import time

from sympy import factorint, primerange

N_MAX = int(float(os.environ.get("N_MAX", 1000)))
t0 = time.time()

pl = list(primerange(2, N_MAX + 1))


def covered(n, i):
    """Necessary predicate used by scan_699.py: ∃ prime p >= i with n mod p < i."""
    import bisect
    lo = bisect.bisect_left(pl, i)
    for k in range(lo, len(pl)):
        p = pl[k]
        if p > n:
            break
        if n % p < i:
            return True
    return False


def conjecture_holds(n, i):
    """Full #699 condition for fixed (n, i); returns (holds, bad_j)."""
    cni = math.comb(n, i)
    cnif = factorint(cni)
    large_in_cni = {p for p in cnif if p >= i}
    if not large_in_cni:
        return False, None  # C(n,i) itself has no large prime factor
    for j in range(i + 1, n // 2 + 1):
        g = math.gcd(cni, math.comb(n, j))
        gf = factorint(g)
        if not any(p >= i for p in gf):
            return False, j
    return True, None


mismatches = 0
counterexamples = []
last_print = 0

for n in range(4, N_MAX + 1):
    for i in range(1, n // 2):
        cov = covered(n, i)
        holds, bad_j = conjecture_holds(n, i)
        if cov != holds:
            mismatches += 1
            print(f"MISMATCH n={n} i={i} covered={cov} holds={holds} bad_j={bad_j}", flush=True)
        if not holds:
            counterexamples.append((n, i, bad_j))
            print(f"COUNTEREXAMPLE n={n} i={i} bad_j={bad_j}", flush=True)
    if n - last_print >= 500:
        print(f"progress n={n} mismatches={mismatches} counterexamples={len(counterexamples)} "
              f"elapsed={time.time()-t0:.0f}s", flush=True)
        last_print = n

print(f"\ndone: n <= {N_MAX}, mismatches={mismatches}, counterexamples={len(counterexamples)}, "
      f"{time.time()-t0:.0f}s", flush=True)
