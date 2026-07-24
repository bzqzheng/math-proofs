"""
Erdős #699 — fast prime-i survival check (corrected via Lucas theorem).

For prime i, #699 holds iff for every j in (i, n//2] there is a prime
p >= i dividing C(n,i) that also divides C(n,j).

For p = i: p | C(n,j) iff some base-i digit of j exceeds the corresponding
base-i digit of n (Lucas theorem).

For p > i: same Lucas condition applies; the simpler "j < p or j mod p > r"
formula is only valid when p > sqrt(n), so we use the full digit condition.
"""

import math
import os
import time

from sympy import factorint, primerange

N_MAX = int(float(os.environ.get("N_MAX", 10000)))
t0 = time.time()

pl = list(primerange(2, N_MAX + 1))


def base_p_digits(x, p):
    digs = []
    while x > 0:
        digs.append(x % p)
        x //= p
    return digs


def p_divides_binom(n, j, p):
    """Return True iff prime p divides C(n,j), using Lucas theorem."""
    n_digs = base_p_digits(n, p)
    j_digs = base_p_digits(j, p)
    for k in range(max(len(n_digs), len(j_digs))):
        nd = n_digs[k] if k < len(n_digs) else 0
        jd = j_digs[k] if k < len(j_digs) else 0
        if jd > nd:
            return True
    return False


def large_prime_factors_plus_i(n, i):
    """Return primes p >= i dividing C(n,i)."""
    c = math.comb(n, i)
    fac = factorint(c)
    return {p for p, e in fac.items() if p >= i}


def conjecture_holds(n, i):
    P = large_prime_factors_plus_i(n, i)
    if not P:
        return False, "nolarge"
    lo = i + 1
    hi = n // 2
    if lo > hi:
        return True, None
    for j in range(lo, hi + 1):
        saved = False
        for p in P:
            if p_divides_binom(n, j, p):
                saved = True
                break
        if not saved:
            return False, j
    return True, None


def main():
    counterexamples = []
    last_print = 0
    for n in range(4, N_MAX + 1):
        for i in pl:
            if i >= n // 2:
                break
            holds, bad_j = conjecture_holds(n, i)
            if not holds:
                counterexamples.append((n, i, bad_j))
                print(f"COUNTEREXAMPLE n={n} i={i} bad_j={bad_j}", flush=True)
        if n - last_print >= 500:
            print(f"progress n={n} counterexamples={len(counterexamples)} elapsed={time.time()-t0:.0f}s", flush=True)
            last_print = n
    print(f"\ndone: n <= {N_MAX}, counterexamples={len(counterexamples)}, {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
