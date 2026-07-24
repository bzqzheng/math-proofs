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
