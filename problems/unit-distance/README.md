# Erdős unit-distance problem — classical baseline check

**Status:** BASELINE-CONFIRMED (the new construction itself is not offline-verifiable)
**Source:** unit-distance conjecture disproved 2026-05-20 (n^1.014 construction); see `docs/source-report-2026-07.md`

## What we verified
Direct enumeration on grids up to 150×150 (22,500 points, ~2.5·10⁸ pairs):
the most popular distance always occurs more than n times, with effective
exponent log u/log n ≈ 1.25 drifting down toward 1 — consistent with the
classical n^(1+c/log log n) law that the May-2026 construction beats
asymptotically (n^1.014 via class field towers).

The n^1.014 construction relies on Golod–Shafarevich / class-field-tower
machinery; there is no enumerable witness, so it cannot be verified offline.
That is exactly why it needed nine human mathematicians to extract and check,
while the Jacobian counterexample needed a tweet — not all LLM-solved
problems have equal verification asymmetry.

## Run
```
make verify-unit-distance
```
