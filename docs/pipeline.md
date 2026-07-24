# Pipeline — how this repo attacks open problems

One page. Six stages. Every problem in `problems/` has passed through stages 1–3;
stage 4 is where it lives; stages 5–6 decide what its results are worth.

## Stage 1 — Intake
Corpora land in `data/` (bulk, gitignored): the erdosproblems.com database,
DeepMind formal-conjectures (Lean), OEIS snapshots. Intake is pull-only and
read-only; corpora are inputs, never edited.

## Stage 2 — Triage
Score each problem against the P1–P5 solvability signature (`docs/analysis.md`):

- P1 verification asymmetry (a finite witness with a cheap checker exists)
- P2 the bottleneck is search, not depth
- P3 clean, self-contained statement
- P4 exploitable structure/symmetry
- P5 a fast generate–verify loop is available

Output: a ranked hit list and a named anti-target list (`docs/candidates.md`).
Infinitary problems (asymptotics, limits, infinite families) fail P1 and are
rejected at this stage, not discovered as failures in stage 4.

## Stage 3 — Calibration
Before any compute: OEIS comments/extensions + preprints from the last 24
months. Record the published frontier in the problem README with citations.
**Never compute below the published frontier.** (This stage has saved days
twice in the first week — see insights I2.)

## Stage 4 — Attack
One directory per problem under `problems/<id>/`, scaffolded from
`problems/TEMPLATE/` (`make new ID=<id>`):

```
problems/<id>/
├── README.md     # statement, witness shape, calibration, oracle, approach, results, verdict
├── <code>        # scanners, provers, verifiers — runnable, no hidden state
└── logs/         # run artifacts; committed at milestones
```

Status taxonomy (README header, kept current):

| Status | Meaning |
|---|---|
| SCOPED | statement + witness shape written, nothing run |
| CALIBRATED | frontier established; compute plan priced |
| SCANNING | search running / periodically resumed |
| BOUND-EXTENDED | clean verification past the previous frontier (a citable result) |
| VERIFIED | an external claim's witness independently confirmed |
| STATEMENT-CONFIRMED | finite content of a theorem confirmed exhaustively |
| DEPRIORITIZED | expected value dropped below other targets; reason recorded |
| BLOCKED | no viable approach this iteration; what would unblock it recorded |
| SOLVED / FALSIFIED | settled here, with the checker output committed |

## Stage 5 — Verification
Oracle gates, both mandatory before frontier compute (insight I5):

- **Gate (a) known-positive:** the pipeline must reproduce a known witness.
- **Gate (b) known-negative:** it must find nothing below the published frontier.

No candidate counts unless a deterministic checker certifies it. A "solution"
without a passing checker is a hypothesis and is labeled as such.

## Stage 6 — Report
Verdict in the problem README → rollup in `docs/progress.md` → generic lessons
promoted to `docs/insights.md` (only if applicable beyond the problem where
found) → commit and push. Negative results are reported with the same care as
positive ones: they prune the search tree for everyone who comes next.

## Operating rules

1. Oracle first — no checker, no claim.
2. Calibrate before compute.
3. Generate → verify → log, every attempt.
4. Anti-targets stay named — do not drift into them.
5. One problem = one directory = one current status. The dashboard
   (`problems/README.md`) is the single source of truth for "where are we".
