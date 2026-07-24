import sympy
from fractions import Fraction

def explore_sylvester_branching():
    print("--- APPROACH 1: SYLVESTER SEQUENCE BRANCHING ---")
    
    # Standard Sylvester Sequence: E_1 = 2, E_{k+1} = E_k^2 - E_k + 1
    E = [2]
    for _ in range(7):
        next_E = E[-1]**2 - E[-1] + 1
        E.append(next_E)
        
    print(f"Sylvester terms E_1..E_8:")
    for idx, e in enumerate(E):
        is_p = sympy.isprime(e)
        print(f"  E_{idx+1} = {e} (digits = {len(str(e))}) -> Prime: {is_p}")
        if not is_p:
            factors = sympy.factorint(e)
            print(f"    Prime factorization of E_{idx+1}: {factors}")

if __name__ == "__main__":
    explore_sylvester_branching()
