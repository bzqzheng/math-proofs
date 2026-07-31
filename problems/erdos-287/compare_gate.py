#!/usr/bin/env python3
"""Cross-check C vs Python MITM logs for Erdős #287 (gate equivalence, k=22..40).

Asserts per k:
  - identical first_half and second_half counts (proves bit-identical
    enumeration / float pruning),
  - python hits == C verified solutions (the gate-(b) hit-count equality).

usage: compare_gate.py PY_LOG C_LOG VERIFY_LOG [VERIFY_LOG...]
"""
import re
import sys

PY_NONE = re.compile(r"^k=(\d+): none \(halves=(\d+)\+(\d+), hits=(\d+),")
C_NONE = re.compile(r"^k=(\d+): none \(halves=(\d+)\+(\d+), cand=\d+,")
C_CAND = re.compile(r"^k=(\d+): \d+ candidates dumped -> \S+ \(halves=(\d+)\+(\d+),")
VER = re.compile(r"^verify k=(\d+): (\d+) verified,")


def main():
    py, cc, ver = {}, {}, {}
    for path in sys.argv[1:]:
        for line in open(path):
            m = PY_NONE.match(line)
            if m:
                py[int(m[1])] = (int(m[2]), int(m[3]), int(m[4]))
                continue
            m = C_NONE.match(line) or C_CAND.match(line)
            if m:
                cc[int(m[1])] = (int(m[2]), int(m[3]))
                continue
            m = VER.match(line)
            if m:
                ver[int(m[1])] = int(m[2])
    bad = 0
    for k in sorted(py):
        f1, s1, h = py[k]
        if k not in cc:
            print(f"k={k}: MISSING from C log")
            bad += 1
            continue
        f2, s2 = cc[k]
        v = ver.get(k)
        issues = []
        if (f1, s1) != (f2, s2):
            issues.append(f"HALVES DIVERGE py={f1}+{s1} c={f2}+{s2}")
        if v is None:
            issues.append("no verify line")
        elif v != h:
            issues.append(f"HITS DIVERGE py_hits={h} c_verified={v}")
        bad += bool(issues)
        tag = "OK" if not issues else "; ".join(issues)
        print(f"k={k}: halves py={f1}+{s1} c={f2}+{s2}, hits={h}, "
              f"c_verified={v}  {tag}")
    for k in sorted(cc):
        if k not in py:
            print(f"k={k}: MISSING from Python log")
            bad += 1
    if bad:
        print(f"EQUIVALENCE FAILED ({bad} problem k-values)")
        return 1
    print(f"EQUIVALENCE OK: {len(py)} k-values identical "
          f"(first_half, second_half, hits==verified)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
