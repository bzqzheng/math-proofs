# math-proofs

**An AI agent's verification-first campaign on open Erdős problems — which conjectures LLMs can actually crack, why those and not others, and what a systematic hunt turns up.**

In 2026, long-standing conjectures started falling to LLM-assisted attacks: the Jacobian conjecture in dimension 3 (87 years open), the Erdős unit-distance problem, a cluster of primitive-set conjectures. This repo is a working lab notebook that asks the obvious follow-up: *what do the fallen problems have in common, and can the pattern be exploited on purpose instead of by accident?*

Everything here runs on one rule:

> **A solution without a passing checker is a hypothesis.** Every claim below is backed by a committed, runnable script. Negative results get the same care as positive ones — a clean verification bound is a citable result, not a failure.

## Highlights

- **Independent re-verification of the Jacobian counterexample.** The Alpöge–Fable 5 polynomial map that killed the 87-year-old Jacobian conjecture, confirmed from scratch in SymPy: `det(JF) ≡ −2`, and the map is 3-to-1 at `(−1/4, 0, 0)`. Two lines of computer algebra, zero trust required — the witness *is* the proof. → `verification/`, `VERIFICATION_REPORT.md`
- **Exhaustive confirmation of Erdős #164's finite content.** All 163,368 primitive subsets of `{2..26}` checked; the maximum of `Σ 1/(a·log a)` is attained *exactly* at the primes. → `VERIFICATION_REPORT.md`
- **A triaged attack corpus.** 1,217 problems from the Erdős Problems database scored against a derived "LLM-solvability signature": 652 attackable → 43 reducible to finite computation → a ranked hit list. → `CANDIDATES.md`
- **Live attacks with new computational bounds** on Erdős #699, #470, #779, #458, #993, #287, #313 — every attempt documented with approach, code, logs, and verdict, including the failures. → `attempts/`, `PROGRESS.md`
- **Compounding insights.** Eight problem-generic lessons so far about oracle design, search structure, and when *not* to compute. Shortest valuable read in the repo. → `INSIGHTS.md`

## The LLM-solvability signature

Across every 2026 success story, the solved problems share a fingerprint — and the contrapositive explains why RH, P≠NP, Collatz, and the twin prime conjecture will *never* fall this way:

1. **Verification asymmetry** (the master property). Checking a candidate is cheap and mechanical relative to finding it. The Jacobian witness certifies itself in milliseconds; RH has no finite witness at all.
2. **The bottleneck was search, not depth.** The missing object was short — the Jacobian witness is 216 characters — not a new theory.
3. **Clean, self-contained statements.** Combinatorics, discrete geometry, polynomial algebra, elementary number theory. Nothing requiring a decade of prerequisites has fallen.
4. **Exploitable structure.** Parametric families with symmetry let the model extrapolate small cases into general constructions.
5. **A fast generate–verify loop.** SymPy, Lean, SAT, or brute force in the loop. Lone-shot generation produced nothing.
6. **Batch economics.** Observed hit rates are ~2.5–9%. The play is high-throughput triage over curated problem lists, not lottery tickets on famous singletons.

Full argument with evidence: `ANALYSIS.md`.

## Results so far

| Problem | Question | Result | Status |
|---|---|---|---|
| Jacobian conjecture (dim 3) | Is the Alpöge–Fable 5 counterexample valid? | `det(JF) ≡ −2` and the 3-to-1 collision confirmed exactly | **Verified** |
| Erdős #164 | Primitive sets and `Σ 1/(a log a)` | Statement holds exhaustively on all 163,368 primitive subsets of `{2..26}` | **Statement confirmed** |
| Erdős #699 | `gcd(C(n,i), C(n,j)) > 1` | Zero counterexamples below `n ≈ 5.9·10⁸` (scan to 10⁹ running); composite-`i` case closed via Sylvester–Schur | Scanning |
| Erdős #470 | Odd weird numbers | Constructive DFS over odd primitive abundant numbers, sharded by smallest prime factor; SPF=5..53 shards complete to 10²⁴, zero finds; SPF=3 running | Scanning |
| Erdős #779 | Fortune's conjecture | No composite Fortunate number for `n ≤ 780` | Bound extended |
| Erdős #458 | `lcm`-vs-binomial inequality | No counterexample for `k ≤ 10⁷`; minimum margin 0.15415 | Bound extended |
| Erdős #993 | Independence-polynomial unimodality for trees | No counterexample across spiders, star-arms, caterpillars, and Kadrawi–Levit families; best near-miss ratio 0.995652 | Deprioritized (literature frontier n=29) |
| Erdős #287 | Egyptian fractions with gaps ≤ 2 | No counterexample for `k ≤ 21` | Needs a better algorithm |
| Erdős #647 | Divisor-function maxima | Calibrated away: Idén (June 2026) already verified to 10¹² | Deprioritized |
| Erdős #64 | Power-of-2 cycles | Enumeration explodes below the known 30-vertex bound | Blocked — needs a construction |

## Repo map

- `ANALYSIS.md` — the solvability signature, fact-check of the 2026 claims, ranked targets
- `CANDIDATES.md` — corpus triage (1,217 → 652 → 43), tier rankings, and named anti-targets
- `INSIGHTS.md` — compounding, problem-generic lessons (read this even if you skip the rest)
- `VERIFICATION_REPORT.md` + `verification/` — offline re-verification scripts and verdicts
- `attempts/` — one notes file per attacked problem: approach, code, logs, verdict
- `PROGRESS.md` — live status, updated as scans complete
- `llm-solved-problems-2026.md` — the source report that started the campaign

## Method

1. **Oracle first.** No candidate counts unless a deterministic checker (SymPy, a custom enumerator, SAT, Lean) certifies it.
2. **Calibrate before compute.** OEIS comments and last-24-months preprints come first; never burn CPU below the published frontier. This saved days twice in the first week.
3. **Generate → verify → log.** Every attempt, positive or negative, is committed with checker output. The negative results are what separate research from astrology.
4. **Anti-targets are named.** Anything without verification asymmetry — RH, P≠NP, Navier–Stokes, Collatz, twin primes, Goldbach — is explicitly out of scope. A claimed chat-model "proof" of those is crank output until formally verified end-to-end.

## Reproduce

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install sympy numpy gmpy2
python verification/verify_jacobian_counterexample.py   # seconds; settles an 87-year-old conjecture
```

Attack scripts live in `attempts/` (Python, plus one C program for the #470 sweep). Each problem's notes file names its entry point.

## Provenance

The analysis, code, and notes in this repo were produced by Kimi (K3-class reasoning model) operating as an autonomous agent under human direction, July 2026. The design principle is that this shouldn't matter: every mathematical claim here is checkable by running the committed scripts, and the failures are documented as carefully as the wins.
