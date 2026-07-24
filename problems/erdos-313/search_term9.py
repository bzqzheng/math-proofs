import sympy
from fractions import Fraction
import time

def verify_primary_pseudoperfect(m, P):
    s = sum(Fraction(1, p) for p in P)
    res = 1 - s
    if res <= 0:
        return False
    return res.numerator == 1 and res.denominator == m

def search_term9():
    m8 = 8490421583559688410706771261086
    P8 = [2, 3, 11, 23, 31, 47059, 2217342227, 1729101023519]
    
    print(f"--- TRACK 1: SEARCHING FOR TERM 9 (Erdos #313 / OEIS A054377) ---")
    print(f"Base m8 = {m8}")
    print(f"Digits of m8 = {len(str(m8))}")
    print(f"P8 = {P8}\n")
    
    val = m8 * m8 + 1
    print(f"val = m8^2 + 1 = {val}")
    print(f"Digits of val = {len(str(val))}")
    
    t0 = time.time()
    print("Factoring val (61 digits)...")
    # Attempt factoring using sympy
    factors = sympy.factorint(val)
    t1 = time.time()
    print(f"Factorization completed in {t1-t0:.2f} seconds.")
    print(f"Prime factors: {factors}\n")
    
    divs = sympy.divisors(val)
    print(f"Total divisors of m8^2 + 1: {len(divs)}")
    
    term9_found = []
    for d in divs:
        p1 = m8 + d
        p2 = m8 + (val // d)
        if p1 < p2 and p1 not in P8 and p2 not in P8:
            if sympy.isprime(p1) and sympy.isprime(p2):
                m9 = m8 * p1 * p2
                P9 = sorted(P8 + [p1, p2])
                if verify_primary_pseudoperfect(m9, P9):
                    term9_found.append((m9, P9, d, p1, p2))
                    print(f"!!! DISCOVERED 9TH PRIMARY PSEUDOPERFECT NUMBER !!!")
                    print(f"  d = {d}")
                    print(f"  p1 = {p1}")
                    print(f"  p2 = {p2}")
                    print(f"  m9 = {m9}")
                    print(f"  Digits of m9 = {len(str(m9))}")
                    print(f"  P9 = {P9}\n")

    if not term9_found:
        print("No 2-prime extensions found for m8 via m8^2+1 divisors.")
    return term9_found

if __name__ == "__main__":
    search_term9()
