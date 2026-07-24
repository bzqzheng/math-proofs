from fractions import Fraction
import sympy

def check_561():
    P = [2, 3, 11, 17]
    s = sum(Fraction(1, p) for p in P)
    res = 1 - s
    print(f"P = {P}")
    print(f"Sum = {s}")
    print(f"Residual = {res}")
    print(f"Is numerator 1? {res.numerator == 1}")
    print(f"Denominator m = {res.denominator}")
    
    # Check Lean definition
    m = res.denominator
    print(f"Lean erdos313Solutions check: m >= 2 and all p in P prime: {m >= 2 and all(sympy.isprime(p) for p in P)}")

if __name__ == "__main__":
    check_561()
