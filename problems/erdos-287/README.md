# Erdős #287 — gaps in Egyptian-fraction representations of 1

**Status:** ACTIVE — C MITM engine validated; no counterexample for k ≤ 50 (2026-07-31)
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

## C port (`mitm_287.c`) — 2026-07-31
Python's per-entry `Fraction`/tuple/int objects cap out at ~25 GB by k=48;
k ≥ 49 needs the C engine. `mitm_287.c` reproduces the Python mathematics
exactly:

- Same 3-prime residue hash (P1=2^61−1, P2=2^31−1, P3=999999937), inverses
  n^(p−2) mod p, residues accumulated mod p per term; all residue arithmetic
  is exact u64/u128.
- Same float pruning: IEEE doubles, identical operation order. One subtlety:
  CPython ≥ 3.12 `sum()` uses Neumaier compensated summation, so
  `max_rem(l,r) = sum(1.0/(l+i))` is NOT naive left-to-right accumulation.
  The C `mr` table replicates Neumaier bit-exactly (verified: all 16,400
  entries l≤400, r≤40 hex-identical to Python's `max_rem`).
- Same split j=k//2, same lo/hi bounds, same join window (min_s2..max_s2),
  same boundary-gap join `1 <= tup2[0] − last_fj <= GAP`.

Compact design (16 bytes/entry vs Python's ~100+ bytes):
- Entry = u64 digest of the residue triple + u64 packed first-half tuple
  (first term in 7 bits, then 1 bit per +1/+2 step). Open addressing, linear
  probing, power-of-2 slots at ≤ 2/3 load + 1-bit occupancy map (no sentinel
  can alias a real entry). Two passes over the first half (count → allocate →
  insert); the second half is streamed with no storage.
- The engine dumps hit candidates (full k-tuples) to
  `hits_287_k{K}_gap{GAP}.txt`; exact `Fraction` verification stays in Python
  (`verify_hits.py`, same check as `mitm_287.py:116`).

**Safe failure direction.** The 64-bit digest join is a SUPERSET of Python's
exact-triple join: a digest collision (~2⁻⁶⁴) can only ADD a spurious
candidate, which `verify_hits.py` rejects (safe). A true residue match always
produces the same digest, so no hit is ever missed — a missed hit would be a
missed counterexample (the unsafe mode, excluded by construction). The engine
is always exhaustive (verification is external, so early-exit is moot).

Gate evidence (`./gate_c.sh`, full log `gate_c_full.log`):
- (a) GAP=3 k=3 → candidate dumped, `verify_hits.py` confirms (2,3,6) exact.
- (b) GAP=2 k ≤ 21 → zero candidates, zero verified (matches Python gate).
- (c) k=22..40: C vs Python `--exhaustive` — **all 19 k-values identical** in
  first_half, second_half, and hits == C verified (`compare_gate.py`:
  `EQUIVALENCE OK: 19 k-values identical`).
- Scale check: k=46,47,48 reproduce the Python log halves EXACTLY
  (45,844,733+67,500,779 / 47,971,376+144,536,739 / 95,654,131+145,130,144),
  cand=0, in 6.0/11.4/17.1 s vs Python's 316/489/687 s (40–53× faster),
  peak RSS 6.5 GB for all three in one process (k=48 table alone: 4 GB).

Memory model: slots = pow2 ≥ 1.5·first_half, 16 B/slot + 1 bit. Measured
(single-k runs, `/usr/bin/time -l` peak RSS): k=48 → 2²⁸ slots, 4.33 GB;
k=49 (first_half 99.9M) → 2²⁸ slots, 4.33 GB; k=50 (first_half 199.2M) →
2²⁹ slots, 8.66 GB. Fits 64 GB with ~7× headroom; k=51+ extrapolates to
≤ 17 GB through k≈53.

## Results
- No counterexample for k ≤ 21 (old DFS + MITM gate (b)).
- No counterexample for k ≤ 45 (exhaustive MITM, ≤ 313 s per k, 2026-07-30).
- No counterexample for k ≤ 48 (exhaustive MITM, M4 Max, 2026-07-31; k=48:
  95.6M+145.1M halves, 687 s — `logs/mitm_k46-48.log`).
- C engine reproduces k ≤ 48 exactly (see gate evidence above).
- **No counterexample for k = 49 (C engine, 2026-07-31; 99,906,514+292,376,059
  halves, 0 candidates, 23.7 s, peak RSS 4.33 GB — `logs/mitm_c_k49.log`).**
- **No counterexample for k = 50 (C engine, 2026-07-31; 199,239,194+310,518,036
  halves, 0 candidates, 35.8 s, peak RSS 8.66 GB — `logs/mitm_c_k50.log`).
  Frontier: no counterexample for k ≤ 50.**
- **No counterexample for k = 51 (207,742,586+605,527,283 halves, 60.0 s —
  `logs/mitm_c_k51.log`), k = 52 (414,336,931+627,479,503 halves, 83.9 s,
  16 GB table — `logs/mitm_c_k52.log`), k = 53 (431,340,373+1,268,572,265
  halves, 139.4 s — `logs/mitm_c_k53.log`), k = 54 (860,399,078+1,331,785,728
  halves, 189.4 s, 32 GB table — `logs/mitm_c_k54.log`); verify_hits 0/0
  throughout. **Frontier: no counterexample for k ≤ 54 — the 64 GB wall for
  this engine (k=55 needs 2³² slots ≈ 137 GB); further k needs a
  streaming/external-memory table redesign.**
  Frontier: no counterexample for k ≤ 53.**

## Run
```
cd problems/erdos-287
# Python spec engine
../../.venv/bin/python mitm_287.py gate
../../.venv/bin/python mitm_287.py --exhaustive 22 40
# C engine
clang -O3 -o mitm_287 mitm_287.c -lm
./gate_c.sh                                  # full gate: (a),(b),(c) equivalence
GAP=2 /usr/bin/time -l ./mitm_287 49 49      # production k=49
../../.venv/bin/python verify_hits.py 49 hits_287_k49_gap2.txt
GAP=2 /usr/bin/time -l ./mitm_287 50 50      # production k=50
../../.venv/bin/python verify_hits.py 50 hits_287_k50_gap2.txt
```
