# Optimization Notes — ppn.c, by tier

Date: 2026-07-31. Analysis of where the cycles go in `ppn.c` (exhaustive PPN
search, k prime factors) and what to do about it, ordered cheapest-highest-value
to most exotic. Conclusion up front: there are likely **2–3 orders of magnitude
available in software** before custom silicon is the right conversation — but
the silicon path is more viable than usual, for structural reasons (Tier 4).

No code has been changed; this is a plan. Step 0 is measurement.

---

## Step 0 — Profile first

Run `sample <pid> 10` on a live `ppn` process before touching anything.
Expected cost split (to be confirmed):

1. **`solve2` discriminant loop** (ppn.c:226–245) — the dominant sink. Per step:
   three multi-limb `mpz` adds (`D += dD`, `dD += ddD`, `s += A`), four small
   residue-tracker updates, and — whenever all four square-filters pass — a
   multi-limb `mpz_sqrt` + multiply + compare.
2. **`solve2` iter-mode loop** (ppn.c:255–266) — one multi-limb divisibility
   test `M % (A*q - N)` per prime; multi-limb division is the priciest basic op.
3. **The segmented sieve** — byte-per-candidate, `memset` + marking per 256KB
   block. Respectable but dated (Tier 2).
4. **`step()`/dfs overhead** for t>=3 — a few `mpz` mul/add per prime.

---

## Tier 1 — Algorithmic wins in the current structure (days, ~10–100x)

**1a. Strengthen the square prefilter.** Currently four moduli (64, 63, 65, 11);
joint pass rate ~ (32/64)(32/63)(33/65)(6/11) ≈ **7%** of steps trigger a full
multi-limb `mpz_sqrt`. Adding more moduli (9, 25, 49, 17, 19, 23, 29, 31 — each
an independent tracker pair like the existing ones) drives the false-pass rate
toward ~0.05%. Cost: ~16 tiny integer adds per step. Benefit: eliminates ~99%
of the most expensive call in the program. **Best line-item in the file.**

**1b. Fixed-width fast path.** Many nodes (small prefixes, shallow depth) have
`N`, `A`, `s`, `D` fitting in `__int128` or even `uint64_t`. GMP overhead
(dispatch, limb-count checks, realloc) dominates there. A specialized branch —
"all quantities fit 128 bits → run the whole disc loop in native arithmetic" —
runs that fraction of the tree at 10–50x GMP speed; fall back to `mpz` when a
bound check trips. Also: `mpz_init2` with realistic bit sizes to kill realloc
churn in the big-int path.

**1c. Divisor-form alternative for wide nodes.** ppn.c:254 uses
`(A*q1 - N)(A*q2 - N) = N^2 + A`. Iter-mode scans primes; the other exploitation
is to **factor M = N^2 + A directly** (ECM via GMP-ECM/yafu), then enumerate
divisors `d ≡ -N (mod A)`. For `T2SPAN`-deferred nodes — too wide to scan —
this changes complexity class when M <= ~80–90 digits. Measure actual N sizes
in the defer files before building this.

## Tier 2 — Structural / parallel wins (~core-count multiplier, then some)

**2a. Multithread wide spans.** The disc loop steps `s` through an arithmetic
progression; slices are embarrassingly parallel (each thread seeds `D` at its
offset once, then runs independently). Today parallelism is across processes by
prime prefix, so a single giant deferred node (span ~1e9) sits on one core for
days. Intra-process slicing fixes the worst-case tail.

**2b. Match process count to P-cores.** Observed load avg ~15 on an M4 Max
(~10–12 P-cores + 4 E-cores). Oversubscription past P-core count mostly burns
cache and memory bandwidth. Running `#P-cores` processes likely *increases*
total throughput.

**2c. Sieve modernization.** Byte-per-candidate over all integers → odd-only,
bit-packed, mod-30 wheel: ~8–15x less memory traffic, ~4x less scan work.
Reference implementation: `primesieve` (pre-sieved wheel patterns, bucket
sieving). Only after profiling confirms the sieve is hot.

**2d. Free wins.** PGO (`-fprofile-generate`/`-fprofile-use`), LTO, confirm the
GMP build uses its ARM64 assembly paths.

## Tier 3 — Bypassing the library (2–5x, real engineering cost)

GMP is near-optimal *for general-purpose* bignum; the win is specialization,
not a faster generic bignum:

- **Operation fusion.** Per step, `D += dD; dD += ddD; s += A` are three
  separate GMP passes over the limbs. A custom fixed-limb routine fuses them
  into one memory sweep — roughly halves memory traffic, the real cost once
  data exceeds L1.
- **Fixed precision.** Once the search is bounded, max bit-lengths are known.
  Fixed-size 512/1024/2048-bit arithmetic (crypto-style) eliminates GMP's size
  dispatch and allocation logic.

Realistic combined gain: **2–5x**. Verification risk is the true cost: keep the
current `ppn.c` as the reference oracle and differentially test any optimized
engine on identical subtrees (required by repo stage-5 gate culture anyway).

## Tier 4 — Custom silicon (FPGA/ASIC): viable shape, premature

Why it fits this problem unusually well: the disc-loop recurrence is *serial*
(each step depends on the last), which normally kills hardware parallelism —
but the expensive part is carry propagation across hundreds of bits. Keep
`D`, `dD`, `ddD` in **carry-save redundant form**: each step becomes one row of
full adders, O(1) gate depth, no carry chain → one step per clock at
300–500 MHz on FPGA, modular trackers essentially free in LUTs. Rare
"all-filters-passed" events go to the host CPU for exact sqrt + primality.
~16 pipelines slicing the s-range ≈ **100–1000x one CPU core**.

Why **not yet**:

- **Scale.** Historical number-theory silicon (Deep Crack, TWINKLE, NFS
  sieving engines) paid off at CPU-*decades*. Current workload is
  CPU-days-to-weeks. Tiers 1–2 recover 1–3 orders of magnitude for a few
  percent of the cost of a verified FPGA pipeline.
- **Verification burden.** Stage-5 credibility rests on independently checkable
  results; a hardware engine needs a bit-exact software twin for differential
  testing — doubling true cost.

Trigger condition for silicon: after Tiers 1–3 ship, the remaining deferred set
provably requires >= CPU-decades AND the math offers no further pruning.
(CPU echo of the same trick: NEON can't beat GMP's ADC carry chains, but
interleaving two independent s-slices in SIMD lanes is worth ~1.5x if the adds
turn out to be the final bottleneck.)

---

## Recommended sequence

1. `sample` a running process — confirm sqrt-vs-sieve-vs-adds split.
2. More square-filter moduli (1a) — ~a day, up to 100x on the dominant call.
3. `__int128` fast path (1b).
4. Thread-sliced spans for defer resolution (2a).
5. Evaluate ECM-factoring N^2+A on the widest deferred nodes (1c).
6. Only then: fixed-precision fused C (Tier 3); only then: hardware (Tier 4).

Invariant throughout: every optimized engine is differentially tested against
the current `ppn.c` as oracle, on identical subtrees, before its output counts
toward any frontier claim.

---

## Step 0 result (2026-07-31, measured on the live k9 tail, M4 Max)

`/usr/bin/sample <pid> 3` on a running k9 worker (2,591 samples; note:
`sample` is shadowed by a broken Homebrew script on this box — use the
absolute path):

- **~62% of cycles in `__gmpz_add`** (the three disc-loop adds per step).
  The underlying `__gmpn_add_n` is only ~1/5 of that → **~80% of the add
  cost is GMP dispatch overhead on small (1–2 limb) operands**, not limb
  arithmetic. This is exactly the Tier 1b case.
- **`mpn_sqrtrem` ≈ 0.7%** — the existing 4-modulus square prefilter is
  ALREADY effective. **Tier 1a is dead on this profile** (predicted
  dominant sink; measured negligible).
- Sieve not visible in this slice (worker was deep in disc-loop territory).

Revised sequencing: **Tier 1b (__int128 fast path, ~2.5–3× on the disc
loop) is the top item**, then Tier 3 fusion (~1.5× more). But retrofitting
for the remaining ~80 k9 shards does not pay — these optimizations belong
in the **ω=10 engine build** (weeks-scale job; ~3× = weeks saved and the
stretch-theorem enabler). The k9 tail runs as-is. Resolve stage
(3.9M ≤34-digit factorizations) needs no optimization (~10–15 min on 12
cores). LOOP-sieve cost is gate-quantified before core-days are committed.
