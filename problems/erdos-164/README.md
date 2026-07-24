# Erdős #164 — primitive sets and Σ 1/(a·log a)

**Status:** STATEMENT-CONFIRMED
**Source:** erdosproblems.com #164; resolved 2026 via von Mangoldt chains (see `docs/source-report-2026-07.md`)

## Statement
For any primitive set A (no element divides another), Σ_{a∈A} 1/(a·log a) is
maximized by the primes.

## What we verified
Exhaustive enumeration of **all 163,368 primitive subsets of {2..26}**:
maximum = 1.3428472749, attained *exactly* at the primes. The prime sum to
2·10⁶ is 1.5677, below and approaching the known constant ≈ 1.6366.

This confirms the theorem's finite content. The proof itself (chain method)
was not re-derived — agreement-with-the-statement, not agreement-with-the-proof;
the distinction is discussed in `docs/verification-report.md`.

## Run
```
make verify-erdos-164
```
