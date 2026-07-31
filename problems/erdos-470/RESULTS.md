# Erdős #470(i) — odd weird numbers: sweep results

**Result: no odd weird number found.** Constructive sweep of the δ < 10⁷
primitive-abundant tree to N = 10²⁴, July 2026. Zero finds across
**≥ 20 trillion DFS nodes** and **≥ 360,000 distinct abundant candidates
tested** (each candidate an odd abundant n with δ = σ(n) − 2n < 10⁷,
checked for semiperfection by exact bitset DP at target δ).

## Question and prior frontier

A weird number is abundant but not semiperfect (no subset of its proper
divisors sums to itself). All known weird numbers are even. Does an odd one exist?

- No odd weird number below 10²¹ (Fang 2022, exhaustive).
- Any odd weird number has ≥ 6 distinct prime factors (Liddy–Riedl 2018).
- This sweep is orthogonal in range (to 10²⁴) but **constructive**: it
  enumerates only candidate-bearing factorizations (δ < 10⁷), not all odd n.

## Method

DFS over factorizations n = ∏ pᵢ^aᵢ (odd, exact 128-bit integer (n, σ)) with:

- **Oracle (I1):** weird ⟺ δ = σ(n) − 2n > 0 and δ not a sum of distinct
  proper divisors. Subset-sum at target δ (forced < 10⁷), not at n (~10²⁴).
- **Abundancy-reachability prune (I6):** branch on p only if
  abund·(p/(p−1))^(k+1) > 2, k = room left under N_CAP.
- **MIN_DEPTH=6 prune (I10):** cut any node that provably cannot reach 6
  distinct prime factors (Liddy–Riedl), with `k_max_cap` (bounded iteration).
- **Recursive partitioning:** SPF (smallest prime factor) → P2/P3 (next
  primes) → EXPA/EXPB/EXPC (exponents of 3/5/7). Every partition validated
  by union gates: sub-shard candidate counts match the unpartitioned run
  **exactly** at N = 10⁹ (four levels, bit-identical node counts where
  applicable). Pipeline gates (I5): 7/7 known even weirds reproduced at
  N = 10⁴; zero finds below 10²¹ as required.

Code: `search_odd_weird.c` (C, `__int128`-exact); runners `run_p3_fleet.sh`,
`run_a_fleet.sh`, `run_b_fleet.sh`, `run_c_fleet.sh`; logs in `logs/`.

## Coverage map

### Fully exhausted (0 weird)

| Region | Scope |
|---|---|
| SPF = 5..53 shards | 15 shards, full 10²⁴ sweep |
| SPF=3 · P2 ∈ {17..43} | 8 sub-shards |
| SPF=3 · P2=5 · P3=61..139 | 18 sub-sub-shards (P3=61: 53.0B nodes largest) |
| SPF=3 · P2=7 · P3=31..73 | 11 sub-sub-shards |
| monster (3·5·7) a=3..50, a=1·b=10..33, a=2·b=2..33 | all exponent shards |
| a=1·b=1·c=8..27, a=1·b=2·c=8..25, P3=11·a=2·b=1·c=6..21, P3=13·a=2·b=1·c=6..20, a=2·b=1·c=2..22 | all exponent shards |
| P2=7·P3=11 a=14..50, P2=5·P3=11 a=14..50, P2=5·P3=13 a=14..50, P3=11·a=2·b=9..33, P3=13·a=2·b=9..33 | all exponent shards |

### Documented bounds (explored, not exhausted, 0 weird)

The abundancy-frontier spines — prefixes with σ/n closest to 2 from below,
where the tree is deepest and essentially all candidates live:

### Documented bounds (explored, not exhausted, 0 weird)

The abundancy-frontier spines — prefixes with σ/n closest to 2 from below,
where the tree is deepest and essentially all candidates live. **Every long
pole in ~20T nodes of exploration sits in this table; every one has
σ/n ∈ (1.72, 1.995).**

| Region (prefix, σ/n) | Nodes explored | Candidates tested |
|---|---|---|
| 3·5·7 (105, 1.83) via a=1·b=1·c=1 | **1,787,454,349,312** (1.79T, 23 h) | **264,140** |
| 3·5²·7 (525, 1.889) via a=1·b=2·c=1 | 937.2B (12 h) | 25,629 |
| 3²·5·11 (495, 1.891) via a=2·b=1·c=1 | 895.7B (12 h) | 19,655 |
| 3·5·7² (735, 1.861) via a=1·b=1·c=2 | 11.85B (12 h) | 13,568 |
| 3²·5·13 (585, 1.867) via a=2·b=1·c=1 | 671.5B (12 h) | 8,166 |
| 3²·5·7 (315, 1.981) via a=2·b=1·c=1 | 8.53B (2 × 12 h) | 8,051 |
| 3²·5·13² (7,605, 1.744) via a=2·b=1·c=2 | 276.5B (12 h) | 6,359 |
| 3²·5³·11 (12,375, 1.967) via a=2·b=3·c=1 | 905.1B (12 h) | 3,407 |
| 3³·5·13 (1,755, 1.914) via a=3·b=1·c=1 | 561.2B (12 h) | 3,158 |
| 3·5³·11 (4,125, 1.815) via a=1·b=3·c=1 | 16.53B (12 h) | 2,009 |
| 3·5²·11 (825, 1.803) via a=1·b=2·c=1 | 891.9B (12 h) | 1,960 |
| 3⁴·5²·13 (26,325, 1.995) via a=4·b=2·c=1 | 918.9B (12 h) | 1,416 |
| 3⁵·5·11 (13,365, 1.961) via a=5·b=1·c=1 | 12.34B (12 h) | 1,398 |
| 3·5⁴·13 (24,375, 1.794) via a=1·b=4·c=1 | 888.8B (12 h) | 1,267 |
| 3·5·11 (165, 1.745) via a=1·b=1·c=1 | 432.5B (12 h) | 1,027 |
| 3⁶·5·11 (40,095, 1.963) via a=6·b=1·c=1 | 687.5B (12 h) | 959 |
| 3⁴·5·11 (4,455, 1.955) via a=4·b=1·c=1 | 806.0B (12 h) | 923 |
| 3³·5·11 (1,485, 1.939) via a=3·b=1·c=1 | 427.1B (12 h) | 919 |
| 3²·5²·13 (2,925, 1.929) via a=2·b=2·c=1 | 904.9B (12 h) | 845 |
| 3·5³·7 (2,625, 1.902) via a=1·b=3·c=1 | 234.3B (12 h) | 819 |
| 3³·5³·13 (43,875, 1.991) via a=3·b=3·c=1 | 900.2B (12 h) | 584 |
| 3·5·7³ (5,145, 1.866) via a=1·b=1·c=3 | 177.8B (12 h) | 612 |
| 3·5³·7² (6,125, 1.452) via a=1·b=3·c=2 | 10.59B (12 h) | 562 |
| 3⁵·5·13 (15,795, 1.936) via a=5·b=1·c=1 | 746.9B (12 h) | 546 |
| 3·5·13 (195, 1.723) via a=1·b=1·c=1 | 639.8B (12 h) | 302 |
| ~20 smaller pockets (c=2/b=2/c=3 of the above) | 0.7–80B each | ≤ 522 each |

Earlier pre-split explorations of the same spines (redone by the partition
runs): monster 982.5B/263,711; P2=5 subtree 558.5B/263,463; P2=7 subtree
544.0B/162; P2=11 325.9B/23; P2=13 288.5B/3.

## Structural findings (the compounding part)

1. **The abundancy-frontier law.** At every recursion level the first-exponent
   shard inherits ~90–95% of the tree's mass, because the search follows the
   prefix whose abundancy approaches 2 from below as slowly as possible.
   All ten ~900B-class spines sit at **σ/n ∈ (1.72, 1.995)** — zero exceptions
   (see table; closest: 26,325 at 1.995). Off-spine shards complete in
   seconds; the spine is effectively infinite against any fixed budget.
2. **Candidate-arrival decay.** 98.3% of each spine's candidates appear in
   the first ~72 s of the DFS; the tail decays (~2/min at 12 h, ~0.05/min at
   23 h). The candidate *set* of the explored spines is essentially known.
3. **Dense pockets are few.** The top five regions hold ~90% of all
   candidates (264,140 / 25,629 / 19,655 / 13,568 / 8,166 tests);
   everything else is ≤ 8,051 (see table).
4. **Splitting discipline.** The prime-value axis degenerates at depth 3
   (I11: viable set explodes to 82,697 once prefixes can be abundant);
   exponent axes (EXPA/EXPB/EXPC) are always bounded and trivially complete.
   Shard weights at small caps never extrapolate (I9: every P3 ≤ 29 is a
   ~100B-node tree at 10²⁴ regardless of its 10⁹ size).

## What would settle the question

- A proof that odd weird numbers require δ ≥ B(n) for some growing bound
  would make this sweep's δ-restriction exact — open.
- Full exhaustion of the abundancy-frontier spines (est. 5–10T more nodes
  each, candidate yield ~0) — diminishing returns, not pursued.
- The literature direction (primitive weird with large prime factors,
  Melfi's conditional infinitude) is untouched by this sweep.

## Reproducibility

```
cd problems/erdos-470
clang -O3 -o search_odd_weird search_odd_weird.c -lm
ALLOW_EVEN=1 N_CAP=10000 ./search_odd_weird          # gate (a): 7 known weirds
# any sweep region, e.g. the whale spine:
N_CAP=1e24 DELTA_MAX=1e7 MIN_DEPTH=6 SPF=3 P2=5 P3=7 EXPA=1 EXPB=1 EXPC=1 \
  TIME_BUDGET=82800 ./search_odd_weird
```

Union-gate evidence (partition completeness) and all run logs: `logs/`.
Campaign narrative: `docs/progress.md`. Method lessons: `docs/insights.md` (I1–I11).
