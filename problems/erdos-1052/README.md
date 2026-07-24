# Attempt: Erdős #1052 — sixth unitary perfect number

## Status: CALIBRATED, DEPRIORITIZED (2026-07-24)

## Calibration (OEIS A002827)
- 5 known (6; 60; 90; 87360; 146361946186458562560000). Unknown if a 6th exists.
- Structural constraints: prime factors of unitary perfect numbers are Higgs
  primes (A057447). Frei: if 3 ∤ n, then n has ≥ 144 distinct odd prime
  factors and n > 10^440. Goto (2007): n with k distinct prime factors
  satisfies n < 2^(2^k) — finiteness per k.
- All unitary perfect numbers are even (Lean-formalized, 2026).

## Assessment
The search equation ∏(p^a + 1) = 2n is exact (δ = 0 window), unlike #470's
tunable δ — there is no "close miss" landscape to exploit, so our DFS
framework loses its main edge. The 6th number is expected to be enormous
(the 5th already has 12 prime factors and 24 digits); the factor-chain
search used historically is a multi-week compiled-compute project with a
low hit probability. Not the best spend while #470 has genuinely fresh
territory (above 10^21) with a validated pipeline.

Revisit if: #470 pipeline matures into a compiled engine — the same engine
adapts to the unitary equation with modest changes.
