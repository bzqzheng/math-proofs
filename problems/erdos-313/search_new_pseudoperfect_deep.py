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

def deep_search_new_roots():
    print("--- DEEP SEARCH FOR NEW PRIMARY PSEUDOPERFECT ROOTS ---")
    
    # We test initial prefix combinations [2, p2, p3] with p2 in [3, 5], p3 in primes up to 100
    base_primes = list(sympy.primerange(3, 100))
    
    discovered = {}
    
    def dfs(P, depth, max_depth):
        m = verify_primary_pseudoperfect(P)
        if m is not None and m not in discovered:
            discovered[m] = P
            print(f"!!! DISCOVERED NEW PRIMARY PSEUDOPERFECT ROOT !!!")
            print(f"  m = {m} (digits = {len(str(m))})")
            print(f"  P = {P}\n")
            
        if depth >= max_depth:
            return
            
        s = sum(Fraction(1, p) for p in P)
        rem = 1 - s
        if rem <= 0:
            return
            
        R = rem.numerator
        B = rem.denominator
        
        # Test 1-step extensions via d | B
        divs = sympy.divisors(B)
        for d in divs:
            num = B + d
            if num % R == 0:
                q = num // R
                if q > P[-1] and sympy.isprime(q):
                    next_P = P + [q]
                    dfs(next_P, depth + 1, max_depth)

    print("Launching deep state graph exploration across prime prefixes...")
    t0 = time.time()
    
    # Test prefixes [2, 3, p3] and [2, 5, p3]
    for p2 in [3, 5, 7]:
        for p3 in base_primes:
            if p3 > p2:
                dfs([2, p2, p3], 3, max_depth=12)
                
    t1 = time.time()
    print(f"Deep search completed in {t1-t0:.2f} seconds.")
    print(f"Total unique primary pseudoperfect numbers found: {len(discovered)}")
    for m in sorted(discovered.keys()):
        print(f"  m = {m} (digits = {len(str(m))}) -> P = {discovered[m]}")

if __name__ == "__main__":
    deep_search_new_roots()
