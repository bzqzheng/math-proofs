"""Resolve nodes deferred by the C engine.

t=2 deferrals (T2ITER / T2SPAN) are settled exactly by factoring M = N^2 + A and
enumerating the divisors u = A*q1 - N.  t>=3 deferrals are reported, not settled.
"""
import sys, re
from gmpy2 import mpz, is_prime
from ppn2 import factorize, divisors_from


def resolve(path):
    unresolved = []
    sols = []
    n2 = 0
    for line in open(path):
        line = line.strip()
        if not line:
            continue
        why, rest = line.split(" ", 1)
        t = int(re.search(r"t=(\d+)", rest).group(1))
        P = [int(x) for x in re.search(r"P=([\d,]*)", rest).group(1).split(",") if x]
        N = mpz(re.search(r"N=(\d+)", rest).group(1))
        A = mpz(re.search(r"A=(\d+)", rest).group(1))
        if t != 2:
            unresolved.append(line)
            continue
        n2 += 1
        m = P[-1] if P else 1
        M = N*N + A
        f = factorize(M)
        for u in divisors_from(f):
            if u*u > M:
                break
            if (u + N) % A:
                continue
            q1 = (u + N)//A
            if q1 <= m or not is_prime(q1):
                continue
            v = M//u
            if (v + N) % A:
                continue
            q2 = (v + N)//A
            if q2 > q1 and is_prime(q2):
                sols.append(P + [int(q1), int(q2)])
                print("  *** SOLUTION (from deferred):", P + [int(q1), int(q2)], flush=True)
    print(f"{path}: t=2 deferrals resolved={n2}, solutions={len(sols)}, unresolved(t>=3)={len(unresolved)}")
    for u in unresolved[:20]:
        print("   UNRESOLVED:", u)
    return sols, unresolved


if __name__ == "__main__":
    for p in sys.argv[1:]:
        resolve(p)
