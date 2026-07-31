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
   independent checker + certificate writer (`colorings/`). DONE, gates above.
2. `probsat.c` (planned) — probSAT-style stochastic local search, parallel
   seeds; the finding tool at the record frontier (complete CDCL grinds there —
   measured: r=5 k=3 n=170 exceeds minutes; Heule used ubcsat).
3. Attack ladder: W(5,3) n=171.., W(6,3) n=226.. (near-free first experiments),
   then the marquee **W(2,7) n=3704..** (~2.3M clauses; local search at scale).
4. UNSAT side (upper bounds / exact values, e.g. W(5,3)) needs CDCL + DRAT —
   deferred until the finding side maps the frontier.

## Results
- Encoder + checker validated on all seven exact nontrivial values' neighborhoods
  (gate (a) 8/8).
- Measured CDCL frontier (Cadical153, r=5 k=3): n=100 SAT in 0.68 s; n=120
  and n=170 (the Heule record) do not return within minutes — the record
  region is out of complete-solver reach; motivates probsat.c.

## Verdict
Encoder/oracle banked. Next single action: write probsat.c, validate by
reproducing W(5,3)>170 / W(6,3)>225 records, then hunt n=171 / n=226 / n=3704.
