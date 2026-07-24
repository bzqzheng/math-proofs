import sympy

def explore_zsigmondy_factors():
    print("--- APPROACH 9: ZSIGMONDY-TYPE PRIMITIVE PRIME FACTOR ANALYSIS ---")
    
    known_m = [2, 6, 42, 1806, 47058, 2214502422, 52495396602]
    
    print("\nTheorem Analysis (Primitive Prime Factors of m^2 + 1):")
    print("For any integer m >= 2, m^2 + 1 has no square factors among primes p = 3 mod 4.")
    print("Every prime factor p of m^2 + 1 must satisfy p = 1 mod 4 (or p = 2 for m odd).")
    print("Since all known primary pseudoperfect m are EVEN, m^2 + 1 is ALWAYS ODD.")
    print("Thus ALL prime factors of m^2 + 1 are odd primes p = 1 mod 4!\n")
    
    for m in known_m:
        val = m * m + 1
        factors = sympy.factorint(val)
        print(f"m = {m} -> m^2+1 = {val}")
        print(f"  Prime factors: {factors}")
        print(f"  All factors 1 mod 4? {all(p % 4 == 1 for p in factors.keys())}")

if __name__ == "__main__":
    explore_zsigmondy_factors()
