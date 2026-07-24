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

## Production launch (2026-07-24): sharded above-10^21 search at N_CAP=10^24
- C engine: validation gate passed bit-for-bit (agent report + my re-check).
  ~137k nodes/s production shape (~8x Python).
- SPF sharding added (patched main myself): SPF=p covers exactly
  factorizations with smallest prime factor p; union over p = complete.
  Gates: unsharded 1765 ✓; SPF=2 finds all 1765 below 1e6 ✓; SPF=3 finds 0 ✓.
- Launched: shard SPF=3 (dominant, 6h budget) + SPF=5..53 (sequential
  runner). Coverage: fresh territory 10^21–10^24 with δ < 10^7.
  NOTE: N_CAP=1e24 parses via float to 999999999999999983222784 (same quirk
  as Python reference — documented in the C header).
- OEIS corpus agent failed (provider quota 403) — deferred; may retry
  inline or when quota refreshes.

## Candidate density decays with n (production data)
SPF=3 shard: tested=261,934 by 2.35B nodes (n ≲ 10^21) but only 262,086 by
7.57B nodes (n ~ 7·10^23). Tuning abundancy into the δ < 10^7 window gets
harder as n grows — consistent with the fine-tuning analysis (δ/n must fall
below 10^7/n). Implication: the marginal value of pushing N_CAP far beyond
10^24 drops fast; 10^24 is a sensible iteration-1 ceiling.

## Magic square of squares (Tier-1 #6): CALIBRATED, DEPRIORITIZED
A 3x3 magic square has parametric form center c, entries c±a, c±b,
c±a∓b, c±b∓a — requiring all 8 offsets to be perfect squares is a system
of simultaneous quadratic conditions. Three squares in AP with middle c
is already a congruent-number/elliptic-curve condition; requiring it in
rows+columns+diagonals simultaneously is a stack of elliptic rational-point
conditions. Decades of elliptic-informed search (Bremner, Robertson) have
found 6-of-9 and 7-of-9 solutions but no 9-of-9. There is no cheap
oracle-shaped search lane distinct from the published one — the witnesses
live on curves, not in enumerable space. Skip unless we bring elliptic
machinery (rank/height searches) to bear; that is a different toolchain
than this repo's.
