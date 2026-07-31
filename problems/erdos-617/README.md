# erdos-617 — Erdős–Gyárfás balanced colorings

**Status:** ATTACK-READY (encoder + checker validated; r=4 proof re-run in flight)
**Source:** erdosproblems.com #617 (FALSIFIABLE); Erdős–Gyárfás 1999
**Signature fit:** P1 (balanced coloring checks in ms), P2 (short object), P5 (SAT/local-search loop).

## Statement
For r ≥ 3: every r-coloring of the edges of K_{r²+1} has r+1 vertices whose
induced edges use at most r−1 colors (i.e. miss a color). A **balanced**
coloring — every (r+1)-subset sees ALL r colors — is a counterexample.
Proved for r=3 (K_10) and r=4 (K_17) by Erdős–Gyárfás; **r=5 (K_26) is the
first open case** — no advance since 1999. For r=5, r+1=6 is not a prime
power, so no known construction exists at any n; both directions are open.

## Finite objects (both publishable, both mechanically checkable)
- SAT: a balanced 5-coloring of K_26 → **disproves** the conjecture at r=5.
- UNSAT: no balanced 5-coloring of K_26 → **proves** it at r=5 (first advance
  since 1999). Instance: 1,625 vars, ~1.15M clauses of length 15.
- Checker: `eg617.py check_balanced` scans all C(n, r+1) subsets.

## Calibration (2026-07-31, web frontier audit)
- r=3, r=4 proved (Erdős–Gyárfás 1999, "A variant of the Erdős–Gyárfás problem").
- Balanced r-colorings of K_{r²+r+1} exist when r+1 is a prime power (Gyárfás
  survey) — the conjecture's n = r²+1 sits exactly below the construction.
- No published computational/SAT attack on r=5 found (UNVERIFIED — absence of
  evidence, worth a literature gate before any publication claim).

## Oracle
- Encoder: `eg617.py` — vars x_{e,c} (edge,color); exactly-one per edge; for
  each (r+1)-subset S and color c, clause "some edge of S has color c".
- Independent checker on every solver output (checker discipline).
- Gates:
  - (a) must-find: r=2 K_5 (C5 construction — conjecture is r≥3 precisely
    because r=2 fails), r=3 K_4, r=5 K_6 trivial balanced colorings. **3/3 pass.**
  - (b) must-prove: r=3 K_10 UNSAT (known theorem) — **pass, 546 s** (Cadical153).
    r=4 K_17 UNSAT — launched 2026-07-31 as a long background run (hours+).

## Approach
1. Encoder/checker + gates. DONE.
2. Finding lane: `../van-der-waerden/probsat.c` (generic probSAT, DIMACS in)
   hunting a balanced 5-coloring of K_26 — any hit disproves the conjecture.
   Add a `dimacs` command to eg617.py, then many seeds at -P.
3. Proof lane: CDCL on r=5 K_26 with S₂₅ star symmetry break (fix vertex 0's
   star colors non-decreasing); honestly priced days–weeks, possibly out of
   reach. A near-miss profile (max satisfiable fraction of (6-set, color)
   pairs) is itself a reportable artifact if UNSAT proves out of reach.
4. Optional due-diligence lane: cyclic colorings (13 difference classes, 5¹³
   with propagation pruning) — synergy with ramsey-r55 circulant machinery.

## Results
- Gates (a) 3/3, (b) r=3 pass (546 s). r=4 K_17 re-proof in flight.

## Verdict
Encoder banked. Next: dimacs writer + probSAT seeds on r=5 K_26 (finding
lane); CDCL proof attempt only after the finding lane maps the instance.
