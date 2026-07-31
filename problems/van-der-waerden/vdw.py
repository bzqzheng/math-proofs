#!/usr/bin/env python3
"""Van der Waerden certificates — SAT encoding + independent checker.

Encodes "there exists an r-coloring of [n] with no monochromatic k-term
arithmetic progression" as CNF and solves it. A found coloring is a lower-bound
certificate (W(r,k) > n); UNSAT is an upper bound (W(r,k) <= n). Every coloring
the solver returns is re-verified by the independent checker before being
reported — a solution without a passing checker is a hypothesis.

Usage:
  vdw.py gate                 known-positive/known-negative gates (fast)
  vdw.py solve r k n          one instance; prints SAT (+ certificate) / UNSAT
  vdw.py find r k n0 n1       hunt certificates for n in [n0, n1]

Certificate files: colorings/vdw_r{k}_c{r}_n{n}.txt  (one color per integer).
"""
import os
import sys
import time

from pysat.solvers import Cadical153

HERE = os.path.dirname(os.path.abspath(__file__))


def aps(n, k):
    """All k-term arithmetic progressions in [1, n]."""
    for d in range(1, (n - 1) // (k - 1) + 1):
        for a in range(1, n - (k - 1) * d + 1):
            yield tuple(a + i * d for i in range(k))


def encode(r, k, n):
    """CNF for 'r-coloring of [n] avoids mono k-AP'. Returns (nvars, clauses)."""
    clauses = []
    if r == 2:
        nvars = n
        var = lambda i, c=0: i
    else:
        nvars = n * r
        var = lambda i, c: (i - 1) * r + c + 1
        for i in range(1, n + 1):
            clauses.append([var(i, c) for c in range(r)])          # >= 1 color
            for c1 in range(r):
                for c2 in range(c1 + 1, r):
                    clauses.append([-var(i, c1), -var(i, c2)])     # <= 1 color
    for ap in aps(n, k):
        if r == 2:
            clauses.append(list(ap))        # not all color 0
            clauses.append([-v for v in ap])  # not all color 1
        else:
            for c in range(r):
                clauses.append([-var(i, c) for i in ap])
    return nvars, clauses


def check_coloring(color, n, k):
    """Independent checker. Returns the offending mono AP, or None if clean."""
    for ap in aps(n, k):
        if len({color[i] for i in ap}) == 1:
            return ap
    return None


def solve(r, k, n):
    """Returns (sat, coloring-or-None, seconds)."""
    nvars, clauses = encode(r, k, n)
    t0 = time.time()
    with Cadical153(bootstrap_with=clauses) as s:
        sat = s.solve()
        dt = time.time() - t0
        if not sat:
            return False, None, dt
        model = set(s.get_model())
        color = {}
        for i in range(1, n + 1):
            if r == 2:
                color[i] = 1 if i in model else 0
            else:
                color[i] = next(c for c in range(r) if (i - 1) * r + c + 1 in model)
    bad = check_coloring(color, n, k)
    assert bad is None, f"CHECKER REJECTED solver output: mono AP at {bad}"
    return True, color, dt


def write_certificate(r, k, n, color):
    os.makedirs(os.path.join(HERE, "colorings"), exist_ok=True)
    path = os.path.join(HERE, "colorings", f"vdw_r{k}_c{r}_n{n}.txt")
    with open(path, "w") as f:
        f.write(f"# van der Waerden certificate: {r}-coloring of [{n}], no mono {k}-AP\n")
        f.write(f"# W({r},{k}) > {n}\n")
        for i in range(1, n + 1):
            f.write(f"{color[i]}\n")
    return path


def expect(r, k, n, want_sat, label=""):
    sat, color, dt = solve(r, k, n)
    status = "SAT" if sat else "UNSAT"
    ok = sat == want_sat
    print(f"  [{'OK' if ok else 'FAIL'}] W({r},{k}) n={n}: {status} "
          f"(expected {'SAT' if want_sat else 'UNSAT'}) {dt:.2f}s {label}", flush=True)
    if sat:
        write_certificate(r, k, n, color)
    return ok


def gate():
    print("gate (a) exact values, both sides of the frontier:", flush=True)
    ok = True
    # W(2,3)=9, W(2,4)=35, W(3,3)=27, W(2,5)=178 — SAT just below, UNSAT at.
    ok &= expect(2, 3, 8, True)
    ok &= expect(2, 3, 9, False)
    ok &= expect(2, 4, 34, True)
    ok &= expect(2, 4, 35, False)
    ok &= expect(3, 3, 26, True)
    ok &= expect(3, 3, 27, False)
    ok &= expect(2, 5, 177, True)
    ok &= expect(2, 5, 178, False)
    print("gate (b) must-find known-good certificate (CDCL-feasible size):", flush=True)
    # NOTE: the record reproduction W(5,3)>170 (Heule 2017) is a must-find gate
    # for the LOCAL-SEARCH engine (probsat.c, planned). Measured CDCL frontier
    # for r=5 k=3 on Cadical153: n=120 does not return within minutes; n=100
    # sits well inside the feasible region. This calibrates probsat.c's job.
    ok &= expect(5, 3, 100, True)
    print("gate:", "PASS" if ok else "FAIL", flush=True)
    return ok


def main():
    args = sys.argv[1:]
    if not args or args[0] == "gate":
        sys.exit(0 if gate() else 1)
    if args[0] == "solve":
        r, k, n = map(int, args[1:4])
        sat, color, dt = solve(r, k, n)
        if sat:
            path = write_certificate(r, k, n, color)
            print(f"SAT W({r},{k}) > {n} ({dt:.1f}s) -> {path}")
        else:
            print(f"UNSAT W({r},{k}) <= {n} ({dt:.1f}s)")
        return
    if args[0] == "find":
        r, k, n0, n1 = map(int, args[1:5])
        for n in range(n0, n1 + 1):
            sat, color, dt = solve(r, k, n)
            tag = f"SAT ({dt:.1f}s)" if sat else f"UNSAT ({dt:.1f}s) — STOP"
            print(f"n={n}: {tag}", flush=True)
            if not sat:
                break
            write_certificate(r, k, n, color)
        return
    print(__doc__)
    sys.exit(2)


if __name__ == "__main__":
    main()
