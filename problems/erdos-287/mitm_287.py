#!/usr/bin/env python3
"""Erdős #287 — meet-in-the-middle counterexample hunt.

Conjecture (erdosproblems.com #287, FALSIFIABLE): every representation
    1 = sum_{i=1..k} 1/n_i   with 1 < n_1 < ... < n_k
has max(n_{i+1} - n_i) >= 3. A counterexample is a representation with all
gaps <= GAP (default 2). None exists for k <= 21 (DFS frontier); k=22 is open.

Method: for each k, enumerate first halves (j = k//2 terms) into a
modular-residue hash table (3 primes), enumerate second halves (k-j terms),
join on exact target residues + boundary gap, verify exactly with Fraction.
Early-exit on first solution per k; --exhaustive proves none exists for that
k (extends the verified frontier).

Oracle gates (run: `python mitm_287.py gate`):
  (a) known-positive: GAP=3, k=3 must find an exact solution (1/2+1/3+1/6
      has max gap 3).
  (b) known-negative: GAP=2, k<=21 must yield zero solutions.
"""
import sys
import time
from fractions import Fraction

P1 = (1 << 61) - 1
P2 = (1 << 31) - 1
P3 = 999999937
PRIMES = (P1, P2, P3)

_invcache = {}


def invs(n):
    v = _invcache.get(n)
    if v is None:
        v = (pow(n, P1 - 2, P1), pow(n, P2 - 2, P2), pow(n, P3 - 2, P3))
        _invcache[n] = v
    return v


def max_rem(l, r):
    """Largest possible sum of r further terms (all +1 steps)."""
    return sum(1.0 / (l + i) for i in range(1, r + 1))


EPS = 1e-9  # float slack for prune comparisons (exact filter is the modular
            # hash + Fraction verification; floats only guide pruning)


def search_k(k, gap=2, exhaustive=False):
    """Returns (solution_list, stats_dict)."""
    t0 = time.time()
    j = k // 2
    n_second = k - j
    table = {}

    # ---------- first half: j terms; at completion key must include last term ----------
    def rec1(pos, last, s, res, tup):
        rem = j - pos - 1
        lo = 2 if pos == 0 else last + 1
        hi = (k - 1) if pos == 0 else last + gap
        for nxt in range(lo, hi + 1):
            ns = s + 1.0 / nxt
            if ns >= 1.0:
                continue
            # can't-reach prune: even maximal completion can't reach 1
            if ns + max_rem(nxt, rem) + max_rem(nxt + rem, n_second) < 1.0 - EPS:
                continue
            nr1 = (res[0] + invs(nxt)[0]) % P1
            nr2 = (res[1] + invs(nxt)[1]) % P2
            nr3 = (res[2] + invs(nxt)[2]) % P3
            if rem == 0:
                table.setdefault((nr1, nr2, nr3), []).append((nxt, tup + (nxt,), ns))
            else:
                rec1(pos + 1, nxt, ns, (nr1, nr2, nr3), tup + (nxt,))

    rec1(0, 0, 0.0, (0, 0, 0), ())
    stats = {"k": k, "first_half": sum(len(v) for v in table.values()), "second_half": 0, "hits": 0}
    if not table:
        stats["sec"] = time.time() - t0
        return [], stats

    all_s1 = [v[2] for vs in table.values() for v in vs]
    min_s1, max_s1 = min(all_s1), max(all_s1)
    min_s2, max_s2 = 1.0 - max_s1, 1.0 - min_s1
    last_values = {v[0] for vs in table.values() for v in vs}
    m1_lo = max(3, min(last_values) + 1)
    m1_hi = max(last_values) + gap

    # ---------- second half ----------
    solutions = []

    def rec2(pos, last, s, res, tup):
        rem = n_second - pos - 1
        lo = m1_lo if pos == 0 else last + 1
        hi = m1_hi if pos == 0 else last + gap
        for nxt in range(lo, hi + 1):
            ns = s + 1.0 / nxt
            if ns >= max_s2 + EPS:
                continue  # overshoot: above window (1 - min_s1)
            if ns + max_rem(nxt, rem) < min_s2 - EPS:
                continue  # can't reach window (1 - max_s1)
            nr1 = (res[0] + invs(nxt)[0]) % P1
            nr2 = (res[1] + invs(nxt)[1]) % P2
            nr3 = (res[2] + invs(nxt)[2]) % P3
            if rem == 0:
                stats["second_half"] += 1
                tup2 = tup + (nxt,)
                tgt = ((1 - nr1) % P1, (1 - nr2) % P2, (1 - nr3) % P3)
                cand = table.get(tgt)
                if not cand:
                    continue
                for last_fj, tup_f, _s1f in cand:
                    if not (1 <= tup2[0] - last_fj <= gap):
                        continue
                    full = tup_f + tup2
                    if sum((Fraction(1, x) for x in full), Fraction(0)) == 1:
                        stats["hits"] += 1
                        solutions.append(full)
                        if not exhaustive:
                            return True
            else:
                if rec2(pos + 1, nxt, ns, (nr1, nr2, nr3), tup + (nxt,)):
                    return True
        return False

    rec2(0, 0, 0.0, (0, 0, 0), ())
    stats["sec"] = time.time() - t0
    return solutions, stats


def gate():
    sols, st = search_k(3, gap=3, exhaustive=False)
    assert sols, "gate (a) failed: no GAP=3 solution for k=3"
    sol = sols[0]
    assert sum((Fraction(1, x) for x in sol), Fraction(0)) == 1, sol
    print(f"gate (a) OK: GAP=3 k=3 -> {sol} (exact sum 1)")
    t0 = time.time()
    total = 0
    for k in range(2, 22):
        sols, st = search_k(k, gap=2, exhaustive=True)
        assert not sols, f"unexpected solution at k={k}: {sols}"
        total += st["first_half"] + st["second_half"]
    print(f"gate (b) OK: GAP=2 k<=21 zero solutions "
          f"(reproduces DFS frontier, {total} halves, {time.time()-t0:.1f}s)")


def main():
    exhaustive = "--exhaustive" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--exhaustive"]
    k_lo = int(args[0]) if len(args) > 0 else 22
    k_hi = int(args[1]) if len(args) > 1 else 40
    for k in range(k_lo, k_hi + 1):
        sols, st = search_k(k, gap=2, exhaustive=exhaustive)
        if sols:
            for sol in sols[:3]:
                print(f"*** COUNTEREXAMPLE k={k}: {sol} "
                      f"(gaps {[sol[i+1]-sol[i] for i in range(len(sol)-1)]})", flush=True)
            print(f"    -> disproves Erdős #287 ({len(sols)} found). "
                  f"Verify independently before publishing.", flush=True)
            return
        print(f"k={k}: none (halves={st['first_half']}+{st['second_half']}, "
              f"hits={st['hits']}, {st['sec']:.1f}s)", flush=True)
    print("done: no counterexample in range", flush=True)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "gate":
        gate()
    else:
        main()
