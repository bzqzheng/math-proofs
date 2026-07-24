"""
Erdős #993 — search caterpillars (path spine with leaf bunches) for non-unimodal
independence polynomial.  The BrettRey n=30 near-miss has this shape.
"""
import random
import time
from math import comb
from itertools import zip_longest

def ip_caterpillar(a):
    L = len(a)
    def mul(p, q):
        r = [0] * (len(p)+len(q)-1)
        for i, x in enumerate(p):
            if x == 0: continue
            for j, y in enumerate(q):
                r[i+j] += x*y
        return r
    def pow_1x(a):
        return [comb(a, j) for j in range(a+1)]
    cur0 = pow_1x(a[-1])
    cur1 = [0, 1]
    for idx in range(L-2, -1, -1):
        child0 = cur0[:]
        child1 = cur1[:]
        cur0 = mul(pow_1x(a[idx]), [x+y for x,y in zip_longest(child0, child1, fillvalue=0)])
        cur1 = [0] + child0
        Lc = max(len(cur0), len(cur1))
        if len(cur0) < Lc: cur0 += [0]*(Lc-len(cur0))
        if len(cur1) < Lc: cur1 += [0]*(Lc-len(cur1))
    return [x+y for x,y in zip_longest(cur0, cur1, fillvalue=0)]

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

def reproduce_n30():
    a = [9, 0, 8, 0, 8]
    c = ip_caterpillar(a)
    print(f"n30 caterpillar a={a} n={sum(a)+len(a)}")
    print(f"coeffs={c}")
    print(f"unimodal={is_unimodal(c)} ratio={valley_ratio(c):.6f}")

def exhaustive(L, A):
    t0 = time.time()
    best = 0.0; besta = None
    cnt = 0
    def rec(pos, a):
        nonlocal best, besta, cnt
        if pos == L:
            cnt += 1
            c = ip_caterpillar(a)
            if not is_unimodal(c):
                print(f"COUNTEREXAMPLE a={a} n={sum(a)+L}")
                print(f"coeffs={c}")
                print(f"elapsed={time.time()-t0:.1f}s checked={cnt}")
                return True
            r = valley_ratio(c)
            if r > best:
                best = r; besta = a[:]
            return False
        for ai in range(A+1):
            a.append(ai)
            if rec(pos+1, a):
                return True
            a.pop()
        return False
    if rec(0, []):
        return True
    print(f"No counterexample L={L} A={A}. checked={cnt} best_ratio={best:.6f} at {besta}")
    print(f"elapsed={time.time()-t0:.1f}s")
    return False

def simulated_annealing(L, A, steps=100000, T0=0.1, cooling=0.99995, seed=None):
    if seed is None:
        a = [random.randint(0, A) for _ in range(L)]
    else:
        a = seed[:]
    c = ip_caterpillar(a)
    fit = valley_ratio(c)
    best_a, best_fit = a[:], fit
    T = T0
    t0 = time.time()
    last = 0
    print(f"SA L={L} A={A} init a={a} fit={fit:.6f} n={sum(a)+L}")
    for step in range(1, steps+1):
        b = a[:]
        i = random.randrange(L)
        delta = random.randint(-2, 2)
        if delta == 0: delta = 1
        b[i] = max(0, min(A, b[i] + delta))
        if b == a:
            continue
        c2 = ip_caterpillar(b)
        f2 = valley_ratio(c2)
        d = f2 - fit
        if d > 0 or random.random() < (2.718281828459045 ** (d / T)):
            a, c, fit = b, c2, f2
            if fit > best_fit:
                best_a, best_fit = a[:], fit
                print(f"  new best step={step} fit={fit:.6f} a={a} n={sum(a)+L}")
                if best_fit > 1.0:
                    print(f"COUNTEREXAMPLE at step {step}: a={best_a} n={sum(best_a)+L}")
                    print(f"coeffs={ip_caterpillar(best_a)}")
                    return best_a
        T *= cooling
        if step - last >= 5000:
            print(f"  step={step} best={best_fit:.6f} cur={fit:.6f} T={T:.4f} elapsed={time.time()-t0:.1f}s")
            last = step
    print(f"SA done. best_fit={best_fit:.6f} a={best_a} n={sum(best_a)+L}")
    return best_a

if __name__ == "__main__":
    reproduce_n30()
    # Try exhaustive for small L/A
    for L in [3,4,5,6]:
        for A in [5,8,10,12]:
            if exhaustive(L, A):
                raise SystemExit
    # SA for larger
    random.seed(1)
    for L in [5,6,7,8,9,10]:
        for A in [20, 50, 100]:
            simulated_annealing(L, A, steps=20000, T0=0.05, cooling=0.9999)
