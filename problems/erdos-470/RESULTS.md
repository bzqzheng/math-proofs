# Erdős #470(i) — odd weird numbers: sweep results

**Result: no odd weird number found.** Constructive sweep of the δ < 10⁷
primitive-abundant tree to N = 10²⁴, July 2026. Zero finds across
**≥ 12 trillion DFS nodes** and **≥ 350,000 distinct abundant candidates
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

| Region (prefix, σ/n) | Nodes explored | Candidates tested |
|---|---|---|
| 3·5·7 (105, 1.83) via a=1·b=1·c=1 | **1,787,454,349,312** (1.79T, 23 h) | **264,140** |
| 3·5²·7 (525, 1.889) via a=1·b=2·c=1 | 937.2B (12 h) | 25,629 |
| 3²·5·11 (495, 1.891) via a=2·b=1·c=1 | 895.7B (12 h) | 19,655 |
| 3²·5·13 (585, 1.867) via a=2·b=1·c=1 | 671.5B (12 h) | 8,166 |
| 3²·5·7 (315, 1.981) via a=2·b=1·c=1 | 8.53B (2 × 12 h passes) | 8,051 |
| 3·5·7² (735, 1.861) via a=1·b=1·c=2 | 11.85B (12 h) | 13,568 |
| smaller dense pockets (b=2, b=3, c=2 of the above; P3=11/13 subtrees pre-split) | 0.6–80B each | ≤ 3,823 each |

Earlier pre-split explorations of the same spines (redone by the partition
runs): monster 982.5B/263,711; P2=5 subtree 558.5B/263,463; P2=7 subtree
544.0B/162; P2=11 325.9B/23; P2=13 288.5B/3.

## Structural findings (the compounding part)

1. **The abundancy-frontier law.** At every recursion level the first-exponent
   shard inherits ~90–95% of the tree's mass, because the search follows the
   prefix whose abundancy approaches 2 from below as slowly as possible
   (105 → 1.83, 315 → 1.981, 525/495/585 → 1.867–1.891, 1155 → **1.996**).
   Off-spine shards complete in seconds; the spine is effectively infinite
   against any fixed budget.
2. **Candidate-arrival decay.** 98.3% of each spine's candidates appear in
   the first ~72 s of the DFS; the tail decays (~2/min at 12 h, ~0.05/min at
   23 h). The candidate *set* of the explored spines is essentially known.
3. **Dense pockets are few.** Five regions hold ~97% of all candidates:
   264,140 / 25,629 / 19,655 / 13,568 / 8,166 / 8,051 tests. Everywhere
   else is ≤ 3,823 (see table).
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
