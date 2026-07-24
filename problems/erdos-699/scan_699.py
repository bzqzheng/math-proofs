"""
Erdős #699 — binomial gcd conjecture, counterexample search.

Conjecture: for every 1 <= i < j <= n/2, gcd(C(n,i), C(n,j)) has a prime
factor p >= i.

Reduction (via Legendre digit sums / Kummer): for prime p >= i, p | C(n,i)
iff n mod p < i, and then p | C(n,j) too (since i < j). Also j drops out
entirely: the conjecture is a property of pairs (n, i) with 1 <= i < n/2:

    exists prime p >= i with n mod p < i.   (*)

Notes that make the scan fast:
- If i itself is prime, p = i always satisfies (*) (n mod i < i trivially).
  So only COMPOSITE i need checking.
- For primes p in (n/2, n): n mod p = n - p, so (*) holds iff p <= n - i.
  Hence if pmax = largest prime < n, all i in (n - pmax, n/2) are covered
  automatically; only i <= n - pmax (the prime gap below n, ~ log n) need
  real checks.

A counterexample (n, i) with i < n/2 failing (*) settles the conjecture in
the negative; the witness is machine-checkable in milliseconds (Kummer).
"""

import os
import time

from sympy import integer_nthroot, prevprime, primerange

N_MAX = int(float(os.environ.get("N_MAX", 10**6)))
t0 = time.time()

primes = list(primerange(2, N_MAX + 1))
import bisect

pl = primes


def covered(n, i):
    """Is (*) satisfied for (n, i)? Returns witnessing prime or None."""
    lo = bisect.bisect_left(pl, i)
    for k in range(lo, len(pl)):
        p = pl[k]
        if p > n:
            break
        if n % p < i:
            return p
    return None


def is_composite(x):
    if x < 4:
        return False
    for p in pl:
        if p * p > x:
            return False
        if x % p == 0:
            return True
    return False


bad = 0
checked = 0
for n in range(4, N_MAX + 1):
    imax = (n - 1) // 2
    pmax = prevprime(n)
    g = n - pmax  # only i <= g can be uncovered by large primes
    for i in range(2, min(g, imax) + 1):
        if not is_composite(i):
            continue
        checked += 1
        if covered(n, i) is None:
            bad += 1
            print(f"*** COUNTEREXAMPLE CANDIDATE: n={n}, i={i} — verify gcd(C({n},{i}),C({n},j)) "
                  f"prime factors for all j in (i, n/2]", flush=True)
    if n % 100000 == 0:
        print(f"progress n={n} checked={checked} bad={bad} elapsed={time.time()-t0:.0f}s", flush=True)

print(f"\ndone: n<= {N_MAX}, pairs checked={checked}, counterexamples={bad}, {time.time()-t0:.0f}s", flush=True)
