# Erdős #993 — tree independence-polynomial unimodality

## Statement
Is the independent-set sequence (coefficients of the independence polynomial)
of every tree unimodal?  A counterexample is one tree whose coefficient
sequence has a local minimum:

    i_{k-1}(T) > i_k(T) < i_{k+1}(T)   for some k.

## Status
Open as of April 2026 ([Hibi–Kara–Vien 2026](https://arxiv.org/html/2604.18824v1)).
Known to be true for all trees on ≤ 29 vertices (Reynolds 2026, Zenodo v3;
exhaustive verification of all 8,691,747,673 trees).  The first
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
4. **Deterministic family scans**:
   - Kadrawi–Levit families `3,k,k+j` and `3*,k,k+j`: no counterexample up to
     k = 100, j = 30 (6,200 members, best near-miss ratio 0.990438).
   - Pure spiders S(a,b,c) (three path arms): no counterexample up to arm
     length 50; all strictly unimodal (best ratio 0.0).
   - Pure star-arms K_{1,m1}, K_{1,m2}, K_{1,m3}: no counterexample up to
     m_i = 120 (1,728,000 triples, best near-miss 0.994475).
5. **Caterpillar search** (path spine with leaf bunches):
   - Exhaustive: no counterexample for spine lengths L = 3..6 and leaf counts
     up to A = 12.
   - Simulated annealing on caterpillars reached **best near-miss ratio
     0.995652** at a = [100, 97, 90, 73, 98] (n = 463) without crossing 1.
   - Confirms BrettRey's n = 30 near-miss is a caterpillar with a = [9,0,8,0,8]
     and ratio 0.868148.

## Literature calibration (critical)
Brett Reynolds' preprint
*"Mean bounds, structural reductions, and exhaustive verification for tree
independence polynomial unimodality"* (Zenodo v3, March 2026)
reports:
- μ(T) < n/3 for every tree with at most one leaf (d_leaf ≤ 1).
- Structural reductions that constrain any counterexample.
- Exhaustive verification to n = 29.
- A generalization of the Kadrawi–Levit families to rooted "bush" trees,
  yielding 4,445 non-log-concade trees up to 60 vertices.
- Forest products built from the 80 most extreme bush trees (pairs, triples,
  powers up to 20, products with paths P1–P16; 253,695 forests total) are all
  unimodal.

This means the non-unimodal counterexample, if it exists, must lie outside
both the small-tree exhaustive range and the known non-log-concade/bush
families.  The marginal return of further local search on these families is
low.

## Verdict
**DEPRIORITIZED for this iteration.**  We have pushed the main known families
further than the published near-miss records, but no counterexample.  A
breakthrough would need either (a) a theoretical construction exploiting a
family not yet analyzed, or (b) a much larger computational search guided by
Reynolds' structural reductions.  Revisit if a new structural idea appears.

## Files
- `scan_993_trees.py` — brute-force enumerator (corrected DP; only
  useful to ~n = 20 because counts explode).
- `heuristic_993_trees_v2.py` — simulated-annealing search on general
  trees.
- `scan_993_families.py` — Kadrawi–Levit family scanner.
- `scan_993_spiders_fast.py` — pure spider / star-arm scanner.
- `scan_993_caterpillars.py` — caterpillar exhaustive + SA scanner.
- `best_roots_tree_n30.json` — imported n = 30 near-miss tree from
  BrettRey's repo.

## Compounding insight
For tree independence polynomials, the recursive DP is extremely sensitive to
 coefficient-list alignment: every `zip` must be `zip_longest(fillvalue=0)`;
otherwise merging child polynomials silently truncates and the sequence
collapses.  This is a generic hazard when DP states are variable-length
vectors — **always merge with the longer length, never trust Python's default
zip truncation**.
