from fractions import Fraction
import math

def continued_fraction(num, den):
    cf = []
    while den != 0:
        q = num // den
        cf.append(q)
        num, den = den, num - q * den
    return cf

def explore_continued_fractions():
    print("--- APPROACH 11: CONTINUED FRACTION CONVERGENTS ---")
    
    known_P = [
        [2],
        [2, 3],
        [2, 3, 7],
        [2, 3, 7, 43],
        [2, 3, 11, 23, 31],
        [2, 3, 11, 23, 31, 47059],
        [2, 3, 11, 17, 101, 149, 3109]
    ]
    
    for P in known_P:
        s = sum(Fraction(1, p) for p in P)
        cf = continued_fraction(s.numerator, s.denominator)
        print(f"P = {P}: sum = {s} -> Continued Fraction: {cf}")

if __name__ == "__main__":
    explore_continued_fractions()
