"""
Erdős #366 and #364 — powerful-number witness scans.

#366 (verifiable tag): does there exist n 2-full (powerful) with n+1 3-full?
  No example is known. Search side: enumerate 3-full numbers (density
  ~ x^(1/3), cheap), test whether n-1 is powerful.
  Fast powerful test for m: strip primes p with p^3 <= m requiring
  exponent >= 2 (v_p = 1 kills); the leftover must be a perfect square
  (two primes > cbrt(m) can't both divide m powerfully).

#364 (falsifiable tag): Erdős conjectured NO three consecutive powerful
  numbers. Counterexample = witness. Enumerate powerful numbers <= X via
  the canonical a^2 * b^3 form (b squarefree), sort, scan diffs for runs.
  Validation: known pairs (A060355) 8, 288, 675, 9800, 12167, ... must
  appear; triples must NOT appear below known frontier.
"""

import os
import time

from sympy import integer_nthroot, primerange

t0 = time.time()

# ---------- part 1: #366 ----------
X3 = int(float(os.environ.get("X3", 10**18)))
SMALL = list(primerange(2, int(X3 ** (1 / 3)) + 2))


def is_powerful(m):
    if m <= 0:
        return False
    for p in SMALL:
        if p * p * p > m:
            break
        if m % p == 0:
            m //= p
            if m % p != 0:
                return False
            while m % p == 0:
                m //= p
    if m == 1:
        return True
    r, exact = integer_nthroot(m, 2)
    return exact


found_366 = []
count3 = 0


def gen3full(start_idx, cur):
    """Yield 3-full numbers via recursion over primes, exponent >= 3."""
    global count3
    for i in range(start_idx, len(SMALL)):
        p = SMALL[i]
        v = cur * p ** 3
        if v > X3:
            return
        while v <= X3:
            yield v
            yield from gen3full(i + 1, v)
            v *= p


print(f"#366 scan: 3-full numbers <= {X3:.1e}", flush=True)
for n in gen3full(0, 1):
    count3 += 1
    if is_powerful(n - 1):
        found_366.append(n)
        print(f"*** #366 WITNESS: n={n-1} (2-full), n+1={n} (3-full)", flush=True)
print(f"3-full count: {count3:,} | witnesses: {len(found_366)} | {time.time()-t0:.0f}s", flush=True)

# ---------- part 2: #364 ----------
X = int(float(os.environ.get("X", 10**13)))
print(f"\n#364 scan: powerful numbers <= {X:.1e}", flush=True)

pow2 = set()
a = 1
while a * a <= X:
    a2 = a * a
    # b squarefree, b^3 <= X/a2; generate squarefree b via recursion
    lim = int((X // a2) ** (1 / 3)) + 2

    def gen_sqfree(start, cur):
        yield cur
        for j in range(start, len(SMALL)):
            q = SMALL[j]
            if cur * q > lim:
                return
            yield from gen_sqfree(j + 1, cur * q)

    for b in gen_sqfree(0, 1):
        v = a2 * b ** 3
        if v <= X:
            pow2.add(v)
    a += 1

import numpy as np

arr = np.array(sorted(pow2), dtype=object)
print(f"powerful count: {len(arr):,} | {time.time()-t0:.0f}s", flush=True)

d = np.diff(arr)
pair_idx = np.nonzero(d == 1)[0]
pairs = [(int(arr[i]), int(arr[i] + 1)) for i in pair_idx]
print(f"consecutive pairs found: {len(pairs)}", flush=True)
known = [8, 288, 675, 9800, 12167, 235224, 332928, 465124, 1825200, 11309768]
missing = [k for k in known if k <= X and k not in {p[0] for p in pairs}]
print(f"known-pair validation: {'PASS' if not missing else 'MISSING ' + str(missing)}", flush=True)
triples = [(int(arr[i]), int(arr[i] + 1), int(arr[i] + 2)) for i in range(len(arr) - 2) if arr[i + 1] == arr[i] + 1 and arr[i + 2] == arr[i] + 2]
print(f"TRIPLES (counterexamples to #364): {len(triples)}", flush=True)
for t in triples:
    print(f"*** #364 COUNTEREXAMPLE: {t}", flush=True)
print(f"\nall done in {time.time()-t0:.0f}s", flush=True)
