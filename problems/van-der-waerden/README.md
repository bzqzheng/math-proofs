# van-der-waerden — coloring certificates for lower bounds

**Status:** ATTACK-READY (oracle validated; local-search engine pending)
**Source:** classical Ramsey theory; DB-adjacent cluster (#138 variants). Literature calibration 2026-07-31 (see below).
**Signature fit:** P1 (certificate checks in ms), P2 (short object: one coloring), P5 (SAT/local-search generate–verify loop).

## Statement
W(r,k) = least N such that every r-coloring of [N] contains a monochromatic
k-term arithmetic progression. A lower bound **W(r,k) > n** is certified by a
single finite object: an r-coloring of [n] with no mono k-AP — mechanically
checkable in milliseconds by scanning all k-APs (`check_coloring` in `vdw.py`).

## Calibration (2026-07-31, via web frontier audit)
- Exact nontrivial values: W(2,3)=9, W(2,4)=35, W(2,5)=178, W(2,6)=1132
  (Kouril–Paul 2008), W(3,3)=27, W(4,3)=76, W(3,4)=293 (Kouril 2012).
- Open records (lower bounds): **W(2,7)>3703**, W(2,8)>11495, W(2,9)>41265,
  W(3,5)>2173, W(3,6)>11191, W(4,4)>1048, **W(5,3)>170**, **W(6,3)>225**
  (Heule 2017, "Avoiding triples in arithmetic progression");
  W(5,4)>2254, W(5,5)>98741; large-r from Monroe (distributed Rabung method,
  JCMCC 128, 2026).
- The small-number frontier has been essentially static since 2017–19 — the
  field sleeps; solver hardware has not.

## Oracle
- Checker: `vdw.py check_coloring` — scans all k-APs in [n], ms per certificate.
- Gate (a) known-positive/negative: exact values both sides — W(2,3), W(2,4),
  W(3,3), W(2,5): SAT at n=W−1 (must-find), UNSAT at n=W (must-prove).
  **8/8 pass** (W(2,5)=178: 3.6 s SAT / 10.2 s UNSAT, Cadical153 via PySAT).
- Gate (b) must-find multi-color record-region certificate (r=5, k=3).

## Approach
1. `vdw.py` — CNF encoder (2-color: one var per integer; r-color: one-hot) +
   independent checker + certificate writer (`colorings/`) + `dimacs` writer.
   DONE, gates above.
2. `probsat.c` — generic probSAT on DIMACS (any SAT-encoded target).
   Tuned CB=3.0 (solves W(2,5)>177 in 0.89 s) but **fails on the record
   instances** (W(5,3)>170, W(6,3)>225, W(2,6)>1131: 1.5B flips × 3 seeds
   each, all UNKNOWN, 2026-07-31). Kept for moderate/CNF-native targets.
3. `vdwls.c` — NATIVE local search (recolor-one-integer move set; the
   published records' approach). Incremental mono-AP score; probSAT-weighted
   (member,color) choice on net = break−make; short tabu tenure; plateau
   perturbation. Debugged via an incremental-vs-rescan drift gate which
   exposed a CSR off-by-one (I12-style: the rescan caught what the
   incremental count missed). Build: `clang -O3 -o vdwls vdwls.c -lm`.
4. Attack ladder: reproduce records (W(5,3)>170, W(6,3)>225, W(2,6)>1131) as
   must-find gates, then hunt n=171 / n=226 / n=3704 (W(2,7) marquee).
5. UNSAT side (upper bounds / exact values) needs CDCL + DRAT — deferred.

## Results
- `vdw.py` CDCL gates 9/9 (exact values both sides; n=100 r=5 k=3 in 0.68 s).
- Measured CDCL frontier (Cadical153, r=5 k=3): n=120 and n=170 (the Heule
  record) do not return within minutes — the record region is out of
  complete-solver reach.
- `probsat.c` CB-swept (2.3/2.5/2.7/3.0/3.5 on n=177): CB=3.0 optimal
  (0.89 s). Record instances: all UNKNOWN at 1.5B flips × 3 seeds — plain
  CNF probSAT is the wrong tool at the records (documented negative).
- `vdwls.c` (native, NOISE=0, CBW=3.0): solves W(2,4)>34 (10k steps),
  **W(2,5)>177 (≤1M steps, 2/3 seeds)**. Parameter map measured (2026-07-31):
  2-color wants MAKEMODE=1 TABU=10; multi-color wants MAKEMODE=0 TABU=0
  (tabu *hurts* multi-color: 0/4 vs 2/3 seeds on W(5,3)>100). Record gate
  attempts: W(5,3)>170 best mono≈66, W(2,6)>1131 best mono≈2512 (vs ~3983
  random) — the published records sit beyond the engine's envelope; the
  record-holders used construction+SAT hybrids (Kouril–Paul, Heule), not
  blind SLS. SAPS clause-weighting implemented (WUP env) but not a clear win.

## Verdict
Encoder + native engine banked with a measured envelope: CDCL exact to
W(2,5)=178; vdwls solves ≤ n≈180 2-color and ≤ n≈100+ multi-color reliably.
Next: (a) production hunts n=171 (r=5), n=226 (r=6), n=3704 (r=2 k=7) as
background seed-filler (honest odds: engine is below record-envelope, but
each seed is an independent ticket and cores are otherwise idle);
(b) if records are the goal, the next engine needs structure (cyclic /
Rabung-method constructions) or a construction+SAT hybrid, not more SLS
tuning.
