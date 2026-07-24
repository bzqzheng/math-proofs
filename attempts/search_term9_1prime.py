import sympy
from fractions import Fraction

def verify_primary_pseudoperfect(m, P):
    s = sum(Fraction(1, p) for p in P)
    res = 1 - s
    if res <= 0:
        return False
    return res.numerator == 1 and res.denominator == m

def search_term9_1prime():
    m8 = 8490421583559688410706771261086
    P8 = [2, 3, 11, 23, 31, 47059, 2217342227, 1729101023519]
    
    print("--- SEARCHING 1-PRIME EXTENSIONS OF TERM 8 (m8) ---")
    divs = sympy.divisors(m8)
    print(f"Total divisors of m8: {len(divs)}")
    
    found = []
    for d in divs:
        q = m8 + d
        if q not in P8 and sympy.isprime(q):
            m9 = (m8 // d) * q
            P9 = sorted(P8 + [q])
            if verify_primary_pseudoperfect(m9, P9):
                found.append((m9, P9, d, q))
                print(f"!!! DISCOVERED 9TH PRIMARY PSEUDOPERFECT NUMBER (1-PRIME EXTENSION) !!!")
                print(f"  d = {d}")
                print(f"  q = {q}")
                print(f"  m9 = {m9} (digits = {len(str(m9))})")
                print(f"  P9 = {P9}\n")

    if not found:
        print("No 1-prime extensions found for m8.")
    return found

if __name__ == "__main__":
    search_term9_1prime()
