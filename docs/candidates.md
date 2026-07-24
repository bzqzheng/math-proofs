# Candidate Problems — Ranked by Gut Hunch (Kimi K3, 2026-07-24)

Method: full local corpus triage. Sources:
- `data/erdosproblems/` — Tao/Bloom community DB, 1217 problems, 652 attackable
  (open + decidable + verifiable + falsifiable), with prize/OEIS/Lean metadata.
- `data/formal-conjectures/` — DeepMind Lean formalizations (510 Erdős files).
- Each candidate scored against the P1–P5 solvability signature from analysis.md.

Key structural finding from triage: **most Erdős problems are infinitary**
(asymptotic bounds, limits, existence of infinite families) — no finite
witness settles them, so P1 fails and they're anti-targets. The signal in
the corpus is the DB's own classification: **43 problems are explicitly
tagged decidable (9), verifiable (7), or falsifiable (27)** — reducible to
finite computation. That sublist plus a handful of famous witness-hunts is
where the expected value lives.

---

## Tier 1 — pure witness hunts (one finite object settles a named question)

1. **Erdős #647 — divisor-function maxima (£25).** Find any n > 24 with
   max_{m<n} (m + τ(m)) ≤ n+2. A single integer is the entire proof, checked
   by `decide` in milliseconds (the Lean file does exactly this for n=24).
   Erdős thought infinitely many such n "extremely doubtful" — but the main
   question only asks for one. Search is trivially prunable (only m near n
   matter, τ(m) is small unless m is highly composite). **Top pick: cheapest
   oracle in the entire corpus, tagged "verifiable" by the DB itself.**

2. **Erdős #470(i) — odd weird numbers ($10).** Find one odd abundant
   number with no subset of proper divisors summing to itself. Known: none
   below 10^21; needs ≥ 6 distinct prime factors (Liddy–Riedl). Witness
   verifies in ms. Search must be constructive (build odd primitive abundant
   numbers with abundancy barely > 2, then test semiperfection) rather than
   brute force. Famous recreational problem; even pushing the 10^21 bound
   with a smarter sieve is a citable result. **Highest fame-per-effort.**

3. **Fortunate numbers conjecture (Erdős #779, falsifiable).** Fortune's
   conjecture: every Fortunate number (smallest m > 1 such that
   primorial p_n# + m is prime) is itself prime. One composite Fortunate
   number kills it. Oracle = primality testing of moderate integers.
   Verified far already, so a counterexample would be a genuine surprise —
   but the falsifiability tag means the community believes computation
   decides it.

4. **Erdős #1052 — sixth unitary perfect number ($10).** Only five known
   (largest ~1.46·10^23). A new one is a famous witness; finiteness itself
   is infinitary and off-limits. Same shape as #470 but worse search
   structure.

5. **Hadwiger–Nelson: a 6-chromatic finite unit-distance graph.** (Not in
   the DB; plane χ is 5–7 since de Grey 2018.) One graph = one of the most
   famous witnesses in combinatorial geometry. Oracle = SAT coloring check.
   Enormous search space; needs LLM-guided symmetry/structure guessing plus
   SAT filtering. Highest payoff on this list, lowest probability.

6. **3×3 magic square of nine distinct perfect squares.** (Not in the DB;
   famous open problem, LaBar/Robertson.) One square settles it. Parametric
   search spaces (magic square = arithmetic structure on 9 entries) are
   LLM-navigable; oracle is a 9-number check. Recreational but
   headline-level.

7. **R(5,5) ≥ 44 via explicit graph** (DB-adjacent, Ramsey cluster
   #77/#165/#183 are infinitary, but small-number lower bounds are witness
   problems). Current R(5,5) bounds 43–48 (as of my knowledge). A
   K5-free/5-independent-set-free graph on 43+ vertices is a checkable
   witness and would be front-page in combinatorics. SAT/local-search with
   LLM-proposed Cayley/paley-type symmetries.

## Tier 2 — DB-tagged finite-computation targets (43 problems)

Full list extracted to `data/finite_computation_targets.txt`. Most promising
subset (cheap oracle + clear statement + prize):

- **#7 (covering systems, verifiable)** and **#307, #242, #287 (unit
  fractions)** — Egyptian-fraction problems with enumerable witnesses.
- **#364/#366 (OEIS A060355-linked, verifiable).**
- **#398 (factorials), #458 (primes, A056604), #699 (binomial
  coefficients)** — number-theoretic falsifiables with direct oracles.
- **#64 ($1000, graph cycles, falsifiable)**, **#107 ($500, convex
  geometry)**, **#97 ($100, convex distances)** — prize falsifiables.
- **#982 (convex distances, A004526)** — computable geometry.

## Tier 3 — proof-fishing, not witness-hunting

- **Primitive-set corollaries of the fresh von Mangoldt chain machinery**
  (#1196/#1217/#164 fell in 2026; adjacent open primitive-set problems,
  Banks–Martin variants, #143-type density questions). New hammers seek
  nails; the tool's creators can't have exhausted the corollaries.
- **OEIS conjecture batch** — volume play from analysis.md; reconstruct via
  OEIS API query for "conjecture" entries, WZ/induction as oracle.
- **#138 variants: van der Waerden number lower bounds** — W(r,k) lower
  bounds are coloring certificates (SAT-checkable). One variant already fell
  to a DeepMind prover agent, proving the area is live for AI methods.

## Anti-targets (P1 fails — do not touch)

#3/#142 ($5k/$10k arithmetic-progressions conjectures — deep analytic
number theory), #30/#39/#41 (Sidon/B₃ asymptotics), #77/#165/#183 (Ramsey
limits/constants), #89 (distinct distances — post-Guth–Katz incremental),
#20 (sunflower conjecture — post-ALWZ), #1135 (Collatz), #687 (Jacobsthal
function bounds), #1 (sum-distinct constant). All infinitary; any
"progress" here without a new theory is noise.

## What I still need from you (the one fetch worth doing)

I already have the canonical corpus locally — a generic problem list adds
nothing. The one thing I cannot reconstruct reliably is **the exact set
already solved by AI**, so we don't burn effort duplicating AlphaProof
Nexus's 9 Erdős + 44 OEIS wins. If you want to run one Deep Research query,
use this:

> "List the specific Erdős problems (by erdosproblems.com number) that
> DeepMind's AlphaProof Nexus proved in its 2026 batch run (9 of 353), and
> the specific OEIS sequences (by A-number) whose conjectures it resolved
> (44 of 492). For each, give the exact statement and whether the proof is
> public. Also list all Erdős problems solved with AI assistance in
> 2025–2026 per Terence Tao's tracking (teorth/erdosproblems wiki
> 'AI-contributions-to-Erdős-problems')."

Meanwhile I can start on Tier 1 items 1–2 (#647, #470) immediately — both
need only this repo, the venv, and CPU time.

## Update (2026-07-24): OEIS volume play DEPRIORITIZED
- OEIS search API is Cloudflare-walled (403 + JS challenge for both FetchURL
  and curl); the wiki's conjecture index is a dated (2008) thin seed.
- Spot-check of the "conjectured formulas" seeds (A005158/A005160 family):
  these are deep algebraic-combinatorics conjectures (ASM/Stanley baker's
  dozen), NOT induction-on-computable-terms — poor fit for our oracle-first
  method anyway.
- The Erdős DB pipeline (652 attackable, 43 finite-computation tags) is a
  strictly richer corpus. OEIS batch hunt deferred unless the user-side
  Deep Research fetch (prompt above) delivers the exact 492-list.
