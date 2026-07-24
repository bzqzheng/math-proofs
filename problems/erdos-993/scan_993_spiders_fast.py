"""Fast scan of spider and star-arm trees for non-unimodal independence polynomial."""
import time
from math import comb

def path_ips(max_n):
    P = [[1], [1,1]]
    for i in range(2, max_n+1):
        prev, prev2 = P[i-1], P[i-2]
        cur = [0] * (len(prev)+1)
        for j, a in enumerate(prev):
            cur[j] += a
        for j, a in enumerate(prev2):
            cur[j+1] += a
        P.append(cur)
    return P

def conv(p, q):
    r = [0] * (len(p)+len(q)-1)
    for i, a in enumerate(p):
        if a == 0:
            continue
        ri = r[i:]
        for j, b in enumerate(q):
            ri[j] += a*b
    return r

def spider_ip(a, b, c, P):
    first = conv(conv(P[a], P[b]), P[c])
    second = conv(conv(P[a-1], P[b-1]), P[c-1])
    second.insert(0, 0)
    L = max(len(first), len(second))
    if len(first) < L:
        first += [0]*(L-len(first))
    if len(second) < L:
        second += [0]*(L-len(second))
    return [x+y for x,y in zip(first, second)]

def is_unimodal(c):
    for k in range(1, len(c)-1):
        if c[k-1] > c[k] and c[k+1] > c[k]:
            return False
    return True

def valley_ratio(c):
    best = 0.0
    for k in range(1, len(c)-1):
        if c[k]:
            r = min(c[k-1], c[k+1]) / c[k]
            if r > best:
                best = r
    return best

def scan_spiders(A):
    P = path_ips(A)
    t0 = time.time()
    best = 0.0; bestp = None
    cnt = 0
    for a in range(1, A+1):
        for b in range(1, A+1):
            for c in range(1, A+1):
                cnt += 1
                coeffs = spider_ip(a,b,c,P)
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
    for m1 in range(1, M+1):
        for m2 in range(1, M+1):
            for m3 in range(1, M+1):
                cnt += 1
                Msum = m1+m2+m3
                e2 = m1*m2 + m1*m3 + m2*m3
                e3 = m1*m2*m3
                coeffs = [1, Msum+1, e2+Msum, e3+comb(Msum,2)]
                for k in range(4, Msum+2):
                    coeffs.append(comb(Msum, k-1))
                if not is_unimodal(coeffs):
                    print(f"STAR COUNTEREXAMPLE m={m1},{m2},{m3} n={Msum+4}")
                    print(f"coeffs={coeffs[:16]}...")
                    return True
                r = valley_ratio(coeffs)
                if r > best:
                    best = r; bestp = (m1,m2,m3)
    print(f"No star counterexample up to M={M}. checked={cnt} best_ratio={best:.6f} at {bestp}")
    print(f"elapsed={time.time()-t0:.1f}s")
    return False

if __name__ == "__main__":
    scan_spiders(50)
    scan_star_arms(120)
