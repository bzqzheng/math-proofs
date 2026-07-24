import sympy
from fractions import Fraction

def verify_primary_pseudoperfect(m, P):
    s = sum(Fraction(1, p) for p in P)
    res = 1 - s
    if res <= 0:
        return False
    return res.numerator == 1 and res.denominator == m

def test_m_squared_plus_1(m, P):
    print(f"\n==========================================")
    print(f"Testing 2-prime extensions for m = {m}")
    print(f"P = {P}")
    val = m * m + 1
    print(f"m^2 + 1 = {val}")
    factors = sympy.factorint(val)
    print(f"Prime factorization of m^2 + 1: {factors}")
    divs = sympy.divisors(val)
    print(f"Total divisors: {len(divs)}")
    
    valid_extensions = []
    for d in divs:
        p1 = m + d
        p2 = m + (val // d)
        if p1 < p2 and p1 not in P and p2 not in P:
            if sympy.isprime(p1) and sympy.isprime(p2):
                new_m = m * p1 * p2
                new_P = sorted(P + [p1, p2])
                if verify_primary_pseudoperfect(new_m, new_P):
                    valid_extensions.append((new_m, new_P, d, p1, p2))
                    print(f"  [FOUND 2-PRIME EXTENSION!]")
                    print(f"    d = {d}")
                    print(f"    p1 = {p1}")
                    print(f"    p2 = {p2}")
                    print(f"    new_m = {new_m}")
                    print(f"    new_P = {new_P}")
    
    return valid_extensions

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
    
    all_found = []
    for m, P in known:
        exts = test_m_squared_plus_1(m, P)
        all_found.extend(exts)

    print("\n==========================================")
    print(f"Total 2-prime extensions found: {len(all_found)}")
