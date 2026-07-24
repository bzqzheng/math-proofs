# High-Leverage Targets — Erdős #313 / PPNs

Ranked by publishable value ÷ effort. Distilled from a multi-LLM literature audit
(Perplexity, Gemini, ChatGPT, Grok, Kimi, GLM, Claude) cross-checked against the repo.

## Session status (honest)
Frontier mapped; r=9 barrier **located and reduced** (not solved) to factoring
`f(q)=n²q²+q−n` over an interval. Σₖ heuristic is **critical (ratio ≈0.97±noise),
undetermined** — does not decide #313. No theorem claimed beyond that.

---

## Tier 1 — do first

### A. Uniqueness at ω = 9 (and 10)  ← TOP PRIORITY

#### Precise problem statements

Recall a **primary pseudoperfect number (PPN)** is a squarefree n > 1 with
`1/n + Σ_{p|n} 1/p = 1`. Let `ω(n)` = number of distinct prime factors.

**Main Theorem (target).** *N₉ is the unique PPN with ω(n) = 9.*
- N₉ = **5998279018951962402** = 2 · 3 · 11 · 17 · 101 · 157 · 1979 · 10093 · 16879  *(verified)*
- i.e. the claim is: if `1/n + Σ_{p|n} 1/p = 1` with `ω(n) = 9`, then `n = N₉`.

**Stretch Theorem.** *N₁₀ is the unique PPN with ω(n) = 10.*
- N₁₀ = N₉ · (N₉+1) = N₉ · 5998279018951962403 = **35979351189199316534587473905773572006** *(verified)*
- where p₁₀ = N₉+1 = 5998279018951962403 is prime.

**Hardness / why this is open.**
- Butske–Jaje–Mayernik (2000) proved uniqueness for every ω ≤ 8 (the field's canonical result).
- Wang (arXiv:2605.21518, 2026) proved *existence* at ω=9,10 but writes: *"no uniqueness
  theorem for the nine-prime-factor example is proved."*
- Sondow–MacMillan (arXiv:1812.06566) conjectured uniqueness at ω=9.
- Non-monotonicity: digits(N₉)=19 < digits(K₈)=31, so ω is **not** monotone in magnitude —
  classification must be by ω, not by a size bound B.

**Method of proof (finite computation).**
For each ω ∈ {9, (10)}: enumerate *all* depth-(ω−1) states (N, A) under Wang's port formalism,
apply the t=1/t=2/t≥3 terminal rules, and verify the only solution is N_ω. Engine
(`../problems/erdos-313/ppn.c`) already validated against BJM for ω≤8 and against Wang's N₉.

**Residual obstruction (the hard part — item #4, currently *reduced*, not solved).**
A single family of A=1 states (3-prime successors of a PPN n) blocks completion at ω=9.
Reduced to batch-factoring the quadratic **f(q) = n²q² + q − n** over an interval
(algebra verified). For n = 2214502422: ~10⁸ factorizations of 38-digit numbers; the
q₁ ∈ (2n,3n) half is feasible (hours), the q₁ ∈ (n,2n) half is the residual.
- **Closing this = the ω=9 theorem.**

**Scope warning.** Don't promise ω=10 unless the full depth-9 enumeration completes (much
larger than ω=9). Before writing "unique," verify the engine is exhaustive over *all*
ω-prime configurations, not just the pruned branches — this is the assumption a referee probes.

**Venue:** *Mathematics of Computation*. Extends BJM, fills Wang's stated gap, resolves
Sondow–MacMillan.

---

## Tier 2 — serious follow-ups

### B. Quantitative Bateman–Horn for the port hypersurfaces
- **Statement:** compute the singular series (local prime densities) + archimedean integral
  for Wang's `cx₁⋯x₅ − R·Σᵢ∏ⱼ₌ᵢ xⱼ = 1`.
- **Why:** Wang uses only the *existence* assertion and flags the asymptotic count as an
  unfilled hole. Doing it **replaces the fitted 1.3 widening factor with a derived constant**,
  converting ρ_eff from a fit into a prediction. This is the rigorous version of items 2–3.
- **Effort:** high (real analytic number theory, weeks–months).

### C. Negative result on Wang's 5-splitting hypothesis
- **Statement:** show standard Hardy–Littlewood heuristics do *not* support Hypothesis 19.2.
- **Why:** if ρ_eff < 1, the 5-splitting should fail; a negative BH result about a named
  hypothesis gets cited, and it's something Wang can't produce without undercutting his own
  conditional theorem.
- **Caveat:** adversarial vs. a living author's 2-month-old preprint; negative BH results
  are hard to certify. Attempt only after A.

---

## Tier 3 — low competition, well-defined

### D. Odd PPNs (genuinely untouched)
- **Contrast:** odd *perfect* numbers have a deep literature (Nielsen ω≥10, size >10^1500,
  congruence + smallest-prime-factor bounds). Odd *PPNs*: nothing beyond "none known."
- **Target:** first paper proving "any odd PPN has ≥ k prime factors and exceeds X."
  Search tooling transfers almost directly. The mod-4 argument *breaks* here — a hint about
  where structural obstructions live. Becomes the reference everyone cites.

### E. Counting function #{PPN ≤ x}
- No nontrivial upper bound exists in the literature. Even a weak explicit one is new.

### F. Formalization in Lean
- Erdős DB already carries a Lean statement of #313; Wang's certificates aren't deposited.
- A Lean-checked certificate for N₉, N₁₀, p₁₀ primality is tractable, unambiguous,
  adoptable. Unglamorous, near-certain to land.

---

## Decision log — batch-sieve for the ω=9 residual (2026-07-24)

**The residual, restated operationally.** The ω=9 sweep (`../problems/erdos-313/ppn.c`, k=9, sharded over
2,910 depth-5 prefixes) enumerates every branch but **defers** over-budget nodes. At the point of
this note: **2,482 / 2,910 shards done, 1,108,471 deferred nodes**, of which:
- ~1.10M are **routine** (`T2ITER`/`T2SPAN`): settle by factoring one ≤34-digit `N²+A`. Not a wall.
- **858 are `LOOP` nodes** — the wall. All are "does PPN `n` have a **3-prime successor**?", i.e.
  scan prime `q₁ ∈ (n, 3n)` and test whether `M(q₁) = n²q₁² + q₁ − n` (a fixed quadratic) splits
  into the two primes that complete a PPN. Hardest single node: `n = 2214502422`
  (`P=[2,3,11,23,31,47059]`), ~1.9×10⁸ prime `q₁`, each `M(q₁)` a 38-digit number.

**Why a batch-sieve, not per-`q₁` factoring.** All `M(q₁)` are values of *one* polynomial at
consecutive `q₁`. For each small prime `p`, the `q₁` with `p | M(q₁)` are the **roots of
`n²x²+x−n` mod p** — 0/1/2 arithmetic progressions — so trial division is **shared** across all
`q₁` in one strided pass per prime (classic line-sieve). Turns "1.9×10⁸ independent factorizations"
(weeks–months) into a sieve pass + real work only on survivors.

**Measured on the hardest node (small-window demo, `attempts` venv):**
- sieve to `B=2,000` → **13%** of prime-`q₁` survive as candidate 2-prime products;
- sieve to `B=100,000` → **24%** survive.
- ⚠️ Bigger `B` → **more** survivors, not fewer: the filter counts "reduces to prime×smooth", and
  more sieving *reveals* more such. So the sieve **sorts** work, it does not shrink the candidate
  pile to a sliver. Expect a ~20–25% survivor set needing targeted `divisor-in-range` checks
  (not full factorization — we only need a divisor of `M` in the valid range with the right
  congruence).

**Two halves (unchanged assessment).** `q₁ ∈ (2n,3n)`: the follow-on 2-prime step is small →
**feasible** (hours). `q₁ ∈ (n,2n)`: as `q₁→n⁺` the port residual `R₁=nq₁/(q₁−n)` blows up → the
2-prime step is huge and the sieve helps less → **genuine residual, may not close.**

**Proof logic for the theorem.** sweep (finish all 2,910 shards) **+** resolve all routine deferrals
(factor) **+** batch-sieve clears all 858 LOOP nodes ⟹ every depth-8 state checked ⟹ N₉ unique.
The sieve converts "deferred, looks unbounded" into "checked, empty" — the crux a referee probes.

**Highest-implications ranking (by axis, honest):**
- *Toward solving #313 (infinitude):* **B** — the only target that touches the conjecture (derives
  the widening constant, rigorous core of any conditional-infinitude claim). Hardest; may not close.
- *Citable theorem you can actually finish:* **A** (ω=9 uniqueness) — settles Sondow–MacMillan,
  fills Wang's gap; zero implication for infinitude.
- *Certainty of landing:* **F** (Lean certificates) — near-certain, low implication, no compute.

**Status of the sweep:** **terminated 2026-07-24** to free the machine (resumable via `k9/*.done`;
re-run `../problems/erdos-313/run_k9.sh`). For Target A the enumeration must eventually be *resumed and completed*
— stopping now is a pause, not an abandonment. For B or F the sweep is irrelevant.

**Open decision (awaiting Bright):** A (build the sieve) vs B (analytic, risky) vs F (safe small win).

## Do NOT do
- Package the six-item list (ρ, f(q), mod-4, completeness) as a standalone paper —
  locally correct, globally not a result. Use the pieces *inside* target A or B instead.
- Include any "LLM consensus matrix" or model component-scores in a submission — not
  independent verification, costs referee goodwill.
- Lead with the ρ_eff ≈ 0.96 heuristic — its punchline is "undetermined," which reads as
  an observation, not a theorem. Relegate to a labeled heuristic section or appendix.
