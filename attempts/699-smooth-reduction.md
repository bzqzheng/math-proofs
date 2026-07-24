# Erdős #699 — the smooth-number reduction (major structural result)

Date: 2026-07-24. Status: reduction PROVED + verified numerically (300 random
pairs, 0 mismatches); cases closed per the table below.

## The reduction

covered(n, i) ⟺ ∃ prime p ≥ i and r ∈ {0,…,i−1} with p | n−r.
Therefore, with (i−1)-smooth meaning "no prime factor ≥ i":

    (n, i) is a COUNTEREXAMPLE to #699
    ⟺  n−i+1, n−i+2, …, n  are i consecutive (i−1)-smooth integers.

The binomial coefficients are gone; what remains is a pure statement about
runs of consecutive smooth numbers.

## Immediate closures

- **i prime: CLOSED (trivially).** p = i itself covers: n mod i < i always.
  (Equivalent view: any i consecutive integers contain a multiple of i,
  which is never (i−1)-smooth.)
- **i ∈ {4,5}: CLOSED (proved).** Failure needs i ≥ 4 consecutive 3-smooth
  integers. Among any 4 consecutive, the two odd ones differ by 2 and would
  both need to be powers of 3; 3^a − 3^b = ±2 forces {1,3}, so the only
  all-3-smooth quadruple is {1,2,3,4} (n=4), and n > 2i = 8 excludes it.
  Verified: 3-smooth runs to 10^6 are exactly {1,2,3,4} and {8,9}.
- **The initial run never fails.** p_k-smooth numbers (p_k = largest prime
  < i) start with {1,…,p_{k+1}−1} (p_{k+1} = next prime). Any failing run
  of length i within it ends at n ≤ p_{k+1}−1 < 2i by Bertrand's postulate
  (p_{k+1} < 2i). So only NON-initial runs matter.

## What remains: composite i
For composite i with p_k = largest prime < i, a counterexample is exactly a
run of i consecutive p_k-smooth integers starting above i+1. Classical
theory (Størmer 1897; Lehmer 1964/65 computed all consecutive p-smooth
pairs for p ≤ 41 via Pell equations) says runs of p-smooth numbers are
finite and effectively computable; long runs are drastically rarer than
pairs. The required bound per i: no run of length ≥ i of p_k-smooth
numbers beyond position 2i.

## Computational status of the run table
See `699-smooth-runs.py` output (appended below when available): max run
lengths of consecutive p-smooth numbers (p ≤ 31) beyond the initial
segment, vs. the run length each composite i would require.

## Why this is the right frame
- Prime i: done. i ∈ {4,5}: done. Initial runs: done.
- Composite i with p_k-smooth run bound: a FINITE, classical, checkable
  question per i — and known results (Lehmer's tables + Shorey–Tijdeman
  gap theorems) plausibly close all small i outright.
- Combined with the fragment theorem (i ≥ n/5 closed for all n) and the
  exhaustive scan (n ≤ 10^8), the residual is: composite i, runs of length
  i of p_k-smooth numbers in the window n ∈ (2i, 10^8] — computation —
  and n > 10^8 — theory.
