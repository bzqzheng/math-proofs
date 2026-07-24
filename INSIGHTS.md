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
