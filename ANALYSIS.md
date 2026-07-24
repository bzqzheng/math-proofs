# Analysis: What LLMs Are Actually Good At in Math, and Where to Strike Next

Author: Kimi (K3-class reasoning model), 2026-07-24
Source material: `llm-solved-problems-2026.md` (Perplexity report, July 2026)

---

## 1. Fact-check of the source report

The report's two most extraordinary claims check out against independent
coverage:

- **Erdős unit-distance conjecture disproved by an OpenAI internal model**
  (announced 2026-05-20). Confirmed by OpenAI's own writeup and widespread
  secondary coverage. The model produced point sets with ~n^1.014 unit
  distances, beating the n^(1+c/log log n) grid construction, using class
  field towers / Golod–Shafarevich theory. Nine mathematicians extracted and
  published a human-checked version.
- **Jacobian conjecture falsified in dimension 3** by Levent Alpöge with
  Claude Fable 5 (posted 2026-07-20). **I independently re-verified the
  counterexample myself** with SymPy (see
  `verification/verify_jacobian_counterexample.py`):
  - det(JF) ≡ -2 for the posted map F: C³ → C³ ✓
  - F(0,0,-1/4) = F(1,-3/2,13/2) = F(-1,3/2,13/2) = (-1/4,0,0) ✓
  - The map is therefore locally invertible everywhere but 3-to-1 at one
    point. An 87-year-old conjecture is dead, and the witness fits in a
    tweet.

Caveats on the rest: the "GPT-5.4 Pro → von Mangoldt chain" Erdős #1196
story is consistent with Tao's tracked Erdős-problem progress; the
"AlphaProof Nexus: 9/353 Erdős + 44/492 OEIS" batch claims come from a
single consulting-firm summary and should be treated as
plausible-but-thinly-sourced. The direction of the trend is not in doubt.

---

## 2. The hidden common properties — the "LLM-solvability signature"

Looking across every success in the report, the solved problems share a
remarkably consistent fingerprint. None of them fell to a model that "just
reasoned harder." They fell because of *structure*:

**P1. Verification asymmetry (the master property).**
Every solved case has a solution whose *checking* is cheap, mechanical, and
fast relative to the search: a polynomial map (SymPy/Lean, seconds), a point
configuration (count pairs), a number-theoretic inequality (evaluate on
primes), a recurrence identity (creative telescoping / induction). The model
never needed to produce a trustworthy proof in prose — it needed to produce
a *candidate object* that a deterministic oracle could certify. This is the
same reason SAT-solving and program synthesis work: generation is hard,
verification is easy, and LLMs are generative search engines.

**P2. The bottleneck was search, not depth.**
These problems were open for 60–87 years not because they required a new
field of mathematics, but because nobody stumbled onto the right object or
combination. The Jacobian witness is 216 characters. The unit-distance
breakthrough was "use richer number fields," not a new theory. Erdős
problems keep falling to "overlooked lemma + recombination." LLMs hold far
more of the literature in context than any human and recombinate freely.

**P3. Clean, formal, self-contained statements.**
Combinatorics, discrete geometry, polynomial algebra, elementary number
theory. No problem requiring a decade of prerequisites (moduli spaces,
derived categories, p-adic Hodge theory) has fallen. The Erdős Problems
database and OEIS are *curated corpora of formally-stated problems* — that
curation is itself an enabler.

**P4. Rich algebraic/symmetric structure to extrapolate.**
LLMs are pattern-completion machines; problems whose solutions live in
parametric families with symmetry (number fields with class towers,
symmetric polynomial maps, Markov chains on divisibility posets) let the
model extrapolate small cases into general constructions.

**P5. A tight generate–verify loop existed.**
In every success story there was a fast oracle in the loop: SymPy, Lean, a
CAS, a brute-force checker, or a human expert giving next-day feedback over
multiple sessions (Ran–Teng: 4 drafts / 7 sessions). Lone-shot generation
produced nothing on this list.

**P6. Batch economics.**
9/353 and 44/492 are ~2.5% and ~9% hit rates. LLMs are not magic; they are
*high-throughput triage + proof search*. The unit economics only make sense
against large, triaged problem lists — which is exactly why a systematic
hunt beats poking at famous singleton conjectures.

**Contrapositive — what has NOT fallen, and why:**
RH, P≠NP, Navier–Stokes, Collatz, twin primes: no small witness exists (or
none is known to exist), verification of a candidate is as hard as the
problem, and the proof would need long chains of unverifiable-until-complete
novel theory. P1 fails, so the whole approach fails.

---

## 3. Ranked candidates: unsolved problems this setup can plausibly attack

Ranking = (significance × tractability under P1–P6), given my actual
capabilities: K3-class reasoning, this repo, Python/SymPy, and the ability
to install Lean/SAT tooling later. Honest prior: the probability that any
single attempt resolves a named conjecture is low; the *expected value* of a
systematic, witness-first batch hunt is real (P6).

### Tier 1 — best expected value

1. **Remaining OEIS conjectures (~448 of the original 492).**
   Closed forms, recurrences, congruences for specific sequences. Every
   candidate is verifiable: compute terms, test induction, apply
   Wilf–Zeilberger creative telescoping for hypergeometric identities.
   Significance: modest per item, but real citations and the highest hit
   rate of any target class. This is the volume play.

2. **Erdős Problems database — construction/counterexample-flavored entries
   (~330 still open).** Filter for problems where a solution would be a
   finite or parametric witness (extremal set systems, sumset constructions,
   primitive-set variants adjacent to the just-solved #1196/#1217/#164
   cluster — the von Mangoldt chain machinery is fresh and likely has
   low-hanging corollaries). Significance: high per item (Tao-tracked,
   community-noticed). Tractability: medium.

3. **Witness-based lower bounds in small Ramsey / extremal graph theory.**
   Improved lower bounds for small off-diagonal Ramsey numbers or Folkman
   numbers = exhibit one graph with the right properties. Verification is a
   brute-force check; search can be LLM-guided symmetry guessing + SAT
   filtering. The 2024 R(4,t) breakthrough (Campos–Griffiths–Morris–
   Sahasrabudhe) shows the area is moving. Significance: high. Tractability:
   medium — the search spaces are brutal, which is exactly why a guided
   search with a cheap oracle is the right shape.

### Tier 2 — high significance, harder

4. **Hadwiger–Nelson: chromatic number of the plane ≥ 6?**
   Current state: 5 ≤ χ ≤ 7 (de Grey 2018). A 6-chromatic finite
   unit-distance graph would be a famous finite witness, verifiable by
   enumeration. Known minimal examples have hundreds-to-thousands of
   vertices; the search is enormous but the oracle is trivial. This is the
   highest-payoff pure witness-search problem on the board.

5. **Union-closed sets conjecture (Frankl) — counterexample hunt.**
   Any counterexample is a finite family of finite sets: perfectly
   checkable. Gilmer's 2022 constant-bound progress suggests the conjecture
   may be true, but the *search* for extremal families (small universe,
   minimizing max element frequency) is exactly P1-shaped and would produce
   publishable bounds either way.

6. **Apéry-style binomial-sum / irrationality identities.**
   LLM proposes candidate identities from experimental mathematics (PSLQ on
   computed values), WZ-method certifies them. Moderate significance,
   genuinely automatable end-to-end in this repo.

### Tier 3 — explicitly avoided

- RH, P≠NP, Navier–Stokes, Collatz, twin primes, Goldbach: P1 fails. No
  witness asymmetry. Any claimed "proof" from a chat model is crank output
  until formally verified end-to-end.
- Jacobian conjecture in n=2: now the sole surviving dimension and the
  hardest case (counterexample search just failed in n=3, which if anything
  weakens the heuristic case for n=2 — but the automorphism-group structure
  in 2D is far more rigid; counterexample search here is a lottery ticket,
  not a program).
- Anything where verification itself requires novel theory.

---

## 4. Working method for this repo

1. **Oracle first.** No candidate counts unless a deterministic checker
   (SymPy, custom enumerator, SAT solver, or Lean) certifies it. The
   Jacobian verification script in `verification/` is the template.
2. **Batch triage.** Pull formal problem lists (Erdős DB, OEIS), score each
   against P1–P5, attack the top decile only.
3. **Generate → verify → log.** Every attempt, positive or negative, gets
   committed here with the checker output. Negative results prune the
   search tree and are the difference between research and astrology.
4. **Honesty invariant.** A "solution" without a passing checker is a
   hypothesis, and gets labeled as such.

## 5. Status log

- 2026-07-24: Repo created. Source report imported. Jacobian counterexample
  independently re-verified (SymPy): det ≡ -2, 3-to-1 collision confirmed.
  Analysis + ranked target list written.
- 2026-07-24: Full offline verification pass (see VERIFICATION_REPORT.md).
  Jacobian: fully confirmed. Erdős #164: statement confirmed exhaustively on
  all 163,368 primitive subsets of {2..26} (max attained exactly at primes).
  Unit-distance: classical n^(1+c/log log n) baseline confirmed by direct
  enumeration; n^1.014 construction not offline-verifiable (class field
  towers). Ran–Teng and AlphaProof batch claims: no verifiable content in
  the report; unconfirmed.
- 2026-07-24 (continued): First-iteration candidate campaign launched.
  * Erdős #699 (binomial gcd): reduction corrected — composite `i` is closed
    by Sylvester–Schur; prime `i` reduces to a prime-factor survival problem.
    Direct Lucas survival check verified `n ≤ 3,000` with zero counterexamples.
    Production scan to `n = 10^9` ongoing (now at ~475M).
  * Erdős #470 (odd weird numbers): compiled C search sharded by smallest
    prime factor to `10^24`; SPF=5..53 shards completed with zero finds;
    SPF=3 shard is the dense one, ~104B nodes/12ks elapsed, 262k candidates
    tested, zero weird finds (consistent with known frontier).
  * Erdős #779 (Fortunate numbers): gmpy2 `next_prime` optimization; scan hit
    1-hour budget at `n = 780`, no composite Fortunate numbers.
  * Erdős #458 (lcm inequality): scan to `k = 10^7` completed in 125 s; zero
    counterexamples, min margin 0.15415 at `k = 4`.
  * Erdős #64 (graph cycles): nauty installed; brute-force cubic/min-degree-3
    enumeration explodes well below the 30-vertex cubic lower bound, so a
    counterexample hunt here requires a structural construction, not raw
    enumeration.
  * Erdős #993 (tree independence-polynomial unimodality): extensively
    searched and deprioritized.  Reproduced the n=26 non-log-concave seeds;
    SA on general trees reached 0.962; deterministic scans of Kadrawi–Levit
    families, pure spiders, and pure star-arms found no counterexample;
    caterpillar SA reached a record near-miss ratio 0.995652 at n=463.
    Literature calibration (Reynolds Zenodo v3, March 2026) shows the
    conjecture is open, verified to n=29, and the known non-log-concave
    "bush" families have been pushed to 60 vertices without producing a
    non-unimodal tree.  Marginal return on further local search is low.
  * Erdős #287 (Egyptian-fraction gap problem): started.  Searched for a
    representation 1 = sum_{i=1}^k 1/n_i with 1<n_1<...<n_k and all gaps
    n_{i+1}-n_i ≤ 2; no counterexample for k ≤ 21 (search timed out at k=22).
