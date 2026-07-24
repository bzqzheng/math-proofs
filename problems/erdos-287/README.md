# Erdős #287 — Egyptian fractions with gaps ≤ 2

**Status:** BLOCKED (needs a better algorithm)
**Source:** erdosproblems.com #287

## Statement
For every k, decide whether 1 = Σ 1/n_i with 1 < n_1 < ... < n_k and all
gaps n_{i+1} − n_i ≤ 2. A counterexample is a k for which no such
representation exists.

## Results
- No counterexample for k ≤ 21 (backtracking scan, `scan_287_gaps.py`)
- Search cost explodes at k = 22 — raw DFS is done; resume only with an
  ILP / meet-in-the-middle reformulation.

## Run
```
make scan-287
```
