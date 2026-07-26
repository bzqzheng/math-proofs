# Progress notes — math-proof campaign

Last updated: 2026-07-24

## Active background scans

| Task | Problem | Command / file | Current status | Timeout |
|---|---|---|---|---|
| `bash-elp5oyig` | Erdős #470, monster **a=2** retry | k_max_cap binary, 12 h budget | 195k→597k n/s after k_max_cap | 13 h |
| `bash-fn3uo9nd` | Erdős #470, P2=5 · P3=11 a=1..50 (fleet I) | 4 parallel runners, 1 h caps | EXPA split of fleet B's 368B-node timeout | 24 h cap |
| `bash-wbgfojqi` | Erdős #470, monster a=1 → b=1..33 (b-fleet) | 4 runners; b=1 at 12 h, rest 1 h | EXPB split of the 952B-node a=1 | 24 h cap |
| `bash-vfqahtb3` | Erdős #470, P2=5 · P3=13 a=1..50 (fleet J) | 4 parallel runners, 1 h caps | tested=289 region | 24 h cap |

**#470 fleet H done (2026-07-26), 0 weird:** a=14..50 complete (a=14: 21.7B nodes, 26 min, descending). **a=1..13 ALL timed out at 1 h, ~50–78B nodes each** (a=1: 78.0B/tested=123; a=2: 75.8B/3,527; a=3: 75.1B/1,290; a=4..13: ≤76B/≤725) — unlike the monster, P2=7·P3=11's mass does NOT collapse with a (deficient prefix 7·11 leaves headroom at every a). Its 13 stragglers (~1T nodes, near-barren) go to b-splits at LOW priority.

**Sweep scale checkpoint (2026-07-26):** complete-forever: all SPF ≥ 5, all SPF=3 · P2=17..43, monster a=3..50, P2=5 · P3=61..139, P2=7 · P3=31..73, P2=7 · P3=11 a=14..50. Outstanding ≈ **6–8 trillion nodes ≈ 90–120 core-hours** (monster b=1 + a=2; P2=5 · P3=11..59 splits; P2=7 · P3=11 a=1..13 + P3=13..29; barren P2=11/13). Discovery value remaining: thin outside the P2=5 spine (263k of ~271k tests already covered). Recommendation: grind the P2=5 spine to completion, then let the user decide whether the barren remainder (P2=7 stragglers + P2=11/13) is worth ~2 more machine-days for completeness-only coverage.

**#470 monster a=1 timed out at 12 h (2026-07-26):** 952,345,616,384 nodes, tested=263,623, weird=0 — the a=1 subtree alone exceeds 950B nodes. Split one exponent deeper: `EXPB` added (fix the exponent of 5; trivially complete partition). Gate: union over b=1..12 at 10⁹ exact (tested 95,851 = 95,851; node counts bit-identical: 172,581 = 172,581). b-mass concentrates at b=1 (121,536) > b=2 (40,011) > b=3 (9,067), same pattern as a. b-fleet launched: b=1 with 12 h budget, b=2..33 with 1 h caps (`run_b_fleet.sh`).

**#470 fleet B hit its 24 h task cap (2026-07-26), 0 weird:** P3=11 (368.3B nodes, tested=970), P3=13 (387.2B, 289), P3=17 (315.9B, 7) all timed out at 6 h unexhausted; P3=19 partial (lost, no checkpoint), P3=23 never started. All 11 timed-out P2=5 subtrees (P3=11..59) go to EXPA a-splits in tested-count order: P3=11 first (fleet I, running), then 13, 17, 19, 23, 29..59. Fleet P3=19 restarts from scratch — acceptable (~6 h lost; checkpoints would cost more than they save at this shard size).

**#470 fleet C done (2026-07-26), 0 weird:** complete: P3=61 (53.0B nodes, 68 min), 67 (17.3B), 71, 73, 79..139 (all < 1B, seconds–minutes). **Timed out at 2 h, not exhausted:** P3=29 (103.5B), 31 (102.1B), 37 (97.4B), 41 (95.0B), 43 (100.0B), 47 (84.2B), 53 (94.6B), 59 (93.5B) — sharp cliff: P3 ≤ 59 is a ~100B-node tree, P3 ≥ 61 completes. The 8 stragglers go to EXPA a-splits, queued behind a=1/a=2 retries and fleet H.

**#470 monster a-fleet done (2026-07-25):** a=3..50 complete, 0 weird. **a=1 timed out at 1 h** (77.29B nodes, tested=262,371) and **a=2 timed out at 1 h** (703M nodes, tested=7,874 — only 195k nodes/s: the MIN_DEPTH prune was paying a full k_max, 15–20 `next_prime` calls, at every depth < 6 node). Fix: `k_max_cap` (capped at `need` iterations, mathematically identical prune decision), 3× speedup on the a=2 pathology. Gates re-passed: 7/7 weirds; EXPA union at 10⁹ exact (102,065; full-run node count bit-identical at 377,361). a=1 relaunched with 12 h budget (`bash-61as8q1z`); a=2 launches when a slot frees.

**#470 fleet D done, both timed out (0 weird):** P2=7 · P3=11: 464,144,953,344 nodes, tested=162; P2=7 · P3=13: 323,825,598,464 nodes, tested=13. P2=7's tree is ~1T+ nodes and barren. P3=11 relaunched as fleet H (EXPA a-shards, `run_a_fleet.sh` — generalized runner); P3=13 queued for the same treatment, then P2=7 · P3=17..29 retries, then P2=11/13 splits (fleets F/G).

**Launch-bug fix (2026-07-25):** `cd DIR && runner1 & runner2 &` backgrounds only `cd DIR && runner1` — runners 2+ executed in the wrong CWD and died instantly. Caught by checking runner processes vs. expectation (the harness equivalent of gate (b): verify the parallelism you think you launched). Killed and relaunched fleets with absolute script paths (`bash-yg0fzzpf`, `bash-vaeejskt`). Lost work: ~7 min on a=1, ~2 shards of fleet C runner 1.

**#470 monster split-axis decision (2026-07-25):** the monster (P2=5 · P3=7) timed out at 12 h — **982,544,601,088 nodes, tested=263,711, weird=0** (~99.9% of all candidate tests in the sweep live here). P4 (fourth-prime) split axis **degenerated** — viable set 82,697 values at 10⁹, because (3,5,7) prefixes can themselves be abundant (insight I11). Reverted P4 patch; added `EXPA` (fix the exponent of 3: 50 bounded shards at 10²⁴, trivially complete partition). Gate (b-expa) passed exactly (union=102,065 at 10⁹); production a-fleet running (`run_expa_fleet.sh`).

**#470 fleet E done (P2=7 · P3=17..73), 0 weird:** complete: P3=31 (23.7B nodes, 30 min), 37 (2.1B), 41..73 (< 250M, seconds). **Timed out at 2 h, not exhausted:** P3=17 (104.5B nodes), 19 (98.8B), 23 (95.5B), 29 (95.3B) — every P3 ≤ ~29 is a ~100B-node tree at 10²⁴ (I9 confirmed again).

**Scale assessment (honest):** completed-forever so far: all SPF ≥ 5 shards, all SPF=3 · P2=17..43, all P2=7 · P3 ≥ 31. Outstanding: P2=5 fleet (P3=7/11..23/29..139), P2=7 · P3=17..29 retries, P2=11 · P3=13..59, P2=13 · P3=17..53 — est. **3–5 trillion nodes ≈ 60–100 core-hours** ≈ 1–1.5 days wall at 8-way parallelism. Value order: P2=5 (263k tested, all discovery mass) > P2=7 > barren P2=11/13 (completeness only). Throughput doubled to 2 workers per task slot; tasks execute in discovery-value order so any stop leaves the least-valuable work incomplete.

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
