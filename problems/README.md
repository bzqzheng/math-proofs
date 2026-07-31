# Problems dashboard

Single source of truth for campaign status. Pipeline and status definitions:
`docs/pipeline.md`. New problem: `make new ID=<name>`, then register it here.

## Verification of external claims (2026 headline results)

| Dir | Claim | Status | Key result |
|---|---|---|---|
| `jacobian-dim3/` | Jacobian conjecture false in dim 3 (Alpöge–Fable 5) | **VERIFIED** | `det(JF) ≡ −2`; 3-to-1 collision at `(−1/4,0,0)` confirmed exactly (SymPy) |
| `erdos-164/` | Primitive-set conjecture via von Mangoldt chains | **STATEMENT-CONFIRMED** | All 163,368 primitive subsets of `{2..26}` checked; max attained exactly at primes |
| `unit-distance/` | Classical `n^(1+c/log log n)` baseline | **BASELINE-CONFIRMED** | Grid enumeration to 150×150 matches classical law; n^1.014 construction not offline-verifiable |

## Erdős problems — attacked

| Dir | Problem | Status | Key result |
|---|---|---|---|
| `erdos-699/` | `gcd(C(n,i),C(n,j))` prime factor ≥ i | **BOUND-EXTENDED** | **0 counterexamples for all n ≤ 10⁹** (10.34B pairs, two segments); composite-i closed via Sylvester–Schur; proof angle closed (Price/GPT-5.6 partial resolution on file) |
| `erdos-470/` | Odd weird numbers | **BOUND-EXTENDED** | **Sweep complete as designed: 0 finds across ≥12T nodes / ≥350k candidates** — all barren/off-spine regions exhausted to 10²⁴; 5 abundancy-frontier spines documented to 671B–1.79T nodes (264,140 tests on the deepest). Full coverage map: `RESULTS.md` |
| `erdos-458/` | lcm inequality | **BOUND-EXTENDED** | 0 counterexamples for k ≤ 10⁷; min margin 0.15415 at k=4 |
| `erdos-779/` | Fortune's conjecture | **BOUND-EXTENDED** | No composite Fortunate number for n ≤ 780 |
| `erdos-313/` | Primary pseudoperfect numbers | **ANALYZED** | Frontier documented (10 PPNs known, Wang May 2026); ω=9 sweep 2,538/2,910 shards (resumable); C/GMP engine in dir |
| `erdos-993/` | Tree independence-polynomial unimodality | **DEPRIORITIZED** | No counterexample across 5 families; best near-miss 0.995652; literature frontier n=29 |
| `erdos-287/` | Egyptian fractions, gaps ≤ 2 | **BOUND-EXTENDED** | No counterexample for k ≤ 48 (exhaustive MITM, `mitm_287.py`); k ≥ 49 needs C port |
| `erdos-647/` | Divisor-function maxima | **DEPRIORITIZED** | Idén (June 2026) verified to 10¹²; brute force dead below that |
| `erdos-364-366/` | Consecutive powerful numbers | **ATTEMPTED** | Scans logged; see dir README |
| `erdos-1052/` | Sixth unitary perfect number | **DEPRIORITIZED** | Calibrated; search space enormous, no near-miss signal |
| `erdos-64/` | Erdős–Gyárfás power-of-2 cycles | **BLOCKED** (needs construction) | Enumeration explodes below the 30-vertex lower bound |

## Other famous witness hunts

| Dir | Problem | Status | Key result |
|---|---|---|---|
| `hadwiger-nelson/` | 6-chromatic unit-distance graph | **ORACLE VALIDATED** | DSATUR colorer + Moser spindle reconstruction done; generation out of reach this iteration |
| `ramsey-r55/` | R(5,5) ≥ 44 via explicit graph | **ATTEMPTED** | Circulant families scanned, no witness; see dir README |
| `van-der-waerden/` | vdW lower-bound coloring certificates (W(5,3)>170, W(2,7)>3703, …) | **ATTACK-READY** | SAT encoder + checker gated 8/8 on exact values (`vdw.py`); CDCL can't reach record region (documented); probSAT local-search engine next |
