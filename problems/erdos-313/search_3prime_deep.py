import sympy
from fractions import Fraction

def verify_primary_pseudoperfect(m, P):
    s = sum(Fraction(1, p) for p in P)
    res = 1 - s
    if res <= 0:
        return False
    return res.numerator == 1 and res.denominator == m

def search_deep():
    known = [
        (47058, [2, 3, 11, 23, 31]),
        (2214502422, [2, 3, 11, 23, 31, 47059]),
        (52495396602, [2, 3, 11, 17, 101, 149, 3109]),
        (8490421583559688410706771261086, [2, 3, 11, 23, 31, 47059, 2217342227, 1729101023519])
    ]
    
    print("--- DEEP 3-PRIME EXTENSION SEARCH ---")
    for m, P in known:
        print(f"\nEvaluating m = {m} (digits = {len(str(m))})...")
        divs = sympy.divisors(m)
        found_count = 0
        for d1 in divs:
            q1 = m + d1
            if q1 not in P and sympy.isprime(q1):
                M = (m // d1) * q1
                val = M * M + 1
                if len(str(val)) <= 70:
                    factors = sympy.factorint(val)
                    divs_M = sympy.divisors(val)
                    for d2 in divs_M:
                        q2 = M + d2
                        q3 = M + (val // d2)
                        if q2 < q3 and q2 not in P and q3 not in P and q2 != q1 and q3 != q1:
                            if sympy.isprime(q2) and sympy.isprime(q3):
                                m9 = M * q2 * q3
                                P9 = sorted(P + [q1, q2, q3])
                                if verify_primary_pseudoperfect(m9, P9):
                                    found_count += 1
                                    print(f"!!! DISCOVERED NEW PRIMARY PSEUDOPERFECT NUMBER !!!")
                                    print(f"  Parent m = {m}")
                                    print(f"  Added primes = ({q1}, {q2}, {q3})")
                                    print(f"  new m = {m9} (digits = {len(str(m9))})")
                                    print(f"  P = {P9}\n")
        print(f"Completed m = {m}: total 3-prime extensions found = {found_count}")

if __name__ == "__main__":
    search_deep()
