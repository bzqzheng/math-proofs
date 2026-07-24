"""
Independent verification of the Alpoge / Claude Fable 5 counterexample
to the Jacobian conjecture (announced 2026-07-20).

Map F: C^3 -> C^3 (as posted publicly):

  F1 = (1 + x*y)^3 * z + y^2 * (1 + x*y) * (4 + 3*x*y)
  F2 = y + 3*x*(1 + x*y)^2 * z + 3*x*y^2 * (4 + 3*x*y)
  F3 = 2*x - 3*x^2*y - x^3*z

Claims to check:
  1. det(JF) is the constant -2 everywhere.
  2. F maps three distinct points to the same image:
       p1 = (0, 0, -1/4)
       p2 = (1, -3/2, 13/2)
       p3 = (-1, 3/2, 13/2)
     all to q = (-1/4, 0, 0).

If both hold, F has everywhere-nonzero constant Jacobian determinant
yet is not injective, falsifying Keller's 1939 Jacobian conjecture in
dimension 3 (and trivially in all n >= 3).
"""

from sympy import Matrix, Rational, simplify, symbols

x, y, z = symbols("x y z")

F1 = (1 + x * y) ** 3 * z + y**2 * (1 + x * y) * (4 + 3 * x * y)
F2 = y + 3 * x * (1 + x * y) ** 2 * z + 3 * x * y**2 * (4 + 3 * x * y)
F3 = 2 * x - 3 * x**2 * y - x**3 * z

F = Matrix([F1, F2, F3])
vars_ = [x, y, z]

# Claim 1: Jacobian determinant is identically -2
J = F.jacobian(vars_)
det = simplify(J.det())
print("det(JF) =", det)
assert det == -2, "Jacobian determinant is not identically -2!"

# Claim 2: three distinct points collide at one image
p1 = (Rational(0), Rational(0), Rational(-1, 4))
p2 = (Rational(1), Rational(-3, 2), Rational(13, 2))
p3 = (Rational(-1), Rational(3, 2), Rational(13, 2))

images = []
for i, p in enumerate([p1, p2, p3], start=1):
    img = tuple(simplify(f.subs(dict(zip(vars_, p)))) for f in F)
    images.append(img)
    print(f"F(p{i}) = {img}")

assert len(set([p1, p2, p3])) == 3, "points are not distinct"
assert len(set(images)) == 1, "images do not coincide!"
print("Common image q =", images[0], "(claimed (-1/4, 0, 0))")

print("\nBoth claims verified: constant Jacobian -2, non-injective (3-to-1 at q).")
print("The Jacobian conjecture is FALSE in dimension 3.")
