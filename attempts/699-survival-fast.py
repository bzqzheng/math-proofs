"""
Erdős #699 — fast prime-i survival check.

For composite i, #699 is already settled by Sylvester–Schur (C(n,i) has a
prime factor > i). For prime i, we must check that for every j in (i, n/2]
some prime p > i dividing C(n,i) also divides C(n,j).

For a fixed prime p > i with p | C(n,i), let r = n mod p (0 <= r < i).
Then p | C(n,j) iff either j < p or (j >= p and j mod p > r).
So p FAILS at j iff j >= p and j mod p <= r. This is a union of intervals
[mp, mp + r] for m = 1, 2, ... while mp <= n/2.

A counterexample to #699 with prime i would require the failure sets of all
large prime factors of C(n,i) to cover every integer j in (i, n/2].

This script searches for such a covering. It is much faster than full gcd
factorization because it only needs the prime factors of C(n,i).
"""

import math
import os
import sys
import time

from sympy import factorint, primerange

N_MAX = int(float(os.environ.get("N_MAX", 5000)))
t0 = time.time()

pl = list(primerange(2, N_MAX + 1))


def large_prime_factors_of_binom(n, i):
    """Return primes p > i dividing C(n,i)."""
    c = math.comb(n, i)
    fac = factorint(c)
    return {p for p, e in fac.items() if p > i}


def conjecture_holds(n, i):
    """
    Check the prime-i survival condition for #699.
    Returns (holds, info). holds=True means #699 holds for (n,i); holds=False
    with info='covered' means the intersection of failure intervals covers some
    j (counterexample to survival); holds=False with info='nolarge' means
    C(n,i) has no prime factor > i (immediate #699 counterexample).

    For p in P, p FAILS at j iff j >= p and j mod p <= r = n mod p.
    #699 fails at j iff EVERY p in P fails at j.
    """
    P = large_prime_factors_of_binom(n, i)
    if not P:
        return False, "nolarge"
    lo = i + 1
    hi = n // 2
    if lo > hi:
        return True, None
    size = hi - lo + 1
    fail_count = [0] * size
    for p in P:
        r = n % p
        m = (lo + p - 1) // p
        while m * p <= hi:
            start = max(lo, m * p)
            end = min(hi, m * p + r)
            for j in range(start, end + 1):
                fail_count[j - lo] += 1
            m += 1
    for idx, c in enumerate(fail_count):
        if c < len(P):
            return True, lo + idx
    return False, "covered"


def main():
    counterexamples = []
    last_print = 0
    for n in range(4, N_MAX + 1):
        for i in pl:
            if i >= n // 2:
                break
            holds, info = conjecture_holds(n, i)
            if not holds:
                counterexamples.append((n, i, info))
                print(f"COUNTEREXAMPLE n={n} i={i} reason={info}", flush=True)
        if n - last_print >= 500:
            print(f"progress n={n} counterexamples={len(counterexamples)} elapsed={time.time()-t0:.0f}s", flush=True)
            last_print = n

    print(f"\ndone: n <= {N_MAX}, counterexamples={len(counterexamples)}, {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
