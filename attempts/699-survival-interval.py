"""
Erdős #699 — interval-union prime-i survival check (much faster).

For prime i, #699 holds iff for every j in [i+1, n//2] there is a prime
p >= i dividing C(n,i) that also divides C(n,j).

Large prime factors p > i: survival intervals are
    [max(i+1, m*p + r_p + 1), min(n//2, (m+1)*p - 1)]   for m = 0, 1, 2, ...
where r_p = n mod p.

For p = i (prime), we use Lucas theorem: i | C(n,j) iff some base-i digit of
j exceeds the corresponding digit of n. We enumerate the surviving j in
[i+1, n//2] by scanning (still cheap because i is small relative to n, but we
only need to do it when i | C(n,i)).
"""

import math
import os
import time

from sympy import factorint, primerange

N_MAX = int(float(os.environ.get("N_MAX", 20000)))
t0 = time.time()

pl = list(primerange(2, N_MAX + 1))


def large_prime_factors_plus_i(n, i):
    """Return primes p >= i dividing C(n,i). For p=i, include only if i | C(n,i)."""
    c = math.comb(n, i)
    fac = factorint(c)
    P = {p for p, e in fac.items() if p > i}
    if i in fac:
        P.add(i)
    return P


def lucas_surviving_js(n, i, lo, hi):
    """Yield j in [lo, hi] for which i | C(n,j), using Lucas theorem (i prime)."""
    # base-i digits of n
    n_digits = []
    temp = n
    while temp > 0:
        n_digits.append(temp % i)
        temp //= i
    if not n_digits:
        n_digits.append(0)
    for j in range(lo, hi + 1):
        t = j
        k = 0
        saved = False
        while t > 0 or k < len(n_digits):
            dj = t % i if t > 0 else 0
            if k < len(n_digits):
                if dj > n_digits[k]:
                    saved = True
                    break
            else:
                if dj > 0:  # n has digit 0 beyond its length
                    saved = True
                    break
            t //= i
            k += 1
        if saved:
            yield j


def survival_intervals_large_p(n, i, hi, P):
    """Yield survival intervals on [i+1, n//2] for each p > i in P."""
    for p in P:
        if p <= i:
            continue
        r = n % p
        m = 0
        while True:
            L = max(i + 1, m * p + r + 1)
            R = min(hi, (m + 1) * p - 1)
            if L > R:
                if m * p > hi:
                    break
                m += 1
                continue
            yield (L, R)
            if R == hi:
                break
            m += 1


def intervals_from_set(js):
    """Convert a sorted iterable of integers to a list of intervals."""
    js = sorted(set(js))
    if not js:
        return []
    intervals = []
    cur_l = cur_r = js[0]
    for x in js[1:]:
        if x == cur_r + 1:
            cur_r = x
        else:
            intervals.append((cur_l, cur_r))
            cur_l = cur_r = x
    intervals.append((cur_l, cur_r))
    return intervals


def merge_intervals(intervals):
    if not intervals:
        return []
    intervals = sorted(intervals)
    merged = [intervals[0]]
    for L, R in intervals[1:]:
        last_L, last_R = merged[-1]
        if L <= last_R + 1:
            merged[-1] = (last_L, max(last_R, R))
        else:
            merged.append((L, R))
    return merged


def covers(intervals, lo, hi):
    if not intervals:
        return False
    if intervals[0][0] > lo:
        return False
    cur_r = intervals[0][1]
    for L, R in intervals[1:]:
        if L > cur_r + 1:
            return False
        cur_r = max(cur_r, R)
    return cur_r >= hi


def conjecture_holds(n, i):
    P = large_prime_factors_plus_i(n, i)
    if not P:
        return False, "nolarge"
    lo = i + 1
    hi = n // 2
    if lo > hi:
        return True, None
    intervals = list(survival_intervals_large_p(n, i, hi, P))
    if i in P:
        js = list(lucas_surviving_js(n, i, lo, hi))
        intervals.extend(intervals_from_set(js))
    merged = merge_intervals(intervals)
    if covers(merged, lo, hi):
        return True, None
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
        if n - last_print >= 1000:
            print(f"progress n={n} counterexamples={len(counterexamples)} elapsed={time.time()-t0:.0f}s", flush=True)
            last_print = n
    print(f"\ndone: n <= {N_MAX}, counterexamples={len(counterexamples)}, {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
