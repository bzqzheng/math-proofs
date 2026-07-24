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
(`attempts/ppn.c`) already validated against BJM for ω≤8 and against Wang's N₉.

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

## Do NOT do
- Package the six-item list (ρ, f(q), mod-4, completeness) as a standalone paper —
  locally correct, globally not a result. Use the pieces *inside* target A or B instead.
- Include any "LLM consensus matrix" or model component-scores in a submission — not
  independent verification, costs referee goodwill.
- Lead with the ρ_eff ≈ 0.96 heuristic — its punchline is "undetermined," which reads as
  an observation, not a theorem. Relegate to a labeled heuristic section or appendix.
