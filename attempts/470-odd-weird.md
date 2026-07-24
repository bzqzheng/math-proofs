# Attempt: Erdős #470(i) — does an odd weird number exist?

## Status: ACTIVE SEARCH, 2026-07-24

## Known frontier (from Lean file + literature)
- No odd weird number below 10^21 (Fang 2022).
- Any odd weird number has ≥ 6 distinct prime divisors (Liddy–Riedl 2018).
- Melfi: infinitely many primitive weird numbers exist, conditional on prime gaps.

## Our key structural trick (derived independently; likely known to specialists)
n weird ⟺ δ := σ(n) − 2n > 0 AND δ is NOT a sum of distinct proper divisors.
Proof: semiperfect ⟺ some subset of proper divisors sums to n ⟺ its complement
(within all proper divisors, total σ(n)−n) sums to σ(n)−2n = δ.
Consequence: the weirdness oracle collapses from subset-sum at target n
(infeasible for n ~ 10^21) to subset-sum at target δ, which we FORCE to be
small by construction (δ < 10^7). Bitset DP, exact, microseconds per test.

## Pipeline (attempts/search_odd_weird.py)
- DFS over factorizations n = ∏ p_i^a_i with exact integer (n, σ).
- Prune 1: δ ≥ DELTA_MAX → cut (δ is monotone once abundant: both
  abundancy−2 and n grow when factors are appended).
- Prune 2: deficient node → cut if even the greediest continuation
  (next smallest primes, as many as the size cap allows) can't reach
  abundancy 2.
- Candidates with 0 < δ < DELTA_MAX get the exact δ-test.

## Validation (PASSED)
Even run below 10^6 reproduced ALL known weird numbers 70, 836, 4030, 5830,
7192, 7912, 9272 (plus thousands of larger known ones) with correct
factorizations and δ values.

## Runs
- Run A (background): odd n < 10^21 — agreement check vs Fang's bound.
  Expectation: 0 finds. Any find here = pipeline bug OR refutation of Fang
  (either way we'd know the filter works by checking the witness by hand).

## Next
- If Run A is clean: scale to n ∈ (10^21, 10^24+], i.e. genuinely new
  territory, and consider C-ifying the DFS if node throughput is the
  bottleneck. Watch tested-candidate counts: the density of
  abundant-with-small-δ odd numbers above 10^21 is the unknown that decides
  feasibility.

## Completeness caveat (to state in any result writeup)
The DFS enumerates every odd n ≤ N_CAP reachable via viable branches; every
ancestor of an abundant node is explored (a deficient prefix of an abundant
n always passes the viability cap, since the true continuation exists).
BUT the δ-test only fires for δ < DELTA_MAX. So the search is COMPLETE for
odd n ≤ N_CAP with δ(n) < DELTA_MAX, and silent about any weird number with
δ ≥ DELTA_MAX. Known even weird numbers overwhelmingly have tiny δ, so the
δ-window is believed to be where the action is — but "no odd weird found"
must always be stated with the δ-window attached.

## Run A result (2026-07-24): PARTIAL agreement check, filter validated
- 61,761,000 DFS nodes in 1500s (Python), 263,768 abundant-with-small-δ
  candidates tested, **0 weird found**. Consistent with Fang's 10^21 bound.
- HONEST SCOPE: the run was time-limited, not space-complete — it did NOT
  enumerate all odd n ≤ 10^21 (DFS is ordered by factorization, not by n).
  What it proves: (a) the pipeline runs correctly at scale, (b) among the
  263,768 candidates in the covered prefix the filter never fired — no
  false positives, no surprises. The full below-10^21 agreement check needs
  the C engine to finish the tree.
- Production decision: C engine (delegated port) with N_CAP = 10^24,
  DELTA_MAX = 10^7, multi-hour budget. 10^21–10^24 is genuinely fresh
  territory (Fang stops at 10^21).

## C engine (2026-07-24): VALIDATED, optimization in progress
- Subagent-delivered C port passes the full gate: ALLOW_EVEN=1 N_CAP=1e6 →
  nodes=239,115, tested=234,355, weird=1765, identical to Python, including
  all 7 known weird < 10^4. (An early buggy binary showed 29 — stale-file
  race during the agent's own fix cycle; final binary is exact.)
- Validation methodology note: diffed found-lists at 1e5/2e5/5e5/1e6 — all
  identical. Trust but diff.
- Throughput at 1e21: ~81k nodes/s (only 2x Python) — bottleneck is
  next_prime inside k_max/p-loops. Requested: static prime table fast path
  + SPF sharding (smallest-prime-factor partition for parallel production
  runs). Agent still iterating.
