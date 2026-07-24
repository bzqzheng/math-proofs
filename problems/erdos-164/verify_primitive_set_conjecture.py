"""
Offline verification of the Erdős Primitive Set Conjecture (#164) on all
small cases, plus a numerical check of the von Mangoldt / prime-sum bound
that the AI-guided proof of #1196/#1217/#164 relies on.

Conjecture (#164, proved per the report by the "von Mangoldt chain" method):
  For every primitive set A (no element divides another),
      f(A) = sum_{a in A} 1/(a log a)  <=  sum_{p prime} 1/(p log p).

What we can verify offline:
  (1) EXHAUSTIVELY: for every primitive subset A of {2,...,N}, f(A) is
      maximized by the primes <= N. This is the full conjecture restricted
      to [2, N] — not a sample, every single primitive set.
  (2) That the prime sum itself converges toward the known constant
      ~1.6366 (Lichtman–Pomerance), so the bound is a finite number.
"""

import math
import sys

sys.setrecursionlimit(100000)

N = 26  # exhaustive over ALL primitive subsets of {2..N}

nums = list(range(2, N + 1))
best_f = 0.0
best_set = ()
n_primitive = 0


def rec(i, forbidden_multiples, chosen, fval):
    global best_f, best_set, n_primitive
    if fval > best_f + 1e-15:
        best_f = fval
        best_set = tuple(chosen)
    if i == len(nums):
        n_primitive += 1
        return
    a = nums[i]
    # branch 1: skip a
    rec(i + 1, forbidden_multiples, chosen, fval)
    # branch 2: take a, if no chosen element divides a
    if a not in forbidden_multiples:
        # multiples of a within [2..N] become forbidden; nothing already
        # chosen can be a multiple of a (all chosen < a), and "a not in
        # forbidden" guarantees no chosen element divides a.
        new_forbidden = forbidden_multiples | set(range(2 * a, N + 1, a))
        chosen.append(a)
        rec(i + 1, new_forbidden, chosen, fval + 1.0 / (a * math.log(a)))
        chosen.pop()


rec(0, set(), [], 0.0)

# sieve for primes
sieve = [True] * (N + 1)
sieve[0] = sieve[1] = False
for p in range(2, N + 1):
    if sieve[p]:
        for q in range(2 * p, N + 1, p):
            sieve[q] = False
primes = [p for p in range(2, N + 1) if sieve[p]]
f_primes = sum(1.0 / (p * math.log(p)) for p in primes)

print(f"Exhaustive check over ALL primitive subsets of {{2..{N}}}")
print(f"  number of primitive subsets enumerated: {n_primitive:,}")
print(f"  max f(A) over all of them:            {best_f:.10f}")
print(f"  attained by A* = {best_set}")
print(f"  f(primes <= {N}):                      {f_primes:.10f}")
assert best_set == tuple(primes), "conjecture FAILS on some small set!"
print("  => max is attained exactly at the primes. #164 holds on [2, N].  OK")

# (2) the global prime bound converges
M = 2_000_000
sieve = bytearray([1]) * (M + 1)
sieve[0:2] = b"\x00\x00"
for p in range(2, int(M**0.5) + 1):
    if sieve[p]:
        sieve[p * p :: p] = b"\x00" * ((M - p * p) // p + 1)
s = sum(1.0 / (p * math.log(p)) for p in range(2, M + 1) if sieve[p])
print(f"\n  sum over primes p <= {M:,} of 1/(p log p) = {s:.6f}")
print(f"  (known limiting constant ~1.636616..., Lichtman–Pomerance)")
print(f"  => the conjectured universal bound is a small finite number.  OK")
