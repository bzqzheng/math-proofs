#!/usr/bin/env python3
"""Verify hit candidates dumped by the C MITM engine (mitm_287.c), Erdős #287.

The C engine joins on a 64-bit digest of the 3-prime residue triple, so its
candidate set is a SUPERSET of the Python engine's exact-residue join:
digest collisions can only add spurious candidates (rejected here — the SAFE
failure mode), while no true residue match is ever missed (a missed hit would
be a missed counterexample — the unsafe mode, excluded by construction).

Per candidate line (k integers n_1..n_k) this checks, independently:
  - exactly k terms, n_1 > 1, strictly increasing, all gaps <= GAP;
  - exact sum 1 via Fraction — the same check as mitm_287.py:116.

usage: verify_hits.py K HITS_FILE [--gap G] [--expect a,b,c] [--expect-none]
exit code 0 on success (incl. expectations), 1 on failed expectation, 2 on error.
"""
import sys
from fractions import Fraction


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    k = int(sys.argv[1])
    path = sys.argv[2]
    gap, expect, expect_none = 2, None, False
    args = sys.argv[3:]
    if "--gap" in args:
        gap = int(args[args.index("--gap") + 1])
    if "--expect" in args:
        expect = tuple(int(x) for x in args[args.index("--expect") + 1].split(","))
    if "--expect-none" in args:
        expect_none = True
    try:
        with open(path) as f:
            lines = [ln.split() for ln in f if ln.strip()]
    except FileNotFoundError:
        print(f"verify k={k}: ERROR hits file not found: {path}")
        return 2

    verified, rejected = [], 0
    for toks in lines:
        try:
            t = tuple(int(x) for x in toks)
        except ValueError:
            rejected += 1
            continue
        ok = (len(t) == k and t[0] > 1
              and all(t[i + 1] > t[i] for i in range(len(t) - 1))
              and all(t[i + 1] - t[i] <= gap for i in range(len(t) - 1))
              and sum((Fraction(1, x) for x in t), Fraction(0)) == 1)
        if ok:
            verified.append(t)
        else:
            rejected += 1

    print(f"verify k={k}: {len(verified)} verified, {rejected} rejected "
          f"(of {len(lines)} candidates, gap<={gap})")
    for t in verified:
        print(f"  VERIFIED SOLUTION k={k}: {t} "
          f"gaps={[t[i + 1] - t[i] for i in range(len(t) - 1)]}")

    rc = 0
    if expect is not None:
        if expect in verified:
            print(f"  expected solution {expect} present: OK")
        else:
            print(f"  FAIL: expected solution {expect} NOT found")
            rc = 1
    if expect_none and verified:
        print(f"  FAIL: expected zero solutions, got {len(verified)}")
        rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
