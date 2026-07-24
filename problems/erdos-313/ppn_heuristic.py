"""Bateman-Horn style heuristic for S_k = #{PPN with exactly k prime factors}.

Every PPN with k prime factors is detected at a unique depth-(k-1) state (N,A,m):
it is a solution iff A | N+1 and q=(N+1)/A is a prime > m.  Modelling those two
events as independent with

    Pr[A | N+1] ~ 1/A ,        Pr[q prime] ~ lambda(N)/log q ,
    lambda(N) = prod_{p|N} (1-1/p)^{-1}      (q is automatically coprime to N)

gives  S_k ~ Sigma_k := sum over depth-(k-1) states of  lambda(N)/(A log((N+1)/A)).

The depth-(k-1) level is far too large to enumerate, so we stop at depth k-2
(the t=2 states, which the search already enumerates) and integrate over the
children analytically:  the children of (N,A,m) are indexed by primes
q in (a,b), a = max(m, N/A), b = 2N/A, with A1 = A q - N, N1 = N q.
"""
import sys, time
from math import log, exp
from gmpy2 import mpz, next_prime

sys.setrecursionlimit(100000)
NQ = 48          # Simpson points


def lam(P):
    r = 1.0
    for p in P:
        r *= 1.0/(1.0 - 1.0/float(p))
    return r


def node_contrib(N, A, m, lamN):
    """integral over the t=1 children of a t=2 state"""
    a = N//A
    if m > a:
        a = m
    a += 1
    xa = float(A*a - N)
    if xa < 1.0:
        xa = 1.0
    xb = float(N)
    if xb <= xa:
        return 0.0
    fN, fA = float(N), float(A)
    y0, y1 = log(xa), log(xb)
    h = (y1-y0)/NQ
    tot = 0.0
    for i in range(NQ+1):
        y = y0 + i*h
        x = exp(y)
        q = (x+fN)/fA                      # the candidate prime q1
        l1 = log(q) if q > 2.5 else 1.0
        z = fN*(x+fN)/(fA*x)               # (N1+1)/A1 ~ N q /(A q - N)
        l2 = log(z) if z > 2.5 else 1.0
        f = 1.0/(l1*l2)
        w = 1 if (i == 0 or i == NQ) else (4 if i % 2 else 2)
        tot += w*f
    return lamN/fA * tot*h/3.0


def sigma(k):
    tot = 0.0; n2 = 0
    stack = [([], mpz(1), mpz(1), k)]
    t0 = time.time()
    while stack:
        P, N, A, t = stack.pop()
        if t == 2:
            n2 += 1
            tot += node_contrib(N, A, P[-1] if P else mpz(1), lam(P))
            continue
        if t < 2:
            continue
        m = P[-1] if P else mpz(1)
        lo = N//A
        if m > lo:
            lo = m
        hi = (t*N - 1)//A
        q = next_prime(lo)
        while q <= hi:
            A2 = A*q - N
            if A2 > 0:
                N2 = N*q
                if A2*(q+1) <= (t-1)*N2:
                    stack.append((P + [q], N2, A2, t-1))
            q = next_prime(q)
    print(f"k={k}  Sigma_k = {tot:.4f}   (t2 states {n2}, {time.time()-t0:.1f}s)", flush=True)
    return tot


if __name__ == "__main__":
    for k in range(int(sys.argv[1]), int(sys.argv[2])+1):
        sigma(k)
