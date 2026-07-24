"""
Erdős #699 — measure how close prime-i survival is to failing.

For each prime i and n, compute the minimum over j in (i, n/2] of the number
of large prime factors of C(n,i) that SAVE j (i.e. divide C(n,j)). A value of
zero means a counterexample; small values are near-misses.
"""

import math
import os
import time

from sympy import factorint, primerange

N_MAX = int(float(os.environ.get("N_MAX", 2000)))
t0 = time.time()

pl = list(primerange(2, N_MAX + 1))


def large_prime_factors(n, i):
    return {p for p, e in factorint(math.comb(n, i)).items() if p > i}


def min_savers(n, i):
    """Return min over j of |{p in P : p divides C(n,j)}|."""
    P = large_prime_factors(n, i)
    if not P:
        return 0
    lo = i + 1
    hi = n // 2
    if lo > hi:
        return len(P)  # vacuous
    min_save = len(P)
    worst_j = None
    for j in range(lo, hi + 1):
        save = 0
        for p in P:
            r = n % p
            if j < p or (j % p) > r:
                save += 1
        if save < min_save:
            min_save = save
            worst_j = j
            if save == 0:
                break
    return min_save, worst_j


def main():
    near_misses = []  # (min_save, n, i, worst_j)
    for n in range(4, N_MAX + 1):
        for i in pl:
            if i >= n // 2:
                break
            ms, wj = min_savers(n, i)
            if ms <= 1:  # record all near-misses
                near_misses.append((ms, n, i, wj))
        if n % 200 == 0:
            print(f"progress n={n} near_misses={len(near_misses)} elapsed={time.time()-t0:.0f}s", flush=True)

    print(f"\ndone n<={N_MAX}. near-misses (min_save<=1): {len(near_misses)}")
    near_misses.sort()
    for ms, n, i, wj in near_misses[:20]:
        print(f"  min_save={ms} n={n} i={i} worst_j={wj}")


if __name__ == "__main__":
    main()
