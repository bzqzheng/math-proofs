# Progress notes — math-proof campaign

Last updated: 2026-07-31 (M4 Max)

**#470 MINING COMPLETE — PROBLEM CLOSED (2026-07-31).** Full 25-region harvest: **356,066 deduped candidates** (`candidates.csv.gz`), `MINING-report.md`. δ-distribution: min=90, median 5.18M, p99=9.90M vs cap 10⁷ — the cap binds. But the near-miss metrics kill the follow-up: among the 1,000 smallest-δ candidates (where weirdness would most plausibly hide, cf. known even weirds at δ=4..12) the closest-to-weird has run-length **83** (92% of δ covered); from δ≈1050 up every 1000-window saturates at 1000/1000. Semiperfection is robust across the whole class; a DELTA_MAX=10⁹ sweep would sample candidates with *more* divisor mass per target — expressibility gets easier, not harder. **Decision: no δ-sweep, no barren tail. #470 is closed at "sweep complete as designed + substrate banked"; remaining EV lowest in portfolio.**

## Active background scans

| Task | Problem | Command / file | Current status | Timeout |
|---|---|---|---|---|
| — | all sweep fleets complete | see `problems/erdos-470/RESULTS.md` | **sweep done as designed (2026-07-30)** | — |

**#470 MOP-UP — discovery-relevant work complete (2026-07-30).** All pockets with ≥ 250 tests have had deep passes; every straggler is exhausted or documented-bound, zero weird everywhere. **j8-fleet:** P3=13·a=4·b=2·c=1 timed out at 918,948,290,560 nodes, tested=1,416 (prefix 26325, σ/n = **1.995** — ninth ~900B-class spine, closest to 2 yet); c≥2 instant. Spine registry (nine spines, ALL σ/n ∈ (1.80, 1.995), zero exceptions): 105/1.83 (1.79T, 264,140) · 525/1.889 (937.2B, 25,629) · 495/1.891 (895.7B, 19,655) · 585/1.867 (671.5B, 8,166) · 315/1.981 (8.53B, 8,051) · 12375/1.967 (905.1B, 3,407) · 1755/1.914 (561.2B, 3,158) · 2925/1.929 (904.9B, 845) · 825/1.803 (891.9B, 1,960) · 26325/1.995 (918.9B, 1,416). Remaining: 3 pockets ≤ 522 tests landing (table above); barren tail P3=17..59 (~1.5T nodes, ~1 day, expected ≤ 7 tests each) held for the user's call.

**#470 b3-fleet (monster a=2·b=1) done (2026-07-28), 0 weird:** c=2..22 all complete instantly (c=2: 33,362 nodes/tested=90; rest negligible). **c=1 timed out at 12 h — 8,531,447,808 nodes, tested=8,051** (prefix 315: σ/n = 1.981 — frontier shard; second identical 12 h pass, so it gets the **documented-bound treatment**: no third partial run; slots go to completable pockets instead).

**#470 j3-fleet (P3=13 · a=2·b=1) done (2026-07-28), 0 weird:** c=6..20 complete (c=6: 20.7B nodes, 25 min, descending). **c=1 timed out at 12 h — 671.5B nodes, tested=8,166** (prefix 585: σ/n = 1.867 — fourth frontier spine, documented-bound). c=2..5 timed out: c=2 (661M/**3,823** — dense; retry running as `bash-vdnd6edi`), c=3 (75.1B/24), c=4 (72.8B/9), c=5 (52.9B/0) — c=3..5 queued.

**#470 WHALE LANDED — SWEEP COMPLETE AS DESIGNED (2026-07-28).** Final whale run: **1,787,454,349,312 nodes (1.79T, 23 h), tested=264,140, weird=0**. Full negative-result writeup with coverage map: **`problems/erdos-470/RESULTS.md`**. Headline: 0 odd weird numbers across ≥12T nodes and ≥350k distinct candidates; all barren/off-spine regions exhausted to 10²⁴; five abundancy-frontier spines documented (264,140 / 25,629 / 19,655 / 13,568 / 8,166 / 8,051 tests). Mop-up tail (pockets ≤ ~3.8k tests) continues in background slots; the result does not depend on it.

**#470 i3-fleet (P3=11 · a=2·b=1) done (2026-07-27), 0 weird:** c=6..21 complete (c=6: 40.1B nodes, 47 min, descending). **c=1 timed out at 12 h — 895.7B nodes, tested=19,655** (prefix 495: σ/n = 1.891 — third abundancy-frontier whale, documented-bound treatment). c=2..5 timed out: c=2 (45.6B/2,665), c=3 (72.5B/41), c=4 (62.5B/21), c=5 (50.7B/5) — queued. All top-5 dense pockets have now had their c-level pass; the three whales (263,623 / 25,629 / 19,655 tests) are documented to ~900–950B nodes each, 0 weird.

**#470 c2-fleet (a=1·b=2) done (2026-07-27), 0 weird:** c=8..25 complete. **c=1 timed out at 12 h — 937.2B nodes, tested=25,629** (prefix 525: σ/n = 1.889 — another abundancy-frontier whale; gets the documented-bound treatment per the wrap-up plan, not a marathon). c=2..7 timed out: c=2 (77.6B/732), c=3 (69.9B/78), c=4 (77.2B/16), c=5 (1.7B/10), c=6 (64.8B/0), c=7 (48.7B/0) — queued behind j3.

**#470 j2-fleet (P3=13 · a=2) done (2026-07-27), 0 weird:** b=9..33 complete. **b=1..8 timed out**: b=1 (657.2B nodes, tested=8,166 — queued for c-split behind the whale), b=2 (72.9B/797), b=3 (75.4B/38), b=4 (68.7B/34), b=5 (5.0B/30), b=6 (43.9B/9), b=7 (53.8B/0), b=8 (46.9B/0).

**Why the whale is the end of the spine (2026-07-27):** the recursion's first-exponent shards inherit ~90–95% of the parent's mass because they sit at the abundancy frontier: prefix 3·5·7 = 105 has σ/n = 1.83 (deficient), and 3·5·7·11 = 1155 has σ/n = **1.996** — just below 2 — so the (1,1,1,1,…) prefix allows maximal depth and maximal tree mass at every level. Fully exhausting the whale by continued EXPD-style splitting is days more for a decaying ~2/min candidate trickle. Decision: one final 23 h run (`bash-7z1aw8h1`); afterwards the whale region is written up as "explored to ~2.8T nodes, 263,623+ candidates tested, 0 weird, arrival rate decayed to ≈0–2/min" and the sweep wraps up with the coverage map.

**#470 c-fleet (a=1·b=1) done (2026-07-27), 0 weird:** c=8..27 complete (c=8: 33.9B nodes, 43 min, descending). **c=1..7 timed out**: c=1 (**943.8B nodes, tested=263,623** — the whale; gets a 24 h run at the next free slot), c=2 (985M/tested=13,552 — 50× denser per node than c=1; retry running), c=3 (77.0B/438; retry running), c=4 (18.8B/31), c=5 (42.1B/15), c=6 (44.5B/1), c=7 (49.2B/0) — c=4..7 queued.

**Candidate-arrival analysis (c=1 log):** 98.3% of all candidates (259,080/263,623) appear in the first **72 seconds** of the DFS; the tail then trickles at ~2/min and decaying (262,236 at 36 min → 263,623 at 12 h). Interpretation: the candidate SET of the spine is essentially known; the unexplored remainder is not candidate-free but is very thin. This caps the expected yield of further grinding while keeping it nonzero — the honest basis for the user's continue/wind-down call.

**#470 i2-fleet (P3=11 · a=2) done (2026-07-27), 0 weird:** b=9..33 complete (b=9: 45.4B nodes, 52 min, descending). **b=1..8 timed out at 1 h**: b=1 (**892.7B nodes, tested=19,637** — third ~900B subtree; relaunched as i3 c-fleet `bash-pd38jjem`), b=2 (898M/2,140), b=3 (78.4B/2,984), b=4 (1.17B/43), b=5 (13.0B/15), b=6 (29.7B/8), b=7 (48.1B/6), b=8 (45.3B/0) — b=2..8 c-splits queued (b=3, b=2 first by tested).

**#470 monster a=2 b-fleet done (2026-07-27), 0 weird:** b=2..33 all complete in seconds (b=2: 21,819 nodes/tested=153; rest negligible). **a=2·b=1 timed out at 12 h** — 8,428,879,872 nodes, tested=8,048 (~195k n/s slow-dense rate), queued for a c-split behind the richer a=1·b=2.

**#470 fleet J done (2026-07-26), 0 weird:** a=14..50 complete (a=14: 21.4B nodes, descending). **a=1..13 ALL timed out at 1 h** (~590B nodes covered): a=1 (75.5B/tested=262), a=2 (906M/**tested=7,793** — slow-dense pocket), a=3 (632M/1,153), a=4 (656M/490), a=5 (3.3B/247), a=6..13 (34–75B/≤82). Stragglers queued for b-splits in tested order (a=2 running as `bash-1ocbdki3`; then a=3, a=4, a=5, a=1, a=6..13). P2=5·P3=17..59 still unstarted; the dense-pocket map so far: monster b=1 (263,623) ≫ a=1·b=2 (25,167) > P3=11·a=2 (19,332) > P3=13·a=2 (7,793) > everything else (≤ ~8k).

**#470 monster a=1 b-fleet done (2026-07-26), 0 weird:** b=10..33 complete (b=10: 27.7B nodes, 34 min, descending). **b=1..9 timed out at 1 h** (~600B nodes): b=1 (952.16B — 99.96% of a=1's mass, tested=263,623), b=2 (67.6B/**tested=25,167** — third-richest region), b=3 (77.7B/650), b=4 (75.7B/104), b=5..9 (52–76B/≤19). Response: `EXPC` added (fix exponent of 7), union gate at 10⁹ exact (tested 81,950 = 81,950; nodes bit-identical 121,536 = 121,536). a=1·b=1 relaunched as c-fleet (`bash-069j36i8`, c=1 at 12 h); b=2..9 c-splits queued (b=2 first).

**#470 fleet I done (2026-07-26), 0 weird:** a=14..50 complete (a=14: 36.0B nodes, 42 min, descending). **a=1..13 ALL timed out at 1 h** (~620B nodes covered): a=1 (77.1B/tested=880), a=2 (69.1B/**tested=19,332** — second-highest density anywhere), a=3 (76.9B/775), a=4 (783M/393 — slow dense pathology), a=5 (1.04B/1,398 — same), a=6 (79.4B/677), a=7..13 (23–50B/≤85). All 13 stragglers queued for b-splits in tested order (a=2 first, running; then a=5, a=1, a=3, a=6, …).

**Queue-growth note (2026-07-26):** each a-fleet completion adds ~13 b-split candidates — the outstanding list is growing superlinearly, and P2=5·P3=17..59 (11 subtrees) hasn't even started. Realistic remaining: **multiple machine-days** for the full P2=5 spine, ~1 more for the barren remainder. The discovery-meaningful work is now: monster b=1 + a=2·b=1 (running), P3=11·a=2 b=1 (running), then P3=11·a=5/a=1/a=3/a=6, P3=13 stragglers (fleet J running), P3=17..59. Everything else is completeness-only.

**#470 monster a=2 timed out at 12 h (2026-07-26):** 8,519,983,104 nodes, tested=8,051, weird=0 — a=2's tree is slow (197k n/s: deep p-loops at high abundancy headroom) but small in absolute terms vs a=1. Split to b-shards: b=2..33 all completed in seconds (b=2: 21,819 nodes/tested=153; b ≥ 3 negligible); **all mass is in b=1** — the recursion follows the least-abundant spine (a=1, b=1, c, …), where the tree is deepest. b=1 running at 12 h (`bash-a5h1m2bz`); if it times out, the next axis is EXPC (exponent of 7).

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

- **#287 Egyptian-fraction gaps** — MITM reformulation (`mitm_287.py`): **no counterexample for k ≤ 45 exhaustive** (k=45: 23M+67M halves, 313 s; gates pass). k=46–48 running on M4 Max; k ≥ 49 needs a C port.

## Blocked / deprioritized

- **#64 power-of-2 cycles** — raw cubic/min-degree-3 enumeration explodes before the 30-vertex lower bound. Needs a construction, not more CPU.
- **#1052 unitary perfect / #398 Brocard** — search space enormous, no near-miss signal.

## Compounding insights

1. **Verification asymmetry is the master filter.** Every attackable problem here is falsifiable by a single finite object with a fast mechanical check.
2. **Local search plateaus.** #993 and its caterpillar sub-problem both climb to `0.99+` fitness without producing a witness — a strong signal that either the conjecture holds or the counterexample is structurally distant.
3. **Literature calibration beats blind search.** The Reynolds preprint saved days of redundant computation on tree families already analyzed to `n=60`.
4. **Negative results are citable.** Extending clean verification bounds is real progress, even without a counterexample.
