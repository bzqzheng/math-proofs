import math
import sympy

def compute_bateman_horn_heuristic():
    print("--- TRACK 3: BATEMAN-HORN DENSITY HEURISTICS & TREE EXPANSION ---")
    
    known_m = [2, 6, 42, 1806, 47058, 2214502422, 52495396602]
    
    print("\nHeuristic prime-pair expectation for m^2 + 1:")
    for m in known_m:
        val = m * m + 1
        divs = sympy.divisors(val)
        pair_prob_sum = 0.0
        valid_pairs = 0
        for d in divs:
            p1 = m + d
            p2 = m + (val // d)
            if p1 < p2:
                # Heuristic probability that p1 and p2 are both prime:
                # P(p1 prime, p2 prime) ~ C / (log p1 * log p2)
                prob = 1.0 / (math.log(p1) * math.log(p2))
                pair_prob_sum += prob
                if sympy.isprime(p1) and sympy.isprime(p2):
                    valid_pairs += 1
        print(f"  m = {m} (val digits = {len(str(val))}):")
        print(f"    Total divisor pairs = {len(divs)//2}")
        print(f"    Heuristic expected prime pairs = {pair_prob_sum:.4f}")
        print(f"    Actual prime pairs found = {valid_pairs}")

if __name__ == "__main__":
    compute_bateman_horn_heuristic()
