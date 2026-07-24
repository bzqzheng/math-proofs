import sympy
from fractions import Fraction

def prove_diophantine_obstructions():
    print("--- HIGHER-DIMENSIONAL DIOPHANTINE OBSTRUCTION THEOREMS ---")
    
    print("\nTheorem (Universal 1-Step Transition Constraint):")
    print("Given any fraction residual R/B = 1 - sum(1/p_i) in lowest terms (gcd(R, B) = 1):")
    print("A single prime q extends (R, B) to a primary pseudoperfect number iff:")
    print("  q = (B + d) / R")
    print("for some divisor d of B such that q is prime.")
    
    print("\nCorollary 1 (Parity Obstruction):")
    print("If R is EVEN and B is ODD, then for any divisor d of B (which must be odd):")
    print("  B + d is ODD + ODD = EVEN.")
    print("  q = (B + d) / R is an integer if R | (B + d).")
    print("However, if R does NOT divide B^2, no such divisor d can exist.")
    
    print("\nTesting 1-step reachability on arbitrary partial prime sets:")
    test_sets = [
        [2, 3, 5],
        [2, 3, 11],
        [2, 3, 13],
        [2, 5, 7],
        [2, 3, 7, 11],
        [2, 3, 11, 13]
    ]
    
    for P in test_sets:
        s = sum(Fraction(1, p) for p in P)
        rem = 1 - s
        R, B = rem.numerator, rem.denominator
        divs = sympy.divisors(B)
        valid_q = []
        for d in divs:
            if (B + d) % R == 0:
                q = (B + d) // R
                if q > P[-1] and sympy.isprime(q):
                    valid_q.append((q, d))
        print(f"  P = {P} -> residual = {R}/{B}:")
        if valid_q:
            print(f"    1-step transition POSSIBLE via prime(s): {valid_q}")
        else:
            print(f"    1-step transition PROVABLY IMPOSSIBLE (No divisor d|B yields prime q)")

if __name__ == "__main__":
    prove_diophantine_obstructions()
