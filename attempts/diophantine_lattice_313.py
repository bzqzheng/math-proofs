import sympy
from fractions import Fraction
import time

def verify_primary_pseudoperfect(P):
    s = sum(Fraction(1, p) for p in P)
    res = 1 - s
    if res <= 0:
        return None
    if res.numerator == 1:
        return res.denominator
    return None

def state_graph_search(max_primes=50, max_k=6):
    primes = list(sympy.primerange(2, max_primes + 1))
    print(f"--- HIGHER-DIMENSIONAL DIOPHANTINE STATE GRAPH SEARCH ---")
    print(f"Primes pool up to {max_primes}: count = {len(primes)}")
    
    discovered_m = {}
    
    def dfs(current_P, last_prime_idx, max_k):
        m = verify_primary_pseudoperfect(current_P)
        if m is not None:
            discovered_m[m] = current_P
            print(f"  [DISCOVERED PRIMARY PSEUDOPERFECT NUMBER!] m = {m}, P = {current_P}")
            
        if len(current_P) >= max_k:
            return
            
        s = sum(Fraction(1, p) for p in current_P)
        rem = 1 - s
        if rem <= 0:
            return
            
        R = rem.numerator
        B = rem.denominator
        
        # Single-prime extension condition:
        # A single prime q = (B + d) / R can extend if d | B and q is prime
        divs_B = sympy.divisors(B)
        for d in divs_B:
            num = B + d
            if num % R == 0:
                q = num // R
                if q > current_P[-1] and sympy.isprime(q):
                    next_P = current_P + [q]
                    m_ext = verify_primary_pseudoperfect(next_P)
                    if m_ext is not None and m_ext not in discovered_m:
                        discovered_m[m_ext] = next_P
                        print(f"  [1-STEP TRANSITION SUCCESS!] q = {q} -> m = {m_ext}, P = {next_P}")
                        
        # Continue DFS for general transitions
        for i in range(last_prime_idx + 1, len(primes)):
            q = primes[i]
            if Fraction(1, q) < rem:
                dfs(current_P + [q], i, max_k)

    # Launch DFS from initial prime choices
    for i, p0 in enumerate(primes):
        dfs([p0], i, max_k)
        
    return discovered_m

if __name__ == "__main__":
    t0 = time.time()
    res = state_graph_search(max_primes=100, max_k=6)
    t1 = time.time()
    print(f"\nSearch completed in {t1-t0:.2f} seconds.")
    print(f"Total unique primary pseudoperfect numbers found: {len(res)}")
    for m in sorted(res.keys()):
        print(f"  m = {m} -> P = {res[m]}")
