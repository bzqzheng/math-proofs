import math
from fractions import Fraction
import sympy

def verify_primary_pseudoperfect(m, P):
    s = sum(Fraction(1, p) for p in P)
    res = 1 - s
    if res <= 0:
        return False
    return res.numerator == 1 and res.denominator == m

def find_1prime_extensions(m, P):
    extensions = []
    divs = sympy.divisors(m)
    for d in divs:
        q = m + d
        if q not in P and sympy.isprime(q):
            new_m = (m // d) * q
            new_P = sorted(P + [q])
            if verify_primary_pseudoperfect(new_m, new_P):
                extensions.append((new_m, new_P))
    return extensions

def find_2prime_extensions(m, P):
    extensions = []
    val = m*m + 1
    # Factor val or get divisors
    divs = sympy.divisors(val)
    for d in divs:
        p7 = m + d
        p8 = m + (val // d)
        if p7 < p8 and p7 not in P and p8 not in P:
            if sympy.isprime(p7) and sympy.isprime(p8):
                new_m = m * p7 * p8
                new_P = sorted(P + [p7, p8])
                if verify_primary_pseudoperfect(new_m, new_P):
                    extensions.append((new_m, new_P))
    return extensions

if __name__ == "__main__":
    print("--- Primary Pseudoperfect Numbers Exploration (Erdos #313 / OEIS A054377) ---")
    
    known = [
        (2, [2]),
        (6, [2, 3]),
        (42, [2, 3, 7]),
        (1806, [2, 3, 7, 43]),
        (47058, [2, 3, 11, 23, 31]),
        (2214502422, [2, 3, 11, 23, 31, 47059]),
        (52495396602, [2, 3, 11, 17, 101, 149, 3109]),
        (8490421583559688410706771261086, [2, 3, 11, 23, 31, 47059, 2217342227, 1729101023519])
    ]
    
    print("\nScanning 1-prime and 2-prime extensions of all known terms:")
    all_terms = {}
    for m, P in known:
        all_terms[m] = P

    for m, P in known:
        print(f"\n--- Analyzing m = {m} (P = {P}) ---")
        ext1 = find_1prime_extensions(m, P)
        print(f"  1-prime extensions found: {len(ext1)}")
        for em, eP in ext1:
            all_terms[em] = eP
            print(f"    m' = {em}, P' = {eP}")

        # Search 2-prime extensions if m <= 10^12
        if m <= 10^12:
            ext2 = find_2prime_extensions(m, P)
            print(f"  2-prime extensions found: {len(ext2)}")
            for em, eP in ext2:
                all_terms[em] = eP
                print(f"    m' = {em}, P' = {eP}")

    print("\n=== TOTAL UNIQUE PRIMARY PSEUDOPERFECT NUMBERS FOUND ===")
    sorted_all = sorted(all_terms.keys())
    for idx, m in enumerate(sorted_all):
        print(f"Term {idx+1}: m = {m} (digits = {len(str(m))})")
        print(f"  P = {all_terms[m]}")


