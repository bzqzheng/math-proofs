# Attempt: Erdős #647 — n > 24 with max_{m<n}(m+τ(m)) ≤ n+2

## Status: DEPRIORITIZED (compute play only), 2026-07-24

## Calibration (OEIS fetch, A087280)
- The property defines OEIS A087280. Only 5 terms known (8 and 24 among them;
  the Lean file proves n=24).
- **Patrik Idén (June 2026, Zenodo preprint) verified NO further terms ≤ 10^12**,
  with gap-growth structural analysis and depth-record extension.
  => Brute-force scanning is dead below 10^12. Reproducing it is worthless;
  beating it is a C/segmented-sieve engineering project (~days of CPU for
  10^13–10^14), not an LLM-reasoning play.

## Structural analysis (ours)
Condition max_{m<n}(m+τ(m)) ≤ n+2 ⟺ for all k ≥ 1: τ(n−k) ≤ k+2.
Binding constraints are small k (for k ≫ τ max ~ 2√n it's automatic):
  k=1: τ(n−1) ≤ 3  → n−1 prime or square of prime
  k=2: τ(n−2) ≤ 4  → prime, semiprime, or p³
  k=3: τ(n−3) ≤ 5  → ...
So surviving n must be preceded by a long run of low-divisor-count integers —
a *backwards sieve condition*, structurally the same species as Jacobsthal's
function / prime constellations. Heuristically each extra constraint multiplies
the survival probability by a factor < 1, which is why Erdős found infinitely
many "extremely doubtful" while offering £25 for one more example.

## Verdict
Not this iteration's best spend. Revisit only with (a) a compiled segmented
scanner to push past 10^12, or (b) a theoretical angle on the backwards-sieve
density. Effort redirected to #470 (odd weird numbers), where the search
structure is far more LLM-navigable.
