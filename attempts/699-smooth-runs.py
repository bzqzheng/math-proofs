"""
#699 smooth-run table (vectorized): for each prime p <= 31, longest runs of
consecutive p-smooth numbers beyond the initial segment, vs. the run length
each composite i (largest prime < i equal to p) would require.
"""

import time

import numpy as np
from sympy import primerange

N = 30_000_000
t0 = time.time()
lpf = np.zeros(N + 1, dtype=np.uint32)
for q in primerange(2, N + 1):
    lpf[q::q] = q
lpf[1] = 1
print(f"LPF sieve to {N:.1e} in {time.time()-t0:.0f}s", flush=True)

PRIMES = list(primerange(3, 32))


def max_runs(p):
    smooth = lpf <= p
    d = np.diff(smooth.astype(np.int8))
    starts = np.nonzero(d == 1)[0] + 1
    ends = np.nonzero(d == -1)[0]
    if smooth[0]:
        starts = np.r_[0, starts]
    if smooth[-1]:
        ends = np.r_[ends, N]
    lens = ends - starts + 1
    order = np.argsort(-lens)
    # initial run is the one starting at 0 or 1
    return [(int(starts[k]), int(ends[k]), int(lens[k])) for k in order[:4]]


print(f"\n{'p':>3} {'init_end':>9} {'max non-init run':>16} {'location':>14}")
for p in PRIMES:
    top = max_runs(p)
    init = next(r for r in top if r[0] <= 1)
    noninit = next(r for r in top if r[0] > 1)
    print(f"{p:>3} {init[1]:>9} {noninit[2]:>16} {noninit[0]:>14,}", flush=True)
print(f"\ntotal {time.time()-t0:.0f}s", flush=True)
