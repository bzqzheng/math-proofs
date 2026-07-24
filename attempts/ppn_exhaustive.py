"""Exhaustive search for primary pseudoperfect numbers with exactly k prime factors.

State: primes p_1<...<p_j chosen, N = prod p_i, a = N*(1 - sum 1/p_i)  (integer, gcd(a,N)=1).
Remaining requirement with t = k-j primes left: sum_{i} 1/q_i + 1/(N*Q) = a/N, all q_i > p_j.

Step: q -> N'=N*q, a'=a*q-N.
t==1: q = (N+1)/a must be an integer prime > p_j.
t==2: (a*q1-N)(a*q2-N) = N^2+a  -> factor M=N^2+a.
t>=3: enumerate primes q in (max(p_j, N//a), t*N//a].
"""
import sys, time
from gmpy2 import mpz, is_prime, next_prime

sys.setrecursionlimit(10000)

class Search:
    def __init__(self, k, count_only_depth=None, factor_fn=None):
        self.k = k
        self.nodes = [0]*(k+2)
        self.sols = []
        self.t2_states = 0
        self.count_only = count_only_depth  # if set, do not descend past this depth
        self.factor_fn = factor_fn

    def run(self):
        self.dfs([], mpz(1), mpz(1), self.k)
        return self.sols

    def dfs(self, P, N, a, t):
        j = self.k - t
        self.nodes[j] += 1
        last = P[-1] if P else mpz(1)
        if t == 1:
            if (N + 1) % a == 0:
                q = (N + 1) // a
                if q > last and is_prime(q):
                    self.sols.append(P + [q])
            return
        if t == 2:
            self.t2_states += 1
            if self.count_only is not None:
                return
            M = N*N + a
            for u in self.factor_fn(M):
                if u*u > M:
                    break
                if (u + N) % a:
                    continue
                q1 = (u + N)//a
                if q1 <= last or not is_prime(q1):
                    continue
                v = M//u
                if (v + N) % a:
                    continue
                q2 = (v + N)//a
                if q2 <= q1 or not is_prime(q2):
                    continue
                self.sols.append(P + [q1, q2])
            return
        # t >= 3
        lo = N//a
        if last > lo:
            lo = last
        hi = (t*N)//a
        q = next_prime(lo)
        while q <= hi:
            a2 = a*q - N
            if a2 > 0:
                N2 = N*q
                # prune: need a2/N2 <= sum of 1/r over t-1 primes > q ; upper bound (t-1)/nextprime(q)
                if a2*next_prime(q) <= (t-1)*N2:
                    self.dfs(P + [q], N2, a2, t-1)
            q = next_prime(q)


def divisors_sorted(M):
    from sympy import factorint
    f = factorint(M)
    divs = [1]
    for p, e in f.items():
        divs = [d*p**i for d in divs for i in range(e+1)]
    divs.sort()
    return divs


if __name__ == "__main__":
    kmax = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    mode = sys.argv[2] if len(sys.argv) > 2 else "count"
    for k in range(1, kmax+1):
        t0 = time.time()
        s = Search(k, count_only_depth=(k-2) if mode == "count" else None,
                   factor_fn=divisors_sorted)
        sols = s.run()
        el = time.time()-t0
        print(f"k={k} nodes={s.nodes[:k]} t2_states={s.t2_states} sols={[[int(x) for x in p] for p in sols]} time={el:.1f}s", flush=True)
