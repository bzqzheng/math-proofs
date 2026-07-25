# Strategy Note — Designing a Theorem/Counterexample Factory

Date: 2026-07-25. Distillation of a long strategy discussion on whether the
campaign's process model ("map a niche as a tree → look for cross-pollination
→ systematically produce theorems") matches how math actually gets made, and
what to build instead.

This is a *process* note, not a math result. It sits alongside
`docs/insights.md` (which captures generic tactical lessons) and
`docs/candidates.md` (which ranks targets). The aim is to make the campaign's
own production method explicit so it can be improved on purpose rather than
by accident.

---

## 1. The two factories

There are two structurally different "math factories" and the campaign has
been quietly running both without distinguishing them. Naming them is the
first fix.

### Factory A — the witness factory (default)

- **Inputs:** open problems whose statement is a *finite, cheaply checkable*
  claim about some object. Concretely: "find n with property P," "find a
  graph G with χ(G) ≥ 6," "is there a counterexample below N?"
- **Method:** LLM proposes candidate objects; deterministic code verifies;
  keep survivors. The LLM is a high-throughput combinatorial search partner;
  a mechanical oracle (SymPy, a SAT solver, a primality test, a `decide`
  tactic) is the filter.
- **Outputs:** counterexamples, bound extensions (negative results), finite
  classification / uniqueness theorems, explicit constructions.
- **What it does NOT produce:** deep structural theorems that require
  multi-field synthesis. And that's fine — it doesn't need to.
- **Who can run it:** someone who does not understand the math, *provided*
  they can pick the right problems and read the oracle's verdict honestly.
- **Repository examples that fit:** Jacobian verification (the original
  inspiration — two lines of SymPy), #470 odd-weird witness hunt, #313
  Target A (ω=9 PPN uniqueness, finite computation), #647 (single integer =
  entire proof), #458 / #779 / #699 bound-extension scans.

### Factory B — the cross-pollination factory (conditional, not default)

- **Inputs:** operational fluency in two fields, plus an open problem in one
  of them.
- **Method:** spot that a tool from field B resolves a problem in field A.
  Output is a *proof*, not a witness.
- **Outputs:** high-implication structural theorems (FLT, Poincaré, the
  von-Mangoldt-chain primitive-set theorems of 2026).
- **What it requires:** someone who can audit the LLM's mathematical moves
  for legality — not just plausibility. An LLM alone will confidently produce
  illegal moves that look like theorems.
- **Who can run it:** a human mathematician, or an LLM pipeline whose every
  step collapses back into a checkable finite computation (i.e. secretly
  Factory A wearing a costume).
- **Repository examples that fit:** the #313 ρ → log 2 branching heuristic
  (Mertens-meets-PPN-trees). **And this is exactly the cautionary tale**:
  the framing is novel, the constant log 2 is genuinely Mertens-derived, but
  the "therefore finiteness" step is a *heuristic that reads like a theorem*.
  That is the signature of Factory B attempted without an audit layer.

### The decision

**Factory A is the default. Factory B only runs when an audit layer is
present.** The campaign has been behaving as if B were the default and A
were the fallback; the repo's own evidence (Section 3 below) says this is
inverted.

---

## 2. Honest critique of the original process model

Original model: *pick a niche → map it as a tree → find cross-pollination →
systematically produce theorems.*

**What's right.**
- Tree-mapping is real and necessary. Every grad student does it in year
  one; every survey paper is one. The 652-problem triage in `candidates.md`
  is legitimate lineage work.
- Cross-pollination is one of the highest-leverage moves in mathematics
  (Wiles: elliptic curves + modular forms; Poincaré: Ricci flow into
  topology; the Jacobian counterexample: class field towers into polynomial
  maps). The instinct is correct.

**What's incomplete (and this is the load-bearing part).**

1. *The map is the floor, not the strategy.* Tree-mapping is the easy 10%.
   Anyone can read surveys. The thing that separates productive
   mathematicians from well-read ones is *taste*: knowing which gaps are
   tractable vs deep vs dead vs already-attacked. There is no shortcut;
   ~10 years of immersion. A map cannot substitute for taste — but a
   frontier-check gate (Section 4) can catch the most expensive taste
   failures.

2. *Cross-pollination needs fluency in both fields, not a map of both.*
   Wiles could import modular forms into elliptic curves because he could
   *compute* in both. An LLM with field B's literature in context is closer
   to a tourist than a translator. Without an audit layer, cross-pollination
   attempts produce confident illegal moves.

3. *Math is a dense graph, not a tree.* Systematic tree-walking finds the
   obvious gaps. The valuable gaps live at non-obvious graph distances and
   are found opportunistically, not by sweeping.

4. *"Systematically produce theorems" doesn't match how math gets made.*
   Read how productive mathematicians actually describe it: Poincaré/Hadamard
   on incubation-then-illumination; Tao's blog ("work on whatever excites me
   and seems tractable"); Erdős's genius was *posing* the right question,
   not sweeping gaps; Polymath projects walk toward a named hard target.
   The honest metaphor is foraging, not farming.

---

## 3. What the repo's own evidence says

The campaign is a case study that tests the model. Results:

- **Best outcome = Jacobian verification = pure Factory A.** Opportunistic
  verification of someone else's witness. Small object, cheap check, famous
  problem, zero synthesis required. This is the template, and the campaign
  wandered away from it.
- **Systematic sweeps produced logs, not theorems.** #699: proved an
  `i ≥ n/5` fragment, scanned to 10⁹, then discovered Price/GPT-5.6 had
  already published a stronger partial proof subsuming ours. **Classic
  tree-walking failure mode** — walked into a filled gap because the
  frontier wasn't checked first.
- **#470 is the cautionary tale for "efficient ≠ valuable."** Trillion-node
  DFS extending a "no odd weird numbers below 10²⁴" bound, while the
  campaign's own insight I9 ("small-cap shard densities don't extrapolate
  to 10²⁴") says the density signal is vanishing. Mechanically excellent
  C code; strategically near-worthless. A factory that runs efficiently in
  the wrong direction is still running in the wrong direction.
- **Cross-pollination attempted without audit (the #313 heuristic)** produced
  a result that *looks* like a theorem (ρ → log 2, ratio ≈ 0.96) but is
  honestly an observation. `next-papers.md` already flags this: "lead with
  this and it reads as an observation, not a theorem."

Pattern: **Factory A produced the win. Factory B attempted without audit
produced plausible-looking non-results. Systematic sweeping produced
neither.**

---

## 4. The witness-factory pipeline (explicit checklist)

Every new target passes through this gate before any compute is spent.
The order is load-bearing — each stage is cheap, and failing an earlier
stage saves the cost of all later ones.

### Stage 0 — Frontier check (MANDATORY, before anything else)

Before reading the problem's math, check whether it's already solved or
past our reach. This is the single cheapest, highest-value stage and its
absence is what burned the #699 effort.

- [ ] erdosproblems.com page: status field, last-edit date, cited frontier.
- [ ] OEIS entry (if a sequence is involved): COMMENTS + EXTENSIONS +
      LINKS sections, dated.
- [ ] arXiv search, last 24 months, for the problem number and for the
      named objects (e.g. "primary pseudoperfect," "odd weird").
- [ ] Tao's erdosproblems wiki changelog if the problem is tracked there.
- **Gate:** if a stronger result than ours is already public, *stop*. File
  the finding, do not compute. (This is `insights.md` I2 made executable.)
- **Process failure to never repeat:** #699 was scanned to 10⁹ without
  this check; Price/GPT-5.6 had already subsumed our fragment.

### Stage 1 — Solvability signature (P1 filter)

Does the problem admit a cheap finite oracle? Apply the signature from
`analysis.md`:

- [ ] Is there a finite object whose existence/refutation settles it?
- [ ] Is checking that object mechanical and fast relative to finding it?
- [ ] Is the verification asymmetric (generation hard, checking easy)?
- **Gate:** if any answer is no → archive as anti-target (infinitary, or
  no cheap oracle). Do not spend compute. The 609 non-falsifiable Erdős
  problems are here for a reason.

### Stage 2 — Oracle construction (before search design)

- [ ] Write the deterministic checker *first*, as standalone code, before
      any search. If the checker can't be written cleanly, the problem
      isn't actually Factory A.
- [ ] Validate the checker on (a) known-positive witnesses and (b)
      known-negative cases below the published frontier (insights I5:
      two gates). A pipeline that fails gate (b) is lying.

### Stage 3 — Search design

- [ ] Estimate witness cost before coding the search. Use the verified
      characterized predicate's arity, not the statement's (insight I7).
- [ ] Density-profile early: run 100 progress lines before walking away
      (insight I8). If density is vanishing, stop — do not extend.
- [ ] Branch-bound by the goal inequality, not the container size
      (insight I6).

### Stage 4 — Output classification (be honest about what was produced)

- **Counterexample / explicit witness:** Factory A at full output. Highest
  value. Publish.
- **Negative bound extension (e.g. "no witness below N"):** legitimate,
  citable, *modest*. Publish only if N meaningfully past the frontier and
  the method is interesting.
- **Finite classification / uniqueness theorem:** Factory A's strongest
  output. Publish (e.g. #313 Target A, if it closes).
- **Heuristic / observation that reads like a theorem:** NOT Factory A
  output. File as a Factory B candidate. Do not publish without an audit
  layer. (The #313 ρ heuristic lives here.)

---

## 5. How Factory B can actually run (when we choose to attempt it)

Only when *all* of:

1. A human mathematician is willing to audit the LLM's moves, **OR** the
   LLM's every claimed step can be re-expressed as a finite computation the
   deterministic oracle checks (i.e. it's secretly Factory A).
2. The frontier check (Stage 0) confirms the target theorem is actually
   open and not a known result in disguise.
3. We are explicit in writeups that heuristic output is heuristic, not
   theorems. The `next-papers.md` warning ("lead with ρ ≈ 0.96 and it reads
   as an observation") is the template for this honesty.

When those hold, Factory B's method is: use the LLM to hold both fields'
literature in context, propose candidate cross-field connections, and for
each connection *reduce the proposed move to a finite checkable consequence*
before trusting it. If the connection cannot be reduced to a finite check,
it stays a conjecture, not a theorem.

---

## 6. Immediate consequences for the live campaign

Translating the strategy into what to do Monday morning:

1. **#470: stop adding shards.** Let the four live P3 shards finish their
   budgets, log the negative bound, and do not launch fleets F/G. The
   campaign's own I9 says the density is vanishing; more shards = more
   logs, not more theorems. This is Factory A running efficiently in the
   wrong direction.
2. **#313 Target A (ω=9 uniqueness): resume.** This is Factory A's
   strongest available output and it's 80% done — 2538/2910 shards
   complete, 858 LOOP nodes remaining, batch-sieve already designed
   (`next-papers.md` decision log). Closing it = a *Math. Comp.*-grade
   finite classification theorem. Redirect the four #470 cores here.
3. **#313 ρ heuristic: reclassify.** It is not a theorem. File under
   Factory B candidate, mark "audit required," do not feature in any
   submission's main result. Honest appendix material at most.
4. **#647: resurrect.** Top of `candidates.md` Tier 1 ("cheapest oracle
   in the entire corpus," £25 prize, single integer = entire proof), got
   one commit then dropped. Most isomorphic to the Jacobian template of
   anything in the corpus. Cheapest Factory A shot currently available.
5. **Build Stage 0 (frontier check) as a real artifact.** A short script
   or checklist that every new target must pass before compute. The #699
   subsumption cost real effort; this is the process fix that prevents
   recurrence.

---

## 7. What this strategy is and isn't

**It is:** a domain-agnostic process for producing a specific *kind* of
math output (witnesses, counterexamples, finite classifications) using
LLMs as search partners and deterministic code as the authority. It does
not require the operator to understand the math deeply. The Jacobian
verification proves this works.

**It isn't:** a method for producing deep structural theorems by
synthesis. That requires either human fluency or a yet-undeveloped LLM
audit layer that can certify multi-step mathematical reasoning. Claiming
otherwise is the failure mode the #313 heuristic illustrates.

The operator's job in Factory A is *taste at the target-selection layer*
(which problems to attempt) and *honesty at the output-classification
layer* (what kind of thing was produced). The middle — search and
verification — is mechanical and delegable. That is a real and valuable
factory. It is just not the factory the original model described, and
naming the difference is what lets it be improved.

---

## Pointers

- `docs/insights.md` — generic tactical lessons (I1–I10). This note is the
  process-level companion to those tactics.
- `docs/candidates.md` — ranked targets; the Stage-0/1 filters above
  re-rank this list.
- `docs/next-papers.md` — #313 decision log; Section 6 item 2 operationalizes
  it.
- `docs/verification-report.md` — the Jacobian verification that is the
  template for Factory A at full output.
