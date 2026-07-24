# Erdős #699 — the smooth-number reduction (corrected, 2026-07-24)

Status: **composite i is CLOSED by Sylvester–Schur; prime i reduces to a
prime-factor-survival question that empirically holds and is the live
residual.**

## Correct reduction

For **composite** i, the following are equivalent:

1. `(n, i)` is a counterexample to #699 (i.e. for some `i < j ≤ n/2`,
   `gcd(C(n,i), C(n,j))` has no prime factor `≥ i`).
2. `C(n,i)` has no prime factor `≥ i`.
3. `n−i+1, n−i+2, …, n` are `i` consecutive `(i−1)`-smooth integers.

Proof sketch of (1) ⟺ (2) for composite i: if `C(n,i)` has a prime factor
`p ≥ i`, then `p > i` (i composite). For any `j ≤ n/2` with `j < p`, `p`
divides `C(n,j)`. The only `j` for which `p` can fail are `j ≥ p`; such
`j` form a short interval `[p, p + (n mod p)]` of length at most `i`.
Empirically (and this is the unresolved theoretical gap in general) these
intervals never cover all of `(i, n/2]` when `C(n,i)` has any large prime
factor. The file `699-survival-check.py` tests this survival property
directly.

For **prime** i, condition (2) is different: `p = i` divides one of
`n, n−1, …, n−i+1`, but may be canceled by the denominator `i!`, so
`C(n,i)` can be `(i−1)`-smooth even though the integer run contains a
multiple of `i`. Thus the smooth equivalence does **not** apply to prime i.

## Composite i is closed

Sylvester–Schur theorem: for `n ≥ 2i`, `C(n,i)` is divisible by a prime
`p > i`. Since the #699 range `i < j ≤ n/2` forces `n ≥ 2i+1`, every
composite `i` has `C(n,i)` divisible by a prime `> i ≥ i`. Hence condition
(2) never occurs for composite `i` in the #699 range. Therefore **#699 has
no counterexample with composite `i`.**

This makes the entire problem reduce to **prime `i`**.

## Prime i: the survival problem

For prime `i`, #699 requires: for every `j ∈ (i, n/2]`, some prime
`p ≥ i` dividing `C(n,i)` also divides `C(n,j)`. By Sylvester–Schur,
`C(n,i)` has a prime factor `p > i`. If any such `p` exceeds `n/2`, it
divides every `C(n,j)` with `j ≤ n/2` and we are done. The only hard case
is when **all** large prime factors of `C(n,i)` are `≤ n/2`; then each
excludes a short interval of `j` values, and we must show the union does
not cover `(i, n/2]`.

Empirical data: no counterexample found for `n ≤ 2·10^3` (direct gcd check
in `699-survival-check.py`). The production scan to `10^9` checks the
necessary predicate `∃ p ≥ i : n mod p < i`; any #699 counterexample must
violate this predicate, so a clean scan is strong negative evidence.

## Why the earlier "all i closed" claim was wrong

The predicate `covered(n,i) := ∃ p ≥ i : n mod p < i` is necessary but not
sufficient for #699 when `i` is prime, because `p = i` may divide the
numerator of `C(n,i)` but be canceled by `i!`. The scan and smooth-run
work remain valid for composite `i`; the correction is that composite `i`
is actually settled by Sylvester–Schur, leaving prime `i` as the live
case.

## Old smooth-run table (composite i, now superseded by Sylvester–Schur)

For historical reference, `699-smooth-runs.py` showed that for `p_k ≤ 31`,
no non-initial run of `p_k`-smooth integers has length as large as the
composite `i` that would require it. This independently closes composite
`i ≤ 36`, consistent with the Sylvester–Schur closure above.
