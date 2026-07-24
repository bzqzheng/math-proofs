"""
Erdős #470(i): search for an odd weird number. (v2 — bounded branching)

KEY TRICK (exact): n weird <=> delta = sigma(n) - 2n > 0 AND delta is not a
sum of distinct proper divisors of n. (Complementation argument; see
attempts/470-odd-weird.md.) Oracle cost is O(delta), and delta is forced
small by construction.

v2 FIXES (v1 was a runaway):
- Per-node prime-branch cap. Deficient node with abundancy A = sigma/n and
  size budget for k more factors: choosing next prime p can reach abundancy
  2 only if A*(1+1/p)^(k+1) > 2 (each further factor contributes at most
  (1+1/p), since primes only grow). Break the p-loop the moment this fails.
  At the root this caps p at ~23 instead of ~10^21.
- Abundant node (delta > 0): extending by prime p gives
  delta' = delta*p + sigma (a=1), increasing in p — break when it exceeds
  DELTA_MAX. Extensions with a >= 2 are strictly worse; try a=1 only.
- Flushed progress logging + tight time checks.

Validation (must pass before frontier runs): ALLOW_EVEN=1 N_CAP=1e6 must
reproduce 70, 836, 4030, 5830, 7192, 7912, 9272 among the finds.
"""

import os
import time

from sympy import nextprime

N_CAP = int(float(os.environ.get("N_CAP", 10**24)))
DELTA_MAX = int(float(os.environ.get("DELTA_MAX", 10**7)))
ALLOW_EVEN = os.environ.get("ALLOW_EVEN", "0") == "1"
TIME_BUDGET = int(os.environ.get("TIME_BUDGET", 600))

t0 = time.time()
nodes = 0
tested = 0
found = []
deadline_hit = False


def divisors_upto(fac, limit):
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
    ds = divisors_upto(fac, delta)
    bits = 1
    for v in ds:
        bits |= bits << v
    return (bits >> delta) & 1


def k_max(n, p_start):
    """Max number of additional prime factors (>= p_start) fitting in N_CAP."""
    k = 0
    m = n
    p = p_start
    while m * p <= N_CAP:
        m *= p
        p = nextprime(p)
        k += 1
    return k


def dfs(p_start, n, sig, fac):
    global nodes, tested, deadline_hit
    if deadline_hit:
        return
    nodes += 1
    if nodes % 1000 == 0:
        if time.time() - t0 > TIME_BUDGET:
            deadline_hit = True
            return
    if nodes % 1_000_000 == 0:
        print(f"progress: nodes={nodes:,} tested={tested:,} found={len(found)} "
              f"n={n} elapsed={time.time()-t0:.0f}s", flush=True)

    delta = sig - 2 * n
    if delta > 0:
        if delta >= DELTA_MAX:
            return
        tested += 1
        if not delta_expressible(fac, delta):
            found.append((n, delta, list(fac)))
            print(f"*** WEIRD n={n} delta={delta} fac={fac}", flush=True)
        # extension by prime p (a=1) gives delta' = delta*p + sig; increasing
        # in p, so the p-loop below breaks as soon as this exceeds DELTA_MAX.
        abundant = True
    else:
        abundant = False
        km = k_max(n, p_start)
        if km == 0:
            return

    abund = sig / n
    p = p_start
    while n * p <= N_CAP:
        if abundant:
            if delta * p + sig >= DELTA_MAX:
                break  # even a=1 extension overshoots delta budget
            dfs(nextprime(p), n * p, sig * (p + 1), fac + [(p, 1)])
        else:
            # can choosing p (any exponent) still reach abundancy 2? Each
            # further prime-power factor q^b contributes multiplier
            # sigma(q^b)/q^b < q/(q-1) <= p/(p-1); at most km+1 factors fit.
            if abund * (p / (p - 1)) ** (km + 1) <= 2.0:
                break
            nn = n
            ppow = 1
            a = 0
            while True:
                ppow *= p
                nn = n * ppow
                if nn > N_CAP:
                    break
                a += 1
                ss = sig * (ppow * p - 1) // (p - 1)
                dfs(nextprime(p), nn, ss, fac + [(p, a)])
                if deadline_hit:
                    return
        if deadline_hit:
            return
        p = nextprime(p)


start = 2 if ALLOW_EVEN else 3
print(f"search v2: odd={not ALLOW_EVEN}, N_CAP={N_CAP:.2e}, DELTA_MAX={DELTA_MAX:.1e}", flush=True)
dfs(start, 1, 1, [])
print(f"\ndone in {time.time()-t0:.1f}s | nodes={nodes:,} | tested={tested:,} | weird={len(found)}", flush=True)
for n, d, f in sorted(found):
    print(f"  n={n} delta={d} fac={f}", flush=True)
