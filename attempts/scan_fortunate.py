"""
Erdős #779 / Fortune's conjecture scan (gmpy2-optimized).

Fortunate number a(n) = least m > 1 with p_n# + m prime (p_n# = primorial).
Fortune's conjecture: a(n) is always prime.

Key speedup: P = p_n# is even, so P+2 is even > 2 and cannot be prime.
Therefore a(n) = next_prime(P + 2) - P, where next_prime returns the
smallest prime strictly greater than its argument. gmpy2.next_prime is
orders of magnitude faster than testing successive odd m.

Falsification channel (Ordowski, OEIS A005235): if a(n) is composite then
a(n) > p_{n+1}^2 (every prime factor of composite a(n) must exceed p_n).
So a counterexample = an n where the prime gap after p_n# exceeds p_{n+1}^2.
"""

import os
import time

import gmpy2
from sympy import nextprime

N_MAX = int(os.environ.get("N_MAX", 5000))
TIME_BUDGET = int(os.environ.get("TIME_BUDGET", 3600))

t0 = time.time()
max_ratio = 0.0
max_ratio_n = 0

P = gmpy2.mpz(1)
pn = 1  # p_n
for n in range(1, N_MAX + 1):
    pn = int(nextprime(pn))
    P *= pn  # p_n#
    a_n = int(gmpy2.next_prime(P + 2) - P)
    if not gmpy2.is_prime(a_n):
        print(f"*** COUNTEREXAMPLE n={n}: a(n)={a_n} is COMPOSITE", flush=True)
        print(f"    verify: P={P}, P+a(n)={P + a_n}", flush=True)
    p_next = int(nextprime(pn))
    ratio = a_n / (p_next ** 2)
    if ratio > max_ratio:
        max_ratio = ratio
        max_ratio_n = n
        print(f"record ratio {ratio:.5f} at n={n} (a(n)={a_n}, p_n={pn}, p_{{n+1}}={p_next})", flush=True)
    if n % 100 == 0:
        print(f"progress n={n} p_n={pn} digits(P)={P.bit_length()} bits elapsed={time.time()-t0:.0f}s", flush=True)
    if time.time() - t0 > TIME_BUDGET:
        print(f"time budget hit at n={n}", flush=True)
        break

print(f"\ndone [gmpy2]. scanned n<= {n}. no composite a(n) found.")
print(f"max a(n)/p_(n+1)^2 = {max_ratio:.5f} at n={max_ratio_n}")
print("(falsification needs ratio > 1)")
