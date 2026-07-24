"""Estimate the work of the exhaustive PPN search level by level.

At each node with t>=3 the engine loops over primes q in (max(m,N/A), t*N/A).
We enumerate the tree but STOP descending at depth `stop_t` (t == stop_t), and
report per-depth: node count, sum of loop widths, max N/A.
"""
import sys, time
from math import log
from gmpy2 import mpz, is_prime, next_prime

sys.setrecursionlimit(100000)


def profile(k, stop_t=3):
    nodes = [0]*(k+2)
    work = [0.0]*(k+2)      # estimated primes iterated
    maxNA = [0.0]*(k+2)
    stack = [([], mpz(1), mpz(1), k)]
    t0 = time.time()
    while stack:
        P, N, A, t = stack.pop()
        j = k - t
        nodes[j] += 1
        NA = N/A
        if NA > maxNA[j]:
            maxNA[j] = float(NA)
        if t <= stop_t:
            continue
        m = P[-1] if P else mpz(1)
        lo = N//A
        if m > lo:
            lo = m
        hi = (t*N - 1)//A
        w = float(hi-lo)/max(log(float(hi)+2.0), 1.0)
        work[j] += w
        if w > 2e7:
            print(f"  !! huge loop d{j} t={t} width={hi-lo} N/A={float(N/A):.3g} P={[int(x) for x in P]}", flush=True)
        q = next_prime(lo)
        while q <= hi:
            A2 = A*q - N
            if A2 > 0:
                N2 = N*q
                if A2*next_prime(q) <= (t-1)*N2:
                    stack.append((P + [q], N2, A2, t-1))
            q = next_prime(q)
    print(f"k={k} stop_t={stop_t} time={time.time()-t0:.1f}s")
    for j in range(k):
        if nodes[j]:
            print(f"  depth {j}: nodes={nodes[j]:>12}  est_prime_iters={work[j]:.3g}  max N/A={maxNA[j]:.3g}")
    return nodes, work


if __name__ == "__main__":
    profile(int(sys.argv[1]), int(sys.argv[2]) if len(sys.argv) > 2 else 3)
