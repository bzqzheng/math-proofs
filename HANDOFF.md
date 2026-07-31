# HANDOFF — read this first (for the Kimi session continuing this campaign)

You are continuing an AI-agent math-research campaign. This file plus
`docs/progress.md`, `problems/README.md` (dashboard), and `docs/insights.md`
(I1–I12) are your memory. Read all four before doing anything else.
Written: 2026-07-30, on migration from M1 Pro (32 GB) → M4 Max (64 GB).

## What this repo is

A verification-first campaign on open problems (Erdős DB + famous-witness
targets). The operating rule: **a solution without a passing checker is a
hypothesis**. Method: `docs/pipeline.md`. Analysis of what makes problems
LLM-solvable (P1–P6 signature): `docs/analysis.md`.

## Campaign state (exact)

**Completed:**
- Independent re-verifications: Jacobian counterexample (dim 3), Erdős #164
  (exhaustive on 163,368 primitive subsets), unit-distance baseline.
  → `docs/verification-report.md`, `make verify`
- **#699** (binomial gcd): 0 counterexamples for all n ≤ 10⁹, 10.34B pairs.
  BOUND-EXTENDED. → `problems/erdos-699/`
- **#470** (odd weird numbers): sweep complete as designed. 0 finds across
  ≥ 20T nodes / ≥ 360k candidates. Full writeup + 25-row spine registry +
  compounding-value section. → `problems/erdos-470/RESULTS.md`
- **#287** (gaps ≥ 3 in Egyptian-fraction reps of 1; FALSIFIABLE):
  **no counterexample for k ≤ 45**, exhaustive MITM (`mitm_287.py`,
  3-prime residue hash + Fraction verify). k=45: 23M+67M halves, 313 s.

**In flight / pending decisions:**
- **#470 near-miss mining** (the harvest): fleet `run_mining.sh` dumps all
  candidates (n, δ, fac) from the 25 spines to `problems/erdos-470/mining/`.
  At handoff: ~10/25 logs done, 345k+ candidates and counting; the analysis
  script `analyze_mining.py` is WRITTEN AND TESTED (bitset capped at δ —
  uncapped shifts OOM, fixed). Next: let the fleet finish, then run
  `.venv/bin/python problems/erdos-470/analyze_mining.py` →
  `candidates.csv.gz` + `MINING-report.md`, then commit.
- **#287 k ≥ 46**: each k doubles table+time (k=45: 313 s, ~6 GB).
  k=46–48 fit on 64 GB (~12–25 GB table); k ≥ 49 needs a C port.
  Command: `.venv/bin/python problems/erdos-287/mitm_287.py --exhaustive 46 48`
- **Held for the user:** #470 barren tail (P3=17..59, ~1 day, ~zero value —
  recommendation: skip); DELTA_MAX=1e9 sweep on the 25 spines (the real
  counterexample hunt — decide after the mining analysis shows the
  δ-distribution).
- **Next problem candidates (user deciding):** Tier-0 non-Erdős list was
  proposed (Frankl union-closed [best risk-adjusted], van der Waerden lower
  bounds [SAT certificates], Hadwiger–Nelson [moonshot; oracle already
  validated in `problems/hadwiger-nelson/`], 3×3 magic square of squares).
  Jacobian n=2 = lottery ticket, side bet only.

## Machinery you will reuse (don't rebuild)

- `search_odd_weird.c`: envs N_CAP, DELTA_MAX, MIN_DEPTH, SPF, P2, P3,
  EXPA, EXPB, EXPC, DUMP, ALLOW_EVEN, TIME_BUDGET. Build:
  `clang -O3 -o problems/erdos-470/search_odd_weird problems/erdos-470/search_odd_weird.c -lm`
- Fleet runners in `problems/erdos-470/`: `run_p3_fleet.sh`, `run_a_fleet.sh`,
  `run_b_fleet.sh`, `run_c_fleet.sh`, `run_mining.sh`. Launch with ABSOLUTE
  paths (`cd DIR && runner1 & runner2 &` backgrounds only the first — this
  bug already bit once).
- Gates are mandatory after any engine change: (a) 7/7 known even weirds at
  N_CAP=10000; (b) union of sub-shards ≡ full shard at N_CAP=1e9 (exact
  tested counts). Same discipline for any new problem (I5).
- #287 MITM gates: `python mitm_287.py gate` (GAP=3 finds (2,3,6); GAP=2
  zero for k ≤ 21).

## Environment setup (M4 Max)

```bash
git clone https://github.com/bzqzheng/math-proofs.git
cd math-proofs && python3 -m venv .venv && source .venv/bin/activate
pip install sympy numpy gmpy2
clang -O3 -o problems/erdos-470/search_odd_weird problems/erdos-470/search_odd_weird.c -lm
make verify
```

If `problems/erdos-470/mining/` is incomplete in the clone (fleet was still
running on the old machine), just re-run `problems/erdos-470/run_mining.sh`
— idempotent, ~2× faster on this machine.

## How to continue

1. `git pull`; read the four memory files above.
2. Check TaskList for running tasks; if none, resume the "In flight" list.
3. Commit + push after every result (`origin` = github.com/bzqzheng/math-proofs).
4. When in doubt, prefer finishing the #470 mining analysis → then #287
   k=46–48 → then the user's next-problem decision.
