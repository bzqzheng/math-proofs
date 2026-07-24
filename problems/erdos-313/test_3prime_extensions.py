import sympy
from fractions import Fraction

def verify_primary_pseudoperfect(m, P):
    s = sum(Fraction(1, p) for p in P)
    res = 1 - s
    if res <= 0:
        return False
    return res.numerator == 1 and res.denominator == m

def search_3prime_extensions(m, P):
    print(f"\n==========================================")
    print(f"Searching 3-prime extensions for m = {m} (digits = {len(str(m))})")
    divs_m = sympy.divisors(m)
    
    new_found = []
    for d1 in divs_m:
        q1 = m + d1
        if q1 not in P and sympy.isprime(q1):
            M = (m // d1) * q1
            P_intermediate = sorted(P + [q1])
            # Now test 2-prime extensions on M:
            val = M * M + 1
            # To be efficient, check digit length of val
            if len(str(val)) <= 35:
                factors_M = sympy.factorint(val)
                divs_M = sympy.divisors(val)
                for d2 in divs_M:
                    q2 = M + d2
                    q3 = M + (val // d2)
                    if q2 < q3 and q2 not in P_intermediate and q3 not in P_intermediate:
                        if sympy.isprime(q2) and sympy.isprime(q3):
                            new_m = M * q2 * q3
                            new_P = sorted(P_intermediate + [q2, q3])
                            if verify_primary_pseudoperfect(new_m, new_P):
                                new_found.append((new_m, new_P, q1, q2, q3))
                                print(f"  [NEW 3-PRIME PSEUDOPERFECT NUMBER DISCOVERED!]")
                                print(f"    q1 = {q1}, q2 = {q2}, q3 = {q3}")
                                print(f"    new_m = {new_m} (digits = {len(str(new_m))})")
                                print(f"    new_P = {new_P}")
    return new_found

if __name__ == "__main__":
    known = [
        (2, [2]),
        (6, [2, 3]),
        (42, [2, 3, 7]),
        (1806, [2, 3, 7, 43]),
        (47058, [2, 3, 11, 23, 31]),
        (2214502422, [2, 3, 11, 23, 31, 47059]),
        (52495396602, [2, 3, 11, 17, 101, 149, 3109]),
    ]
    
    total = 0
    for m, P in known:
        res = search_3prime_extensions(m, P)
        total += len(res)
        
    print(f"\nTotal new 3-prime primary pseudoperfect numbers found: {total}")
