# erdos-375 — Grimm's conjecture: distinct prime divisors for consecutive composites

**Status:** SCANNING
**Source:** erdosproblems.com #375; C. A. Grimm, *A conjecture on consecutive composite numbers*, Amer. Math. Monthly 76 (1969) 1126–1128
**Signature fit:** P1 (a counterexample block is a finite, machine-checkable witness), P2 (bottleneck is search, not depth), P3 (self-contained elementary statement), P5 (fast generate–verify loop); P4 partial (the k-smooth reduction is exploitable structure)

## Statement

**Grimm's conjecture (1969).** For every block of consecutive composite integers
`n+1, …, n+k` there exist **distinct** primes `p_1, …, p_k` with `p_i | n+i`.

Witness shape: a counterexample is a single block `a..b` of composites whose
bipartite divisibility graph has no system of distinct representatives. Such a
block is checkable in milliseconds (exact max matching + a Hall violator).
Conversely, a verified bound is: every maximal composite run fully contained in
`[2, N]` admits an assignment. Testing maximal runs suffices — any block of
composites sits inside a maximal run and inherits its assignment by restriction,
and a failing sub-block would make its maximal run fail too.

## Calibration

Published frontier (per campaign task spec; web re-verification was unavailable
this session — flagged in the final report):

| source | result |
|---|---|
| Grimm, AMM 76 (1969) | conjecture stated; implies the existence of primes in short intervals |
| Laishram–Shorey, *Grimm's conjecture on consecutive integers*, Int. J. Number Theory 2 (2006) 207–211 | verified all blocks with **n ≤ 19,236,701,629 (~1.9·10¹⁰)** |

Never compute below the frontier without cross-validation: our sub-frontier runs
are oracle gates (the reduction must reproduce known-true answers), not results.
The campaign goal is a resumable open engine that re-verifies to the frontier
and then extends toward 10¹² (a 50–100× record extension).

## Oracle

- Checker: `grimm_reference.py` (sympy `factorint` on every member, complete
  bipartite graph, exact Hopcroft–Karp, assignment validated). Also unit-tests
  its own Hopcroft–Karp against exponential brute force on 300 random tiny graphs.
- Gate (a) known-positive: block 8..10 must yield exactly `{8:2, 9:3, 10:5}`;
  tricky prime-power blocks must pass full *and* reduced matching:
  `114..126` (contains 121=11², 125=5³), `524..540` (contains 529=23²),
  `8192..8208` (contains 8192=2¹³ — the block's ONLY 17-smooth member).
- Gate (b) exact agreement: C engine vs Python reference on **all blocks below
  10⁷** (block-by-block OK/FAIL + identical smooth-member and match counts);
  additionally full sympy matchings on **all blocks below 10⁶** must agree with
  the reduction (this tests the reduction itself, not just the C port — the
  I12 lesson: test the reduction where the answer is known).
- Gate (c) gap cross-check: engine `record-gap` lines below 10⁹ must equal a
  hardcoded OEIS A000230/A005250 first-occurrence table (29 records).

Run all gates: `.venv/bin/python problems/erdos-375/grimm_reference.py gate`
(builds the engine with clang if needed). Latest output: `logs/gates-2026-07-31.txt`.

## Approach

Engine: `grimm.c`, single file, `clang -O3 -o grimm grimm.c -lm`, uint64
throughout (n ≤ 10¹³ < 2⁶³).

1. Segmented odd-only sieve of Eratosthenes over `[2, N_MAX]`; consecutive
   primes delimit maximal composite runs (blocks are independent of
   segmentation — a block closes only when its terminating prime is found).
2. **Reduction.** In a block of length k, a prime `q > k` divides at most one
   member (two members differ by `≤ k−1 < q`), so any member with a prime
   factor `> k` can always take that factor. Only **k-smooth** members (all
   prime factors `≤ k`) are constrained: the block is OK iff they match into
   the primes `≤ k`. Proof of the reduction is in the `grimm.c` header;
   gate (b) validates it empirically below 10⁶ against direct full matchings.
3. Per block: factor each member by primes `≤ k` only (trial division with an
   exact early-exit: if `p² > rem` then `rem` is 1 or prime), collect smooth
   members, exact Hopcroft–Karp. A matching failure prints
   `CANDIDATE COUNTEREXAMPLE` (flushed) and the engine keeps going.

Config (env, `strtod`-parsed like `search_odd_weird.c`): `N_MAX` (default
1e10), `N_START` (resume offset, default 2), `SEG` (segment size, default
1e7), `PROGRESS` (progress interval, default 1e8), `DUMP_BLOCKS=1` (per-block
lines for gate b).

**Resumable.** State = `N_START` only. The engine walks back to the largest
prime `≤ N_START`, so the boundary block straddling `N_START` is re-verified
in full and shards stitch without gaps:

```bash
N_MAX=5e11            ./grimm > logs/run-0-5e11.txt
N_MAX=1e12 N_START=5e11 ./grimm > logs/run-5e11-1e12.txt
```

Sharding for 8 cores: split `[2, N]` into disjoint `[N_START_i, N_MAX_i]`
windows; the union verifies every block (a boundary block is reported whole,
exactly once, by the later shard — verified empirically below). Progress lines are flushed from the
first seconds (`config:` line immediately, then every `PROGRESS` integers).

## Results

All outputs below are from committed scripts (`grimm.c`, `grimm_reference.py`);
logs in `logs/`.

**Gates — ALL PASS** (`logs/gates-2026-07-31.txt`, total 75.7s on M4 Max):

- (a) HK == brute force on 300 random tiny graphs; block 8..10 → exactly
  `{8:2, 9:3, 10:5}`; blocks 114..126, 524..540, 8192..8208 pass full and
  reduced matching (full == reduced on each).
- (b) engine vs Python reference: **664,577/664,577 blocks below 10⁷ agree**
  block-by-block (OK/FAIL + smooth-member + match counts identical);
  **78,496 blocks below 10⁶ additionally agree with full sympy matchings**
  (the reduction itself is exact where the answer is known independently).
- (c) all **29 record prime gaps below 10⁹ match OEIS A000230/A005250**
  exactly; no counterexample candidates.

**Verification runs** (single core, M4 Max, 0 counterexamples everywhere):

| N_MAX | wall time | throughput | blocks | smooth members | max k | max matching | log |
|---|---|---|---|---|---|---|---|
| 10⁷ | 0.3s | 39.6M ints/s | 664,577 | 29,312 | 153 | 10 | `logs/timing-1e7-2026-07-31.txt` |
| 10⁹ | 27.4s | 36.4M ints/s | 50,847,532 | 409,844 | 281 | 10 | in `logs/gates-2026-07-31.txt` |
| 10¹⁰ | 288.2s | 34.7M ints/s | 455,052,509 | 1,485,866 | 353 | 10 | `logs/timing-1e10-2026-07-31.txt` |

10¹⁰ is still below the Laishram–Shorey frontier (1.92·10¹⁰) — it is a
calibration/timing run, not a record. (Consistency bonus: the 10¹⁰ log's
record gaps past 10⁹ — 288 @ 1,294,268,491; 292 @ 1,453,168,141;
320 @ 2,300,942,549 — continue to match OEIS A005250.)

**Resume/stitch verified empirically** (`logs/stitch-check-2026-07-31.txt`):
a single run to 10⁸ and two shards `[2, 5·10⁷]` + `[5·10⁷, 10⁸]` produce
byte-identical block sets (5,761,453 = 3,001,132 + 2,760,321 blocks, zero
duplicates — the boundary block is reported whole by the second shard only).

**Extrapolation to 10¹² (honest).** Throughput decays mildly with size —
36.4M → 34.7M ints/s from 10⁹ to 10¹⁰ (−4.7%/decade), driven by the
factoring loop length π(k̄), k̄ ≈ ln n (≈ 8 → 9 → 10 divisions per integer
from 10⁹ to 10¹²). Assuming the same decay for two more decades:
≈ 31.5M ints/s/core at 10¹², i.e. **≈ 31,700 core-seconds ≈ 9 core-hours
total — about 1.1 h wall-clock at 8 cores** (single-threaded engine, I/O
negligible). Not core-days: the reduction makes almost every block
nearly free, and the largest block below 10¹⁰ has k = 353 with only
10 smooth members to match.

## Verdict

**Settled here.** The engine is exact against an independent sympy oracle:
block-by-block agreement on all 664,577 blocks below 10⁷, the k-smooth
reduction itself validated against full matchings on all 78,496 blocks below
10⁶, prime-gap detection exact against OEIS A005250 below 10⁹, and the
resume semantics verified by an exact stitch experiment. Grimm's conjecture
re-verified for all blocks with n ≤ 10¹⁰ (455,052,509 blocks, 0
counterexamples, 0 matching failures) — still below the published frontier,
so a calibration pass, not yet an extension.

**Next action (production run to the frontier and beyond).** 8 shards to
10¹², e.g.:

```bash
for i in 0 1 2 3 4 5 6 7; do
  N_START=$((i))e11 N_MAX=$((i+1))e11 ./grimm > logs/prod-$i.txt &
done   # shard 0 starts at 2 (N_START=0 handled as fresh start)
```

Each shard is resumable from its own `N_START`; boundary blocks stitch
exactly (verified above). Expected cost ≈ 1–2 h wall at 8 cores per the
extrapolation. Any `CANDIDATE COUNTEREXAMPLE` line would be enormous news;
none is expected.
