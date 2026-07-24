"""
Erdős #470(i): search for an odd weird number.

KEY STRUCTURAL TRICK (exact, derived in attempts/470-odd-weird.md):
    n is weird  <=>  delta := sigma(n) - 2n > 0  AND  delta is NOT expressible
    as a sum of distinct proper divisors of n.
Proof: semiperfect means a subset of proper divisors sums to n; the complement
of that subset (within all proper divisors, total sum sigma(n)-n) sums to
sigma(n)-n-n = delta. So subset-sum testing collapses from target n
(infeasible for n ~ 10^21) to target delta, which we force to be small.

SEARCH: DFS over factorizations n = prod p_i^a_i (exact integer sigma and n).
Pruning:
  - delta > DELTA_MAX  => prune (delta is monotone increasing once abundant:
    both (abundancy - 2) and n only grow as factors are appended).
  - deficient node     => prune if even the most generous continuation
    (appending the next k smallest available primes, k = as many as the size
    cap allows) cannot push abundancy past 2.
VALIDATION: run with allow_even=True below 10^6 must reproduce the known
weird numbers 70, 836, 4030, 5830, 7192, 7912, 9272, ...
Then the real run: odd n in (10^19, N_CAP] overlapping Fang's 10^21 bound
to sanity-check that the filter agrees (no odd weird below 10^21).
"""

import math
import os
import time

from sympy import nextprime

# ---- parameters (env-overridable for validation runs) ----
N_CAP = int(float(os.environ.get("N_CAP", 10**24)))
DELTA_MAX = int(float(os.environ.get("DELTA_MAX", 10**7)))
ALLOW_EVEN = os.environ.get("ALLOW_EVEN", "0") == "1"
TIME_BUDGET = int(os.environ.get("TIME_BUDGET", 240))

t0 = time.time()
nodes = 0
tested = 0
found = []


def divisors_upto(fac, limit):
    """All divisors of n (from factorization fac) that are <= limit."""
    ds = [1]
    for p, a in fac:
        pp = 1
        ext = []
        for _ in range(a):
            pp *= p
            for d in ds:
                v = d * pp
                if v <= limit:
                    ext.append(v)
        ds += ext
    return ds


def delta_expressible(fac, delta):
    """Is delta a sum of distinct proper divisors? (bitset subset-sum)"""
    ds = divisors_upto(fac, delta)
    bits = 1
    for v in ds:
        bits |= bits << v
    return (bits >> delta) & 1


def max_extra_abundancy(sig, n, p_next):
    """Upper bound on reachable abundancy: greedily append the next smallest
    primes (each once, factor (1+1/p)) while n * p <= N_CAP. Returns
    (max_abundancy_num, max_abundancy_den) as a float comparison value."""
    abund = sig / n
    nn = n
    p = p_next
    while True:
        if nn * p > N_CAP:
            break
        abund *= 1 + 1.0 / p
        nn *= p
        p = nextprime(p)
        if time.time() - t0 > TIME_BUDGET:
            break
    return abund


def dfs(idx_start_prime, n, sig, fac):
    global nodes, tested
    nodes += 1
    if nodes % 100000 == 0 and time.time() - t0 > TIME_BUDGET:
        return
    delta = sig - 2 * n
    if delta > 0:
        if delta >= DELTA_MAX:
            return
        tested += 1
        if not delta_expressible(fac, delta):
            found.append((n, delta, list(fac)))
            print(f"*** WEIRD CANDIDATE n={n} delta={delta} fac={fac}", flush=True)
        # keep recursing: multiples can also have small delta (delta' ~ p*delta)
    else:
        # deficient: can we still reach abundancy 2 within the size cap?
        if max_extra_abundancy(sig, n, idx_start_prime) <= 2.0:
            return

    p = idx_start_prime
    while n * p <= N_CAP:
        if time.time() - t0 > TIME_BUDGET:
            return
        # try p^a for a = 1, 2, ... while within cap
        nn, ss = n * p, sig * (p + 1)
        ppow = p
        a = 1
        while nn <= N_CAP:
            # pruning on the deficient side is handled at recursion entry;
            # but skip branches where even this prime can't help enough:
            dfs(nextprime(p), nn, ss, fac + [(p, a)])
            a += 1
            ppow *= p
            nn_next = n * ppow
            if nn_next > N_CAP:
                break
            nn = nn_next
            ss = sig * (ppow * p - 1) // (p - 1)
        p = nextprime(p)


if ALLOW_EVEN:
    start = 2
else:
    start = 3

print(f"search: odd={not ALLOW_EVEN}, N_CAP={N_CAP:.2e}, DELTA_MAX={DELTA_MAX:.1e}")
dfs(start, 1, 1, [])
print(f"\ndone in {time.time()-t0:.1f}s | nodes={nodes:,} | abundant-with-small-delta tested={tested:,} | weird found={len(found)}")
for n, d, f in found:
    print(f"  n={n} delta={d} fac={f}")
