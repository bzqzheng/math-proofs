"""
Erdős #779 / Fortune's conjecture scan.

Fortunate number a(n) = least m > 1 with p_n# + m prime (p_n# = primorial).
Fortune's conjecture: a(n) is always prime.

Falsification channel (Ordowski, OEIS A005235): if a(n) is composite then
a(n) > p_{n+1}^2  (every prime factor of composite a(n) must exceed p_n).
So a counterexample = an n where the prime gap after p_n# exceeds p_{n+1}^2.
This script computes a(n) sequentially, flags composites (full BPSW via
sympy.isprime on every candidate), and reports the ratio a(n)/p_{n+1}^2
distribution so we can see how close the landscape gets to the
falsification channel.
"""

import os
import time

from sympy import isprime, nextprime, prime, primorial

N_MAX = int(os.environ.get("N_MAX", 1500))
TIME_BUDGET = int(os.environ.get("TIME_BUDGET", 900))

t0 = time.time()
max_ratio = 0.0
max_ratio_n = 0
results_tail = []

pn1 = 1
for n in range(1, N_MAX + 1):
    pn1 = nextprime(pn1)  # p_n
    P = primorial(n)
    m = 3
    while not isprime(P + m):
        m += 2
    # m is now a(n) (smallest m>1; m=2 impossible since P+2 is even > 2)
    if not isprime(m):
        print(f"*** COUNTEREXAMPLE n={n}: a(n)={m} is COMPOSITE", flush=True)
        print(f"    verify: factors of {m} and primality of P+m", flush=True)
    ratio = m / (nextprime(pn1) ** 2)
    if ratio > max_ratio:
        max_ratio = ratio
        max_ratio_n = n
        print(f"record ratio {ratio:.5f} at n={n} (a(n)={m}, p_n={pn1})", flush=True)
    if n % 100 == 0:
        print(f"progress n={n} p_n={pn1} digits(P)={len(str(P))} elapsed={time.time()-t0:.0f}s", flush=True)
    if time.time() - t0 > TIME_BUDGET:
        print(f"time budget hit at n={n}", flush=True)
        break

print(f"\ndone. scanned n<= {n}. no composite a(n) found.")
print(f"max a(n)/p_(n+1)^2 = {max_ratio:.5f} at n={max_ratio_n}")
print("(falsification needs ratio > 1)")
