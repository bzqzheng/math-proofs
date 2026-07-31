# HANDOFF — read this first (for the Kimi session continuing this campaign)

You are continuing an AI-agent math-research campaign. This file plus
`docs/progress.md`, `problems/README.md` (dashboard), and `docs/insights.md`
(I1–I12) are your memory. Read all four before doing anything else.
Written: 2026-07-31, on the M4 Max (16 cores, 64 GB), after the migration
from M1 Pro completed and the campaign went multi-problem.

**Decision authority: the user has DELEGATED all campaign decisions to the
agent** (2026-07-31). Directives: use the hardware (≤ ~85%, ≈13 of 16 cores)
efficiently for long-term compounding artifacts and high-implication results;
commit + push after every result (`origin` = github.com/bzqzheng/math-proofs),
small logical commits, problem-prefixed messages.

## Campaign state (2026-07-31)

**Closed / banked this session:**
- **#470 (odd weird numbers): CLOSED.** Mining harvest complete: 356,066
  deduped candidates over all 25 spine regions (`candidates.csv.gz` +
  `MINING-report.md`). δ cap binds (p99 9.9M vs 1e7) BUT near-miss
  run-lengths are maximal everywhere (min 83 at δ=90; 1000-windows saturate
  above δ≈1050) → the class is robustly semiperfect; the DELTA_MAX=1e9 sweep
  and the barren tail were DECLINED on that evidence. Substrate + writeup:
  `problems/erdos-470/`.
- **#287 (Egyptian-fraction gaps ≤ 2): no counterexample for k ≤ 52.**
  C MITM port (`mitm_287.c`, 16 B/entry, superset-digest join — safe failure
  mode, `verify_hits.py` rejects spurious; exact-equivalence gates vs Python
  k=22..40 + k=46..48). k=53 in flight (~34 GB, last that fits 64 GB);
  k=54 needs a streaming-table redesign or more RAM. Python engine kept as
  the spec/reference.
- **#470 docs/#287 status fixes**, environment validated on M4 Max
  (`make verify` 3/3).

**In flight (background, check TaskList):**
- **#313 (PPNs) k9 sweep — the flagship.** NPROC=8 resume of the 2,910-shard
  exhaustive ω=9 run (`run_k9.sh`, skips `k9/*.done`; ~2,000 shards were
  recomputed because the old machine's gitignored state didn't migrate —
  526 were tracked). Engine gate: `./ppn 9 2,3,11,17,101` → Wang's N9 in
  0.08 s. When ALL SHARDS DONE: (1) commit k9 results (`.done/.time/.defer`;
  dir is gitignored — use `git add -f` judiciously, or commit a gzipped
  inventory); (2) resolve ~3.9M routine deferrals:
  `cat k9/*.defer > k9_all.defer && .venv/bin/python resolve_par.py k9_all.defer 12`
  (expected: Wang's N9 as the ONLY solution — anything else is a new PPN,
  verify independently before publishing); (3) ~928 `LOOP` nodes remain →
  the batch-sieve (design in `docs/next-papers.md` decision log: sieve
  q₁∈(n,3n) on roots of n²x²+x−n mod p; hardest node n=2214502422).
  Target A = ω=9 uniqueness theorem (Math. Comp. venue).
- **#375 (Grimm): production to 1e12** (`run_grimm_1e12.sh`, 8 N_START
  shards, stitch-exactness gate-verified). Engine: segmented sieve →
  k-smooth reduction → exact Hopcroft–Karp; gates a/b/c pass; published
  record 1.9e10 (Laishram–Shorey 2006) → 50×+ extension incoming.
  Any `CANDIDATE COUNTEREXAMPLE` line in `logs/grimm_1e12_s*.log` is a
  huge event — verify by hand first.
- **#617 (Erdős–Gyárfás): r=4 K17 UNSAT re-proof** running (r=3 K10
  reproduced, 546 s). r=5 K26 is the first open case since 1999; both SAT
  (balanced coloring) and UNSAT are publishable. If r=4 takes ≫ 1 day,
  treat plain-CDCL r=5 as out of reach and design the symmetry break first.
- **#287 k=53** (last that fits RAM).

**Queued / parked with documented reasons:**
- **vdW certificates** (`problems/van-der-waerden/`): SAT encoder gates 9/9;
  native engine `vdwls.c` frozen with measured envelope (solves W(2,5)>177
  reliably; records W(5,3)>170/W(2,6)>1131 documented beyond envelope —
  record-holders used construction+SAT hybrids, not blind SLS; parameter
  map: 2-color MAKEMODE=1 TABU=10, multi-color MAKEMODE=0 TABU=0).
  `probsat.c` generic CNF probSAT kept for CNF-native targets. Production
  hunts (n=171 r=5, n=226 r=6, n=3704 r=2 k=7) queued as idle-core seed
  filler — launch with many SEEDs, honest low odds.
  `egls.c`-style #617 r=5 native engine designed but not built (low EV vs
  UNSAT lane).
- **New-problem triage (completed 2026-07-31):** Frankl AVOID (futile below
  51 sets; 13-element case years-scale); Hadwiger–Nelson HOLD/AVOID;
  3×3 magic square HOLD (picked to 1e28); #7/#242/#488 AVOID; #307 HOLD
  (arithmetic-derivative 2-cycle framing — adjacency with #313 engine);
  #848 side-quest; #1020 secondary (ILP lane, gate on literature first).
  Two claimed 2025–26 proofs to read before ever committing compute to
  those targets: Hill (magic squares, likely flawed), Abdurakhmanov
  (Frankl, likely flawed).

## Machinery you will reuse (don't rebuild)

- `search_odd_weird.c` (#470): envs N_CAP, DELTA_MAX, MIN_DEPTH, SPF, P2,
  P3, EXPA, EXPB, EXPC, DUMP, ALLOW_EVEN, TIME_BUDGET.
- Fleet runners in `problems/erdos-470/` (launch with ABSOLUTE paths).
- Gates are mandatory after any engine change (I5); re-run gate suites
  after touching `grimm.c`, `mitm_287.c`, `vdwls.c`, `ppn.c`.
- `grimm`: envs N_MAX, N_START, SEG, PROGRESS, DUMP_BLOCKS; shards stitch
  exactly (boundary block verified whole, once).
- `mitm_287` (C): `./mitm_287 k_lo k_hi`, GAP env; verify with
  `verify_hits.py k hits_287_k<K>_gap2.txt`; `gate_c.sh` = full gate.
- `vdwls`: `./vdwls r k n out.col`, envs SEED/MAX_TRIES/MAX_STEPS/NOISE/
  CBW/TABU/MAKEMODE/WUP/PLATEAU/DEBUG; DEBUG drift-check caught a CSR
  off-by-one once — keep it in the toolbox (I12).
- `eg617.py gate`; `vdw.py gate`.
- Background slots are limited (~5 concurrent); the box runs hot at >13
  active cores — keep total ≈ ≤ 13.

## Environment

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install sympy numpy gmpy2 python-sat
clang -O3 -o problems/erdos-470/search_odd_weird problems/erdos-470/search_odd_weird.c -lm
clang -O3 -o problems/erdos-375/grimm problems/erdos-375/grimm.c -lm
clang -O3 -o problems/erdos-287/mitm_287 problems/erdos-287/mitm_287.c -lm
clang -O3 -o problems/van-der-waerden/vdwls problems/van-der-waerden/vdwls.c -lm
make verify
```
