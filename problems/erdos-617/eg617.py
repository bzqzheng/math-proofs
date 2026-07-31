#!/usr/bin/env python3
"""Erdos-Gyarfas #617 — balanced r-colorings of E(K_{r^2+1}).

Conjecture (Erdos-Gyarfas 1999): for r >= 3, every r-coloring of the edges of
K_{r^2+1} has r+1 vertices whose induced edges use AT MOST r-1 colors (i.e.
miss a color). A **balanced** coloring — every (r+1)-subset of vertices sees
ALL r colors on its edges — is therefore a counterexample. Proved for r=3
(K_10) and r=4 (K_17) by Erdos-Gyarfas; r=5 (K_26) is the first open case.

Finite objects, both mechanically checkable:
  SAT   -> a balanced r-coloring (disproves the conjecture at r)
  UNSAT -> no balanced coloring exists (proves the conjecture at r)

Every solver-produced coloring is re-verified by the independent checker
before being reported — a solution without a passing checker is a hypothesis.

Usage:
  eg617.py gate           known-positive / known-negative gates
  eg617.py solve r [n]    one instance (default n = r^2+1)
"""
import itertools
import os
import sys
import time

from pysat.solvers import Cadical153

HERE = os.path.dirname(os.path.abspath(__file__))


def encode(r, n):
    """CNF for 'balanced r-coloring of E(K_n) exists'.

    Var x_{e,c}: edge e has color c. Exactly one color per edge; for every
    (r+1)-subset S and every color c, some edge inside S has color c.
    Returns (nvars, clauses, edges).
    """
    edges = list(itertools.combinations(range(n), 2))
    eidx = {e: i for i, e in enumerate(edges)}
    var = lambda ei, c: ei * r + c + 1
    clauses = []
    for ei in range(len(edges)):
        clauses.append([var(ei, c) for c in range(r)])
        for c1 in range(r):
            for c2 in range(c1 + 1, r):
                clauses.append([-var(ei, c1), -var(ei, c2)])
    for S in itertools.combinations(range(n), r + 1):
        eis = [eidx[e] for e in itertools.combinations(S, 2)]
        for c in range(r):
            clauses.append([var(ei, c) for ei in eis])
    return len(edges) * r, clauses, edges


def check_balanced(color_of, edges, r, n):
    """Independent checker. Returns (balanced, witness_subset_or_None)."""
    for S in itertools.combinations(range(n), r + 1):
        if len({color_of[e] for e in itertools.combinations(S, 2)}) < r:
            return False, S
    return True, None


def solve(r, n):
    """Returns (sat, coloring-or-None, seconds). Coloring: dict edge->color."""
    nvars, clauses, edges = encode(r, n)
    t0 = time.time()
    with Cadical153(bootstrap_with=clauses) as s:
        sat = s.solve()
        dt = time.time() - t0
        if not sat:
            return False, None, dt
        model = set(s.get_model())
        color_of = {}
        for ei, e in enumerate(edges):
            color_of[e] = next(c for c in range(r) if ei * r + c + 1 in model)
    balanced, witness = check_balanced(color_of, edges, r, n)
    assert balanced, f"CHECKER REJECTED solver output: subset {witness} misses a color"
    return True, color_of, dt


def expect(r, n, want_sat, label=""):
    sat, color_of, dt = solve(r, n)
    status = "SAT" if sat else "UNSAT"
    ok = sat == want_sat
    print(f"  [{'OK' if ok else 'FAIL'}] r={r} n={n}: {status} "
          f"(expected {'SAT' if want_sat else 'UNSAT'}) {dt:.2f}s {label}", flush=True)
    return ok


def gate():
    print("gate (a) must-find known-balanced colorings:", flush=True)
    ok = True
    # r=2, K_5: the 5-cycle + complement construction is balanced (conjecture
    # is stated for r >= 3 precisely because r=2 fails).
    ok &= expect(2, 5, True, "(C5 construction)")
    # Trivial smalls: n = r+1, one subset, just use all r colors.
    ok &= expect(3, 4, True)
    ok &= expect(5, 6, True)
    print("gate (b) must-prove known theorems (Erdos-Gyarfas 1999):", flush=True)
    ok &= expect(3, 10, False, "(r=3 proved)")
    ok &= expect(4, 17, False, "(r=4 proved)")
    print("gate:", "PASS" if ok else "FAIL", flush=True)
    return ok


def main():
    args = sys.argv[1:]
    if not args or args[0] == "gate":
        sys.exit(0 if gate() else 1)
    if args[0] == "solve":
        r = int(args[1])
        n = int(args[2]) if len(args) > 2 else r * r + 1
        sat, color_of, dt = solve(r, n)
        if sat:
            os.makedirs(os.path.join(HERE, "colorings"), exist_ok=True)
            path = os.path.join(HERE, "colorings", f"eg_r{r}_n{n}.txt")
            with open(path, "w") as f:
                f.write(f"# BALANCED {r}-coloring of K_{n} — counterexample to Erdos-Gyarfas #617\n")
                for (u, v), c in sorted(color_of.items()):
                    f.write(f"{u} {v} {c}\n")
            print(f"SAT: balanced {r}-coloring of K_{n} FOUND ({dt:.1f}s) -> {path}")
            print("*** This DISPROVES Erdos-Gyarfas #617 at r=%d. Verify independently." % r)
        else:
            print(f"UNSAT: no balanced {r}-coloring of K_{n} ({dt:.1f}s) — conjecture holds at r={r}")
        return
    print(__doc__)
    sys.exit(2)


if __name__ == "__main__":
    main()
