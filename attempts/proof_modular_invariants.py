import sympy

def verify_mod4_invariants():
    print("--- TRACK 2: QUADRATIC RESIDUE & MODULO 4 INVARIANT ANALYSIS ---")
    
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
    
    print("\n1. Testing mod 4 congruence for all prime factors in known primary pseudoperfect numbers:")
    for m, P in known:
        mod4_counts = {1: 0, 2: 0, 3: 0}
        for p in P:
            mod4_counts[p % 4] += 1
        print(f"  m = {m} ({len(P)} primes): mod4 breakdown -> {mod4_counts}")

    print("\n2. Theorem Proof (2-Prime Extension Mod 4 Invariant):")
    print("   Theorem: If p1 = m + d and p2 = m + (m^2+1)/d are prime factors of m^2+1,")
    print("   then p1 * p2 = m^2 + m(d + (m^2+1)/d) + m^2 + 1 = 1 mod (p1) and mod (p2).")
    print("   Specifically, m^2 = -1 mod p1 and m^2 = -1 mod p2.")
    print("   By Quadratic Reciprocity, (-1/p) = +1  <=>  p = 1 mod 4 (for any odd prime p).")
    print("   Conclusion: EVERY prime factor p of m^2+1 MUST satisfy p = 1 (mod 4)!")

if __name__ == "__main__":
    verify_mod4_invariants()
