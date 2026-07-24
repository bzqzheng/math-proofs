# Attempts: #364 (three consecutive powerful numbers) and #366 (2-full n with 3-full n+1)

## Status: SCANS RUNNING, 2026-07-24

## Statements and witness shapes
- **#366**: find n powerful (every prime exponent ≥ 2) with n+1 3-full
  (exponents ≥ 3). No example known; DB tags it "verifiable" (a witness is
  machine-checkable). Search from the sparse side: 3-full numbers have
  density ~ x^{1/3}; test powerful(n−1) with a strip-small-primes +
  perfect-square-cofactor test (O(primes ≤ cbrt) worst case, tiny average).
- **#364**: Erdős conjectured NO three consecutive powerful numbers.
  Counterexample = witness. Enumerate powerful ≤ X via canonical a²b³
  (b squarefree), sort, scan for runs. Known pair list (A060355) validates
  the enumerator.

## Validation (PASSED, X=10^7)
- Powerful count 6,553 (consistent with ~2.17√x).
- All 9 known consecutive pairs ≤ 10^7 found; zero triples.

## Full run (background): 3-full ≤ 10^18 for #366; powerful ≤ 10^12 for #364.

## Heuristic prior (honest)
Expected number of #366 solutions up to X is ~ ∫ x^{1/3}·x^{−1/2}/x dx-type
— a convergent integral: if solutions exist at all, they are finitely many
and probably small. A null result at 10^18 materially lowers the
probability that a solution exists at searchable size at all; it would then
become a theory problem (why does the Pell mechanism that produces
(2-full,2-full) and (3-full,2-full) pairs never produce (2-full,3-full)?).
#364 is the same shape: conjectured empty, heuristic agrees, scan is due
diligence + frontier extension.

## Note on #307 (skipped)
Barbeau's prime-reciprocal product problem has a 2026 machine-checked
barrier (Bonfioli): any solution needs ≥ 59 primes and prime-products
≥ 2·10^56. Brute force is dead; needs an ideas-first approach. Skipped.

## Theory note (2026-07-24): why (2-full,3-full) is a Thue problem, not a Pell problem

Canonical forms: n 2-full ⟺ n = c²d³ (d squarefree, unique). m 3-full ⟺
m = x³y² with rad(y) | x (exponents e ≥ 3 are exactly those writable
3f + 2g with no prime left at exponent exactly 2).

So #366 asks for solutions of
    x³y² − c²d³ = 1,   rad(y) | x, d squarefree.
For each FIXED (y, d) this is a Thue equation (binary cubic form in x, c)
— finitely many solutions, effectively computable (Baker + LLL). This
explains the asymmetry with the famous cases:
- (2-full, 2-full) consecutive pairs are infinite because they come from
  PELL equations (degree 2: x² − 8y² = 1, Mahler's answer to Erdős).
- (3-full, 2-full) examples exist (8/9, 12167/12168, ...) because
  cube-vs-square Thue curves x³ − c²d³ = ±1 occasionally have points.
- (2-full, 3-full) pairs require the SAME Thue family but with the rad(y)|x
  constraint on the cube side and squarefree condition on the other —
  the scan's job is to find one lattice point on any of these curves
  satisfying the side conditions.

Program if the scan returns null:
1. For small (y, d), enumerate the Thue curves x³y² − c²d³ = 1 and solve
   each (sage/pari `thue` would do it; or implement Baker-free small-case
   search bounded by the scan frontier).
2. Any solution automatically satisfies n+1 3-full IF rad(y) | x; check the
   side conditions.
3. The interesting theorem-shaped output even without a full solution:
   "no (2-full,3-full) pair with y·d ≤ B" for the largest B our scan +
   Thue bounds reach — a finite, publishable obstruction statement.

Status: scan running first; this is the fallback path.

## Full run results (2026-07-24)
- **#366: 4,480,252 three-full numbers ≤ 10^18 enumerated; ZERO have a
  2-full predecessor.** No (2-full, 3-full) consecutive pair exists below
  10^18. Complete over this range (the 3-full side is the sparse side, so
  enumeration is exhaustive — no window caveat). We are not aware of a
  published bound for this question; treat 10^18 as our verified frontier,
  to be cross-checked against literature before claiming novelty.
- **#364: 2,158,391 powerful numbers ≤ 10^12; exactly 18 consecutive pairs
  — matching A060355 term-for-term; ZERO triples.** Consistent with Erdős's
  conjecture; frontier presumably well beyond 10^12 in the literature, so
  this is pipeline validation, not new ground.
- Throughput note: 24 min total, dominated by is_powerful on 18-digit
  survivors. A compiled version reaches ~10^21 for #366 with days of CPU —
  the heuristic (convergent integral) says expected witnesses up there are
  O(1) at most; diminishing returns without the Thue angle.
