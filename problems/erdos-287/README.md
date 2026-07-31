# Erdős #287 — gaps in Egyptian-fraction representations of 1

**Status:** ACTIVE — MITM hunt at k=22+ (2026-07-30)
**Source:** [erdosproblems.com #287](https://www.erdosproblems.com/287) (FALSIFIABLE)

## Statement (canonical, corrected 2026-07-30)
Let k ≥ 2. Is it true that for any 1 < n_1 < ... < n_k with
1 = Σ 1/n_i we must have **max(n_{i+1} − n_i) ≥ 3**?

- A **counterexample** is a representation with all gaps ≤ 2 (any k).
- Known: max gap ≥ 2 always (Erdős 1932 — 1 is not a sum of reciprocals of
  consecutive integers); 1/2+1/3+1/6 shows 3 is best possible.
- Would follow (all but finitely many exceptions) from a Sophie-Germain-type
  hypothesis: for all large N, a prime p ∈ [N, 2N] with (p+1)/2 also prime.

(The earlier README had the direction garbled; the scan script's
"COUNTEREXAMPLE" label was correct: a find = a gaps-≤2 representation.)

## Method
Meet-in-the-middle (`mitm_287.py`): enumerate first halves into a
3-prime modular-residue hash, join second halves on target residues +
boundary gap, verify exactly with `Fraction`. Correct can't-reach pruning
(the old DFS pruned in the wrong direction) + early-exit per k.

Gates (both pass): (a) GAP=3 k=3 finds (2,3,6) exactly;
(b) GAP=2 k ≤ 21 yields zero solutions in 0.1 s — the old buggy DFS needed
hours to reach k=21.

## Results
- No counterexample for k ≤ 21 (old DFS + MITM gate (b)).
- **No counterexample for k ≤ 39 (exhaustive MITM, ≤ 33 s per k, 2026-07-30).**
- k = 40..45 exhaustive: running (~1–20 min each expected). k ≥ 46 likely
  needs a C port — the Python hash table grows ~2× per k.

## Run
```
python problems/erdos-287/mitm_287.py gate
python problems/erdos-287/mitm_287.py --exhaustive 22 40
```
