# Jacobian conjecture, dimension 3 — counterexample verification

**Status:** VERIFIED
**Source:** Alpöge & Fable 5, posted 2026-07-20; see `docs/source-report-2026-07.md`

## Statement
The Jacobian conjecture (1939) claimed every polynomial map F: Cⁿ → Cⁿ with
det(JF) a nonzero constant is invertible. Disproved in dimension 3 by an
explicit counterexample. The witness is the proof: two properties, both pure
polynomial arithmetic.

## What we verified (offline, SymPy)
- `det(JF) ≡ −2` for the posted map F: C³ → C³ — a nonzero constant ✓
- `F(0,0,−1/4) = F(1,−3/2,13/2) = F(−1,3/2,13/2) = (−1/4,0,0)` — F is locally
  invertible everywhere yet 3-to-1 at one point ✓

## Run
```
make verify-jacobian
```

Full context and verdict table: `docs/verification-report.md`.
