# INSIGHTS — compounding, problem-generic lessons

Insights here must be generic (applicable beyond the problem where found).
High signal, low noise. Newest first.

---

## I1. Reduce the oracle's target, not the search space
Found in: #470 (weird numbers).
The semiperfectness test looked infeasible (subset-sum target n ~ 10^21),
but complementation moved the target to δ = σ(n) − 2n, which is *small by
construction of the search*. General pattern: when a property P(x) is a
statement about a huge object x, look for a complement/dual formulation
whose witness lives at the scale of a controllable parameter. Other uses:
witness-set minimization in covering problems, certificate compression in
SAT-adjacent searches. **Whenever an oracle is too slow, ask: is there a
dual quantity that is small exactly where I choose to look?**

## I2. Calibrate against OEIS + recent preprints BEFORE any computation
Found in: #647. A 2-minute OEIS fetch (A087280) revealed someone had
verified the conjecture to 10^12 in June 2026 — saving days of redundant
compute. General pattern: for any computational attack on a named problem,
the first move is fetching the relevant OEIS entry's COMMENTS/EXTENSIONS
and searching for preprints from the last 24 months. The frontier moves
monthly now. **Never compute below the published frontier; compute is only
worth spending above it.**

## I3. Monotonicity of the certificate size gives free pruning
Found in: #470. δ = σ(n) − 2n is monotone increasing along any factorization
extension once abundant (both factors of (abundancy−2)·n grow). This turned
an infinite search tree into a pruneable DFS. General pattern: when
searching multiplicative/ compositional spaces (factorizations, set
systems, graph extensions), find a certificate-relevant quantity that is
monotone along the extension order; it converts "search everywhere" into
branch-and-bound.

## I4. "Verifiable/falsifiable by finite computation" tags are the
##    highest-signal filter in any problem corpus
Found in: corpus triage. The Erdős DB's own classification (decidable/
verifiable/falsifiable) outperformed my P1–P5 scoring in precision. General
pattern: when attacking a curated corpus, exploit the curators' metadata
before inventing your own triage. **Read the schema before the problems.**

## I12. Derive prunes from the reachability algebra, not from intuition —
##     and test them on a case where the answer is known
Found in: #287 (MITM vs old DFS). The old backtracker pruned with the
inequality BACKWARDS: it cut branches whose partial sum + MAXIMUM remaining
sum exceeded 1 (killing valid tuples like 2,3,6 for k=3) and never cut
branches that couldn't reach 1 (the actually useful direction). It only
avoided lying by luck (it found solutions inside its wrongly-restricted
subset for every k it reported). The MITM prune — cut when
partial + maxRemaining < 1, with a float epsilon and monotone-safety
checked — turned days-at-k=22 into 0.1 s for all k ≤ 21. General pattern:
for every prune, write down (a) the exact reachability inequality that
makes the cut valid, (b) whether the bound is monotone-safe along children,
(c) a known-positive case the pipeline MUST still find. A prune you can't
justify from the algebra is a bug you haven't caught yet.

## I11. When the natural split axis degenerates, split on a bounded
##     dimension instead
Found in: #470 (monster P2=5·P3=7, ~1T nodes). Splitting it by the fourth
prime produced a viable set of 82,697 values at 10⁹ — the deficient-branch
viability condition degenerates once the prefix itself can be abundant
(abundancy already > 2, so every large prime "could" still lead somewhere).
The root prime's EXPONENT, by contrast, is always finite and small
(a ≤ log_SPF(N_CAP): 50 values at 10²⁴), and the union is trivially
complete — no viability argument needed. General pattern: before building
sharding machinery, check the split axis is (a) finite and (b) small at the
PRODUCTION cap (I9 applies here too); an axis that explodes with the cap
means you're on the wrong dimension. **Split on what is bounded, not on
what is natural.**

## I10. Calibration theorems about the witness are prune conditions —
##     push them into the search
Found in: #470 (MIN_DEPTH patch). Liddy–Riedl ("odd weird ⇒ ≥ 6 distinct
prime factors") sat in the problem README as a calibration fact while the
DFS burned 450B nodes on branches that could never host a witness. One
env-gated condition (`depth + k_max(n, p_start) < 6 → cut`) made two
unbounded shards bounded. General pattern: after calibrating (I2), list
every known necessary condition on the WITNESS — depth, size, residues,
parity, forbidden substructures — and check each against the search code:
is it (a) already implied by construction, (b) testable per-node as a
prune, or (c) silently violated by parts of the tree? (b) is almost always
cheap to add and env-gate; re-run both oracle gates after adding it.
**A theorem you cite but don't search with is a prune you haven't shipped.**

## I9. Shard weights measured at a small size cap do not extrapolate to a
##    large cap — profile mass by depth, not just by shard
Found in: #470 (P2 sub-shards). At N_CAP=10⁹ the P2∈{11,13} sub-shards
finished in <1 s (≤1.5k nodes, looked like rounding errors next to P2=5);
the same sub-shards at N_CAP=10²⁴ held 37B nodes EACH and blew a 1 h budget.
The tree's mass sits at depths that don't exist under the small cap:
exponent ranges and branching budgets both grow with log(N_CAP), so a shard
that is empty at depth d says nothing about depth d+10. General pattern:
when profiling sharded searches whose depth budget scales with the instance
cap, either profile at a cap within ~2 orders of magnitude of production,
or instrument mass-by-depth at the small cap and check whether mass is still
increasing at the deepest level reached. **Never size production budgets
from small-cap shard weights alone.**

## I8. Measure candidate density per shard EARLY; shard workloads are never
##    balanced by symmetry
Found in: #470 production. After SPF-partitioning the search, shard SPF=3
held ~all 259k candidates (2.6% of nodes), while SPF=5 burned 580M nodes
with zero candidates — same code, 100x density difference. The symmetric
partition (by smallest prime factor) was anything but symmetric in value.
General pattern: after launching any sharded search, read the first
progress reports before walking away: candidate density per shard tells you
where the tree's mass is, whether some shards are pure due-diligence (keep,
but at low priority/budget), and whether the "main" shard needs further
splitting. **The first 100 progress lines are the cheapest profiling you
will ever do.**

## I7. Extra quantified variables often drop out after the right
##    characterization — check before pricing the search (but verify the drop-out)
Found in: #699 (binomial gcd). For composite `i`, the conjecture quantifies
over `(n, i, j)`, but the Legendre-digit-sum characterization of `p | C(n,i)`
for `p > i` reduces the *existence* of a large prime factor of `C(n,i)` to a
predicate on `(n, i)` alone. Composite `i` is then settled by Sylvester–Schur.
For prime `i`, the same predicate is necessary but not sufficient: `p = i` may
divide the numerator of `C(n,i)` but be canceled by `i!`, and even when a
large prime divides `C(n,i)` it may not divide a particular `C(n,j)`. The
remaining live case is a prime-factor-survival problem over `j`. General
pattern: before estimating a witness search's cost, push each atomic predicate
through the strongest known characterization — but then stress-test the
characterized predicate against the *full* statement on small cases to catch
exactly this kind of cancellation. **Never price a search on the statement's
arity; price it on the verified characterized predicate's arity.**

## I6. Cap the branching factor with a necessary condition from the goal
##    inequality — not just the state space
Found in: #470 (v1 runaway). The DFS iterated the "next prime" loop over all
primes up to N_CAP/n (~10^21 at the root) because the size cap is not the
real constraint — the *goal inequality* is. Deriving "choosing p can reach
abundancy 2 only if A·(p/(p−1))^(k+1) > 2" collapsed the root branching from
10^21 to ~8. General pattern: in any DFS/BFS over combinatorial objects,
bound the branch variable by the *viability of ever satisfying the target
predicate*, not by the container size. An unbounded loop over a legal-but-
doomed range is the most common silent way search code "runs forever."
Related: log with flushed progress from minute one — an empty log after 10
minutes IS the bug report.

## I5. Validate pipelines on known-positive and known-negative cases
Found in: #470. The DFS+δ-test was validated by (a) reproducing all 7 known
weird numbers < 10^4 with correct δ, (b) running below Fang's 10^21 bound
expecting zero finds. General pattern: any search pipeline gets two gates —
must-find-known-witnesses and must-not-find-below-frontier — before any
frontier compute. A pipeline that fails gate (b) is lying, and gate (b) is
the one most people skip.
