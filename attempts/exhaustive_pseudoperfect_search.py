import sympy
from fractions import Fraction
from itertools import combinations

def verify_primary_pseudoperfect(P):
    s = sum(Fraction(1, p) for p in P)
    res = 1 - s
    if res <= 0:
        return None
    if res.numerator == 1:
        return res.denominator
    return None

def exhaustive_search(max_prime=500, max_k=6):
    primes = list(sympy.primerange(2, max_prime + 1))
    print(f"Primes up to {max_prime}: count = {len(primes)}")
    
    found = {}
    for k in range(1, max_k + 1):
        print(f"Searching k = {k} primes...")
        count_checked = 0
        for P in combinations(primes, k):
            count_checked += 1
            m = verify_primary_pseudoperfect(P)
            if m is not None:
                found[m] = P
                print(f"  [DISCOVERED!] k={k}, m={m}, P={list(P)}")
        print(f"  Completed k={k}: checked {count_checked} combinations.")
    
    return found

if __name__ == "__main__":
    print("--- Exhaustive Small Prime Subset Search for Primary Pseudoperfect Numbers ---")
    results = exhaustive_search(max_prime=300, max_k=5)
    print("\nSummary of all discovered primary pseudoperfect numbers:")
    for m in sorted(results.keys()):
        print(f"m = {m} (digits = {len(str(m))}) -> P = {list(results[m])}")
