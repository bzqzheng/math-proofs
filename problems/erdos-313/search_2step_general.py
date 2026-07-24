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

def search_2step_general():
    print("--- GENERALIZED 2-STEP EXTENSION EXPLORER ACROSS ALL PRIME PREFIXES ---")
    
    primes = list(sympy.primerange(2, 500))
    print(f"Base prime pool: {len(primes)} primes up to 500.")
    
    discovered = {}
    
    # Generate partial prime sets of size 2, 3, 4, 5
    from itertools import combinations
    
    t0 = time.time()
    count_tested = 0
    for k in range(1, 5):
        print(f"\nTesting prime subsets of size k = {k}...")
        for P in combinations(primes[:50], k):
            count_tested += 1
            s = sum(Fraction(1, p) for p in P)
            rem = 1 - s
            if rem <= 0:
                continue
            R, B = rem.numerator, rem.denominator
            
            # Check 1-step extensions
            for d in sympy.divisors(B):
                if (B + d) % R == 0:
                    q = (B + d) // R
                    if q > P[-1] and sympy.isprime(q):
                        m = verify_primary_pseudoperfect(list(P) + [q])
                        if m is not None and m not in discovered:
                            discovered[m] = list(P) + [q]
                            print(f"  [DISCOVERED VIA 1-STEP!] m = {m} -> P = {list(P) + [q]}")
                            
            # Check 2-step extensions when R = 1 (m = B)
            if R == 1:
                m = B
                val = m*m + 1
                for d in sympy.divisors(val):
                    p1 = m + d
                    p2 = m + (val // d)
                    if p1 < p2 and p1 > P[-1] and p2 > P[-1]:
                        if sympy.isprime(p1) and sympy.isprime(p2):
                            m_ext = verify_primary_pseudoperfect(list(P) + [p1, p2])
                            if m_ext is not None and m_ext not in discovered:
                                discovered[m_ext] = list(P) + [p1, p2]
                                print(f"  [DISCOVERED VIA 2-STEP!] m = {m_ext} -> P = {list(P) + [p1, p2]}")
                                
    t1 = time.time()
    print(f"\nCompleted search in {t1-t0:.2f} seconds. Total tested: {count_tested}")
    print(f"Total unique primary pseudoperfect numbers found: {len(discovered)}")
    for m in sorted(discovered.keys()):
        print(f"  m = {m} (digits = {len(str(m))}) -> P = {discovered[m]}")

if __name__ == "__main__":
    search_2step_general()
