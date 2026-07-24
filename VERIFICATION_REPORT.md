# Offline Verification Report — Do I Agree With the Source Report?

Date: 2026-07-24. All checks below ran locally (SymPy/NumPy, no network).
Scripts and raw outputs are in `verification/`.

## Verdict table

| # | Claim in report | What I could check offline | Result | Agree? |
|---|---|---|---|---|
| 1 | Jacobian conjecture false in dim 3 (Alpöge + Fable 5) | **Everything.** det(JF) ≡ −2 and the 3-to-1 collision at (−1/4,0,0) are pure polynomial arithmetic | Both properties confirmed exactly by SymPy | **Yes, fully** |
| 2 | Erdős #164 / primitive-set conjectures proved via von Mangoldt chains | The *statement* of #164 on all small cases; the size of the prime bound | Exhaustive over **all 163,368 primitive subsets of {2..26}**: max of Σ 1/(a·log a) = 1.3428472749, attained *exactly* at the primes. Prime sum to 2·10⁶ = 1.5677, below and approaching the known constant ≈1.6366 | **Yes for the theorem statement**; the *proof itself* (chain method) I cannot re-derive offline |
| 3 | Unit-distance conjecture disproved, u(n) ≥ n^1.014 | The classical baseline the construction must beat | Direct enumeration on grids up to 150×150 (22,500 pts, ~2.5·10⁸ pairs): most popular distance always occurs more than n times; exponent log u/log n ≈ 1.25 and *drifting down toward 1*, consistent with the classical n^(1+c/log log n) law | **Yes for the framing/baseline**; the n^1.014 construction itself is **not verifiable offline** (existence proof needs infinite class field towers — no enumerable witness) |
| 4 | Ran–Teng spectral conjecture proved | Nothing — the report never states the conjecture precisely | — | **Cannot judge** from the report alone |
| 5 | AlphaProof Nexus: 9/353 Erdős + 44/492 OEIS | Nothing — no individual statements or proofs given | — | **Cannot judge**; single thin source, treat as unconfirmed |

## Key observations

**The Jacobian case is the gold standard for "AI did math": the witness is
the proof.** Two lines of SymPy settle an 87-year-old conjecture. There is
no trust component at all — I don't need to believe Alpöge, Anthropic, or
the report; the object certifies itself. This is P1 (verification
asymmetry) in its purest form.

**The primitive-set check is a nice demonstration of what "verification"
means for a *proof* (as opposed to a counterexample).** I cannot verify the
von Mangoldt chain argument line-by-line offline. But the theorem it proves
makes infinitely many finite predictions, and the hardest of them — "the
max over ALL primitive sets is attained at the primes" — I confirmed
exhaustively, not by sampling: 163,368 out of 163,368 primitive subsets of
{2..26} obey the bound, with equality only for the primes. A proof whose
every checkable consequence checks out earns agreement-with-the-statement,
not agreement-with-the-proof. The distinction matters and I've kept it.

**The unit-distance result is the one case where offline verification is
structurally impossible** — and that's diagnostic. The construction's
existence relies on Golod–Shafarevich / class-field-tower machinery; there
is no small certificate to enumerate. This is why that result needed nine
human mathematicians to extract and check, while the Jacobian result needed
a tweet. Not all LLM-solved problems have equal verification asymmetry.

**What the baseline computation adds:** my grid enumeration shows the
classical exponent at ~1.25 for small n, decaying toward 1 like
1 + c/log log n (effective c rising through 0.48→0.57 across my range,
consistent with slow convergence). The AI's claimed n^1.014 is *weaker* than
the grid at laptop scale but *stronger* asymptotically — exactly the regime
where humans rarely look and where algebraic structure (many norm-1
differences in rich number fields) pays off. The report's story is
quantitatively coherent with everything I can compute.

## Bottom line

I agree with the report's two flagship claims: one because I verified the
entire mathematical content myself (Jacobian), one because the framing and
baseline check out and the construction, while unverifiable here, has
independent expert confirmation (unit-distance). The primitive-set theorem
statement agrees with exhaustive finite evidence. The Ran–Teng and
AlphaProof-batch items carry no verifiable content in the report and remain
unconfirmed from my seat.
