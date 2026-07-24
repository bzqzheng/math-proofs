from fractions import Fraction
import sympy

def explore_sat_ilp():
    print("--- APPROACH 10: SAT / CONSTRAINT SATISFACTION FORMULATION ---")
    print("Formulating Primary Pseudoperfect Condition as Diophantine Equality:")
    print("  prod_{i=1}^k p_i - sum_{j=1}^k (prod_{i != j} p_i) = 1")
    print("  Let P_k = prod_{i=1}^k p_i,  S_k = sum_{j=1}^k (P_k / p_j)")
    print("  Target: P_k - S_k = 1\n")

    print("Checking P_k - S_k = 1 for ground truth terms:")
    known_P = [
        [2],
        [2, 3],
        [2, 3, 7],
        [2, 3, 7, 43],
        [2, 3, 11, 23, 31],
        [2, 3, 11, 23, 31, 47059],
        [2, 3, 11, 17, 101, 149, 3109],
        [2, 3, 11, 23, 31, 47059, 2217342227, 1729101023519]
    ]
    
    for P in known_P:
        prod_P = 1
        for p in P:
            prod_P *= p
        sum_P = sum(prod_P // p for p in P)
        diff = prod_P - sum_P
        print(f"P = {P}:")
        print(f"  prod_P = {prod_P}")
        print(f"  sum_P  = {sum_P}")
        print(f"  diff (prod - sum) = {diff} -> Equal 1? {diff == 1}")

if __name__ == "__main__":
    explore_sat_ilp()
