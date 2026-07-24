# Attempts: #699 (binomial gcd) and #458 (lcm inequality)

## Status: SCANS RUNNING / QUEUED, 2026-07-24

## #699 — the reduction (verified against brute force, 0 mismatches, n<120)
Conjecture: for 1 ≤ i < j ≤ n/2, gcd(C(n,i), C(n,j)) has a prime factor ≥ i.
Via Legendre digit sums: for prime p ≥ i, p | C(n,i) ⟺ n mod p < i (then
p | C(n,j) automatically). The variable j DROPS OUT — the conjecture is a
property of pairs (n, i), i < n/2:
    (*) ∃ prime p ≥ i with n mod p < i.
Speedups: prime i is auto-covered (p = i works); only composite i checked.
Primes p ∈ (n/2, n) cover all i > n − pmax (pmax = largest prime < n), so
only i ≤ (prime gap below n) need real checks. Counterexample = one pair
(n, i) failing (*), machine-checkable in ms by Kummer's theorem.

- Smoke: n ≤ 200k, ~900k composite-i pairs, 0 counterexamples (2s).
- Full run (background): n ≤ 10^8.
- Value either way: a counterexample is a famous witness; a clean 10^8 run
  is a strong verification extension plus the coverage structure (gap-below-n
  characterization) is independently interesting.

## #458 — ψ-difference over prime gaps
Conjecture: lcm(1..p_{k+1}−1) < p_k·lcm(1..p_k). Between consecutive primes
only prime POWERS q^e (e≥2) contribute to ψ, so the margin at k is
log p_k − Σ log q over prime powers in the gap. Danger zone is small k.
- Smoke: k ≤ 100k, 0 counterexamples; global min margin 0.154 at k=4
  (p=7, gap 4, prime power 9=3² in gap). Margins grow thereafter.
- Full run: k ≤ 10^7 (queued — launched after a task slot frees).

## Corpus triage notes (other Tier-2 falsifiables, from Lean statements)
- #398 Brocard n!+1=m²: externally verified ~10^15; below frontier, skip.
- #672 AP product = perfect power: 4-D unbounded space; only small cases
  solved (Euler, Obláth); low yield for blind search. Skip this iteration.
- #287 Egyptian-fraction max gap ≥ 3: no structure to prune by; conjecture
  tied to an open prime conjecture. Skip.
- #835 Johnson graph χ(J(2k,k)) = k+1?: smallest open k=10 → SAT on 184,756
  vertices, infeasible. Skip.
- #7 odd-modulus covering system: existence doubted; search unstructured.
  Possible SAT/CP formulation later.
- #242 Erdős–Straus: verified ~10^17 externally. Skip.

## #699 theory angle (2026-07-24): sieve framing of the failure set
After the reduction, a counterexample (n, i) requires: for EVERY prime
p ∈ [i, n], n mod p ∉ [0, i). I.e. n survives sifting by the residue
"window" [0, i) across all medium/large primes. This is an upper-bound
sieve problem (Brun/Selberg territory): the sifted set's expected density
is ∏_{p ∈ [i, n]} (1 − i/p), which decays extremely fast for i in the
composite range — heuristically explaining why no counterexamples appear
and suggesting a route: split i into regimes (i near n/2 handled by the
gap-below-n argument; medium i by Rosser-Iwaniec-type bounds; tiny i
directly). Also related to Jacobsthal's function g(m): n mod p ≥ i for
all p | m-ish means a run of i consecutive integers each divisible by some
prime of the system — Jacobsthal bounds give g(m) ≪ log²m for m = primorial,
which is far from excluding i ~ log n windows... the honest statement is
that a proof is within sight of modern sieve methods but nontrivial.
No proof attempted yet; scan data first.

## Production-scale integrity check (2026-07-24): PASSED
covered() vs an independent Kummer digit-sum implementation of
"∃ prime p ≥ i with v_p(C(n,i)) > 0": 3000 random (n, i) pairs at
10^5..10^8, zero mismatches. (The earlier n≤119 check verified the full
reduction including j; this verifies the production predicate itself.)

## #699 result (2026-07-24): clean to 10^8
870,779,549 composite-i pairs checked (all n ≤ 10^8), ZERO counterexamples
to the binomial-gcd conjecture. 34 min wall. Extension to 10^9 launched
(~5.5h estimated). Note: we have not yet cross-checked the external
frontier for this conjecture — do that before claiming any novelty.
