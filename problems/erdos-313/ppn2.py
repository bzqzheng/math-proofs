"""Exhaustive PPN search, v2.

State (P, N, A, t): primes p_1<...<p_j chosen, N=prod, A = N*(1 - sum 1/p_i), t=k-j left.
Need: sum_{i=1..t} 1/q_i + 1/(N*Q) = A/N with p_j < q_1 < ... < q_t.
Step: A' = A*q - N,  N' = N*q.

t==1: q = (N+1)/A prime.
t==2: q_2 = (N*q_1+1)/(A*q_1-N).  Two modes:
        (a) iterate q_1 over primes in (max(p_j,N/A), 2N/A]  -- cheap when N/A small
        (b) (A q_1 - N)(A q_2 - N) = N^2 + A -- factor, cheap when N/A large
t>=3: iterate q over primes in (max(p_j,N/A), t*N/A).
"""
import sys, time
from gmpy2 import mpz, is_prime, next_prime, isqrt

sys.setrecursionlimit(100000)

ITER_LIMIT = 0   # 0 => always use the divisor/factoring route at t==2


def _rho(n, tries=40):
    from gmpy2 import gcd
    import random
    if n % 2 == 0:
        return mpz(2)
    for _ in range(tries):
        c = mpz(random.randrange(1, n))
        x = mpz(random.randrange(0, n)); y = x; d = mpz(1)
        ys = y; r = 1; q = mpz(1)
        while d == 1:
            x = y
            for _ in range(r):
                y = (y*y + c) % n
            k = 0
            while k < r and d == 1:
                ys = y
                for _ in range(min(128, r-k)):
                    y = (y*y + c) % n
                    q = q*abs(x-y) % n
                d = gcd(q, n)
                k += 128
            r *= 2
        if d != n:
            return d
        y = ys
        d = mpz(1)
        while d == 1:
            y = (y*y+c) % n
            d = gcd(abs(x-y), n)
        if d != n:
            return d
    return None


SMALL_PRIMES = []
def _init_small():
    global SMALL_PRIMES
    if SMALL_PRIMES:
        return
    lim = 100000
    sieve = bytearray([1])*lim
    sieve[0] = sieve[1] = 0
    for i in range(2, int(lim**0.5)+1):
        if sieve[i]:
            sieve[i*i::i] = bytearray(len(sieve[i*i::i]))
    SMALL_PRIMES = [i for i in range(lim) if sieve[i]]


def factorize(n):
    """Return dict prime->exp."""
    _init_small()
    f = {}
    n = mpz(n)
    for p in SMALL_PRIMES:
        if p*p > n:
            break
        while n % p == 0:
            f[mpz(p)] = f.get(mpz(p), 0)+1
            n //= p
    if n == 1:
        return f
    stack = [n]
    while stack:
        m = stack.pop()
        if m == 1:
            continue
        if is_prime(m):
            f[m] = f.get(m, 0)+1
            continue
        r = isqrt(m)
        if r*r == m:
            stack += [r, r]
            continue
        d = _rho(m)
        if d is None:
            from sympy import factorint
            for p, e in factorint(int(m)).items():
                f[mpz(p)] = f.get(mpz(p), 0)+e
            continue
        stack.append(d); stack.append(m//d)
    return f


def divisors_from(f):
    divs = [mpz(1)]
    for p, e in f.items():
        divs = [d*p**i for d in divs for i in range(e+1)]
    divs.sort()
    return divs


class Search:
    def __init__(self, k, log_every=0, cap_nodes=None):
        self.k = k
        self.nodes = [0]*(k+2)
        self.t2 = 0
        self.t2_factor = 0
        self.sols = []
        self.log_every = log_every
        self.t0 = time.time()
        self.cap = cap_nodes
        self.aborted = []

    def emit(self, P):
        self.sols.append([int(x) for x in P])
        print(f"  *** SOLUTION k={self.k}: {[int(x) for x in P]}  n={int(_prod(P))}", flush=True)

    def run(self, start=None):
        if start is None:
            self.dfs([], mpz(1), mpz(1), self.k)
        else:
            P = [mpz(x) for x in start]
            N = mpz(1); A = mpz(1)
            for q in P:
                A = A*q - N; N = N*q
            self.dfs(P, N, A, self.k-len(P))
        return self.sols

    def dfs(self, P, N, A, t):
        j = self.k - t
        self.nodes[j] += 1
        if self.log_every and self.nodes[j] % self.log_every == 0:
            print(f"    [d{j} n={self.nodes[j]} t2={self.t2} {time.time()-self.t0:.0f}s] {[int(x) for x in P]}", flush=True)
        last = P[-1] if P else mpz(1)
        if t == 1:
            if (N + 1) % A == 0:
                q = (N + 1) // A
                if q > last and is_prime(q):
                    self.emit(P + [q])
            return
        if t == 2:
            self.t2 += 1
            self.solve2(P, N, A, last)
            return
        lo = N//A
        if last > lo:
            lo = last
        hi = (t*N - 1)//A
        q = next_prime(lo)
        while q <= hi:
            A2 = A*q - N
            if A2 > 0:
                N2 = N*q
                if A2*next_prime(q) <= (t-1)*N2:
                    self.dfs(P + [q], N2, A2, t-1)
            q = next_prime(q)

    def solve2(self, P, N, A, last):
        lo = N//A
        if last > lo:
            lo = last
        # q1 < (N + sqrt(N^2+A))/A
        hi = (2*N)//A + 1
        span = hi - lo
        if span <= ITER_LIMIT:
            q = next_prime(lo)
            while q <= hi:
                den = A*q - N
                if den > 0:
                    num = N*q + 1
                    if num % den == 0:
                        q2 = num//den
                        if q2 > q and is_prime(q2):
                            self.emit(P + [q, q2])
                q = next_prime(q)
        else:
            self.t2_factor += 1
            M = N*N + A
            try:
                f = factorize(M)
            except Exception as e:
                self.aborted.append(([int(x) for x in P], str(e)))
                return
            for u in divisors_from(f):
                if u*u > M:
                    break
                if (u + N) % A:
                    continue
                q1 = (u + N)//A
                if q1 <= last or not is_prime(q1):
                    continue
                v = M//u
                if (v + N) % A:
                    continue
                q2 = (v + N)//A
                if q2 > q1 and is_prime(q2):
                    self.emit(P + [q1, q2])


def _prod(P):
    r = mpz(1)
    for x in P:
        r *= x
    return r


if __name__ == "__main__":
    k = int(sys.argv[1])
    start = [int(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 and sys.argv[2] else None
    s = Search(k, log_every=int(sys.argv[3]) if len(sys.argv) > 3 else 0)
    t0 = time.time()
    s.run(start)
    print(f"k={k} start={start} nodes={s.nodes[:k]} t2={s.t2} t2_factor={s.t2_factor} "
          f"sols={len(s.sols)} aborted={len(s.aborted)} time={time.time()-t0:.1f}s", flush=True)
