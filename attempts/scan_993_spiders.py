"""
Erdős #993 — scan spiders and star-arm trees for non-unimodal independence polynomial.

Spider S(a,b,c): center connected to three paths of lengths a,b,c (vertices per arm incl neighbor).
I(S) = P_a P_b P_c + x P_{a-1} P_{b-1} P_{c-1}.

Star-arm S(m1,m2,m3): center connected to stars K_{1,m1}, K_{1,m2}, K_{1,m3}.
I = prod(1+m_i x) + x prod((1+x)^{m_i}).
"""
import time
from itertools import combinations_with_replacement

def path_ip(n):
    """Independence polynomial of path P_n (n vertices)."""
    if n < 0:
        return [1]
    if n == 0:
        return [1]
    dp = [[1], [1, 1]]  # P_0, P_1
    for i in range(2, n + 1):
        prev, prev2 = dp[i-1], dp[i-2]
        cur = [0] * (len(prev) + 1)
        for j, a in enumerate(prev):
            cur[j] += a
        for j, a in enumerate(prev2):
            cur[j+1] += a
        dp.append(cur)
    return dp[n]

def is_unimodal(c):
    return not any(c[k-1] > c[k] and c[k+1] > c[k] for k in range(1, len(c)-1))

def valley_ratio(c):
    best = 0.0
    for k in range(1, len(c)-1):
        if c[k]:
            r = min(c[k-1], c[k+1]) / c[k]
            if r > best:
                best = r
    return best

def spider_ip(a, b, c):
    pa, pb, pc = path_ip(a), path_ip(b), path_ip(c)
    pam, pbm, pcm = path_ip(a-1), path_ip(b-1), path_ip(c-1)
    # product pa*pb*pc
    def mul(p, q):
        r = [0] * (len(p)+len(q)-1)
        for i, x in enumerate(p):
            if x == 0: continue
            for j, y in enumerate(q):
                r[i+j] += x*y
        return r
    first = mul(mul(pa, pb), pc)
    second = [0] + mul(mul(pam, pbm), pcm)
    return [x+y for x,y in zip(first, second)]

def scan_spiders(A):
    t0 = time.time()
    best = 0.0; bestp = None
    cnt = 0
    for a in range(1, A+1):
        for b in range(a, A+1):
            for c in range(b, A+1):
                cnt += 1
                coeffs = spider_ip(a,b,c)
                if not is_unimodal(coeffs):
                    print(f"SPIDER COUNTEREXAMPLE a={a} b={b} c={c} n={a+b+c+1}")
                    print(f"coeffs={coeffs}")
                    print(f"elapsed={time.time()-t0:.1f}s checked={cnt}")
                    return True
                r = valley_ratio(coeffs)
                if r > best:
                    best = r; bestp = (a,b,c)
    print(f"No spider counterexample up to A={A}. checked={cnt} best_ratio={best:.6f} at {bestp}")
    print(f"elapsed={time.time()-t0:.1f}s")
    return False

def scan_star_arms(M):
    t0 = time.time()
    best = 0.0; bestp = None
    cnt = 0
    # precompute binomials
    from math import comb
    for m1 in range(1, M+1):
        for m2 in range(m1, M+1):
            for m3 in range(m2, M+1):
                cnt += 1
                Msum = m1+m2+m3
                e1 = Msum
                e2 = m1*m2 + m1*m3 + m2*m3
                e3 = m1*m2*m3
                coeffs = [1, e1+1]
                # c_k = e_k + C(Msum, k-1) for k=1,2,3; e_k=0 for k>3
                for k in range(2, Msum+2):
                    if k <= 3:
                        ek = [e2, e3][k-2]
                    else:
                        ek = 0
                    coeffs.append(ek + comb(Msum, k-1))
                if not is_unimodal(coeffs):
                    print(f"STAR COUNTEREXAMPLE m={m1},{m2},{m3} n={Msum+4}")
                    print(f"coeffs={coeffs[:12]}...")
                    return True
                r = valley_ratio(coeffs)
                if r > best:
                    best = r; bestp = (m1,m2,m3)
    print(f"No star counterexample up to M={M}. checked={cnt} best_ratio={best:.6f} at {bestp}")
    print(f"elapsed={time.time()-t0:.1f}s")
    return False

if __name__ == "__main__":
    scan_spiders(200)
    scan_star_arms(100)
