# Progress notes — math-proof campaign

Last updated: 2026-07-24

## Active background scans

| Task | Problem | Command / file | Current status | Timeout |
|---|---|---|---|---|
| `bash-nrop5gj5` | Erdős #470, SPF=3 · P2=5 · **P3=7** | fleet A, 12 h budget | the monster sub-sub-shard | 13 h |
| `bash-sq8pcmjx` | Erdős #470, SPF=3 · P2=5 · P3=11..23 | fleet B, 6 h per shard | 5 sub-sub-shards, sequential | 24 h cap |
| `bash-x5g6fc40` | Erdős #470, SPF=3 · P2=7 · P3=11,13 | fleet D, 6 h per shard | 2 sub-sub-shards, sequential | 24 h cap |
| `bash-0ns7ru10` | Erdős #470, SPF=3 · P2=7 · P3=17..73 | fleet E, 2 h per shard | 15 sub-sub-shards, sequential | 24 h cap |

**#470 P2=11/13 pruned retries timed out again (6 h):** P2=11: 325,883,379,712 nodes, tested=23; P2=13: 288,513,482,752 nodes, tested=3; both weird=0. The prune bought ~45%/30% more coverage but these trees are bigger — they go to P3-splitting too (viable sets computed: P2=11 → 12 shards P3=13..59; P2=13 → 10 shards P3=17..53). Queued as fleets F (P2=11) and G (P2=13), behind fleet C (P2=5 · P3=29..139), launching as worker slots free.

**#470 P3 gates PASSED (2026-07-25):** P2=5 union 134,601 = full 134,601; P2=7 union 8,082 = full 8,082 (10⁹, MIN_DEPTH=6, exact both ways). Production P3 fleet (48 sub-sub-shards for P2=5/7 + 22 for P2=11/13) running in waves behind the 4-slot background limit: fleets A (P3=7, the monster), B (P2=5 · P3=11..23), D (P2=7 · P3=11,13), E (P2=7 · P3=17..73) running; C (P2=5 · P3=29..139), F (P2=11 · P3=13..59), G (P2=13 · P3=17..53) queued. Runner: `run_p3_fleet.sh`.

**#470 P2=5/7 timed out at 12 h (2026-07-25 ~08:20):** P2=5: 558,523,752,448 nodes, tested=263,463, weird=0. P2=7: 544,000,770,048 nodes, tested=162, weird=0 (near-zero density — discovery mass is almost all in P2=5). Response: `P3` sub-sub-sharding added to `search_odd_weird.c` (same completeness argument, one level deeper), gate (a) passed. Viable P3 sets at 10²⁴: P2=5 → 31 values (7..139), P2=7 → 17 values (11..73). Production P3 sub-shards launch after gate (b3).

**#470 MIN_DEPTH prune (2026-07-24):** Liddy–Riedl (odd weird ⇒ ≥6 distinct prime factors) pushed into the DFS as `MIN_DEPTH` (env-gated, default off): cut any node with `depth + k_max(n, p_start) < MIN_DEPTH`, skip weirdness tests below depth 6. Gate (a): 7/7 even weirds with flag off. Gate (b): union ≡ full shard at 10⁹, tested=142,733 both ways, exact. Unpruned P2=11/13 retries timed out at 224.6B/222.0B nodes (tested=17/3, weird=0); relaunched with the prune. Insight → I10.

**#470 P2=11..43 first pass done 2026-07-24:** P2=17 (4.35B nodes, 431 s), P2=19 (16.0M, 1.6 s), P2=23/29/31/37/41/43 (< 80k nodes each, < 1 s) all complete, **0 weird**. P2=11 and P2=13 blew the 1 h cap (37.4B / 36.8B nodes, tested=1 and 0 — near-zero candidate density, pure due-diligence per I8) and were relaunched with 6 h budgets. Density measured at 10⁹ did NOT extrapolate to 10²⁴ → new insight I9.

**#699 COMPLETE 2026-07-24: 0 counterexamples for all n ≤ 10⁹** — segment 1 (`logs/699_run_1e9.log`): 6,787,335,884 pairs to n=674.8M; segment 2 (`logs/699_run_1e9_part2.log`): 3,549,443,097 pairs, done in 10,375 s. Total **10,336,778,981 (n,i) pairs, bad=0**.

**#470 SPF=3 shard** (`bash-51p87u8h`) hit its 6 h budget on 2026-07-24: `224,745,041,920` nodes, `263,057` candidates tested, **0 weird** (`logs/odd_prod_1e24_spf3.log`). The SPF=3 subtree was not exhausted, so the shard is being sub-sharded by second prime `P2 ∈ {5..43}` (12 values, analytically bounded) — `P2` support added to `search_odd_weird.c`, validated by gates (a) known-witnesses and (b) sub-shard union ≡ full shard.

**#699 part 1** (`bash-53si6yjm`) hit its 6 h timeout at `n = 674,800,000` — `6,787,335,884` pairs checked, **0 counterexamples** (`logs/699_run_1e9.log`). Added `N_START` resume support to `scan_699.py` and relaunched the remaining segment (`logs/699_run_1e9_part2.log`).

## Completed attempts

- **#779 Fortunate numbers** — no composite Fortunate number up to `n = 780` (time budget).
- **#458 lcm inequality** — no counterexample up to `k = 10^7`; min margin `0.15415` at `k = 4`.
- **#993 tree independence-polynomial unimodality** — deprioritized after extensive search.
  - SA on general trees: best ratio `0.962`.
  - Kadrawi–Levit families `3,k,k+j` / `3*,k,k+j`: clean to `k=100, j=30`; best `0.990`.
  - Pure spiders `S(a,b,c)`: clean to arm length `50`; all unimodal.
  - Pure star-arms: clean to `m_i = 120`; best `0.994`.
  - Caterpillars: clean in exhaustive sweep `L≤6, A≤12`; SA record near-miss `0.995652` at `n=463` (`a=[100,97,90,73,98]`).
  - Literature calibration (Reynolds Zenodo v3; Hibi–Kara–Vien arXiv Apr 2026): conjecture open, verified to `n=29`, known bush families pushed to `60` vertices without non-unimodal tree.

## Started / partial

- **#287 Egyptian-fraction gaps** — searching for `1 = Σ 1/n_i` with `1<n_1<...<n_k` and all gaps `≤2`. No counterexample for `k ≤ 21`; backtracking cost explodes at `k=22`.

## Blocked / deprioritized

- **#64 power-of-2 cycles** — raw cubic/min-degree-3 enumeration explodes before the 30-vertex lower bound. Needs a construction, not more CPU.
- **#1052 unitary perfect / #398 Brocard** — search space enormous, no near-miss signal.

## Compounding insights

1. **Verification asymmetry is the master filter.** Every attackable problem here is falsifiable by a single finite object with a fast mechanical check.
2. **Local search plateaus.** #993 and its caterpillar sub-problem both climb to `0.99+` fitness without producing a witness — a strong signal that either the conjecture holds or the counterexample is structurally distant.
3. **Literature calibration beats blind search.** The Reynolds preprint saved days of redundant computation on tree families already analyzed to `n=60`.
4. **Negative results are citable.** Extending clean verification bounds is real progress, even without a counterexample.
