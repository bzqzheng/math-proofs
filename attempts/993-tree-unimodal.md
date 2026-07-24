# Erdős #993 — tree independence-polynomial unimodality

## Statement
Is the independent-set sequence (coefficients of the independence polynomial)
of every tree unimodal?  A counterexample is one tree whose coefficient
sequence has a local minimum:

    i_{k-1}(T) > i_k(T) < i_{k+1}(T)   for some k.

## Status
Open.  Known to be true for all trees on ≤ 25 vertices (Radcliffe); the first
non-log-concave trees appear at n = 26 (Kadrawi–Levit 2023), but they remain
unimodal.  A GitHub evolutionary-search project (BrettRey/erdos-problem-993)
reports near-miss fitness ≈ 0.866 on an n = 30 tree and no counterexample up
to n = 60.

## Our attack
1. **Reproduce the n = 26 seeds** from the published structural families:
   - T1: the `3,k,k` family with k = 4 (center + 3 arms: three K2's, four K2's,
     four K2's), n = 26.
   - T2: the `3*,k,k+1` family with k = 3 (center + P4 ∪ K2 ∪ K2 under one
     arm, three K2's, four K2's), n = 26.
2. **Fitness**: `max_k min(c[k-1], c[k+1]) / c[k]` over interior coefficients.
   A value > 1 is exactly a local-minimum counterexample.
3. **Search**: simulated annealing with small tree-preserving mutations
   (add/remove leaf, rewire leaf, subdivide edge, contract leaf edge).  Tree
   size is capped at ~120 vertices to keep the O(n^2) polynomial DP fast.
4. **First run**: T1 seed climbed from fitness 0.825 to 0.987 in ~20k steps
   before size-capping was added; no counterexample yet.

## Files
- `attempts/scan_993_trees.py` — brute-force enumerator (corrected DP; only
  useful to ~n = 20 because counts explode).
- `attempts/heuristic_993_trees_v2.py` — simulated-annealing search.
- `attempts/best_roots_tree_n30.json` — imported n = 30 near-miss tree from
  BrettRey's repo.

## Compounding insight
For tree independence polynomials, the recursive DP is extremely sensitive to
 coefficient-list alignment: every `zip` must be `zip_longest(fillvalue=0)`;
otherwise merging child polynomials silently truncates and the sequence
collapses.  This is a generic hazard when DP states are variable-length
vectors — **always merge with the longer length, never trust Python's default
zip truncation**.
