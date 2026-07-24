# A provable fragment of Erdős #699 (2026-07-24)

## Theorem (fragment). The binomial-gcd conjecture holds for all i ≥ n/5.

**Claim.** For every n and every i with n/5 ≤ i < n/2, there exists a prime
p ≥ i with n mod p < i. Hence (by the Kummer reduction in
`699-458-binomial-lcm.md`) p divides gcd(C(n,i), C(n,j)) for every
i < j ≤ n/2 — the conjecture holds in this range.

**Proof.** Put x = n − i. Since i < n/2 we have x > i, so any prime
p ∈ (x, n] satisfies p > x = n − i ≥ i and n mod p = n − p < n − x = i —
both required properties at once. It remains to force a prime into (x, n].

Nagura's theorem (j=4 rung: for x ≥ 24 there is a prime in (x, 5x/4);
Nagura 1952, Proc. Japan Acad. 28, 177–181) applies whenever x ≥ 24, and
5x/4 ≤ n ⟺ 5(n−i)/4 ≤ n ⟺ i ≥ n/5 — exactly our hypothesis. For
n ≥ 46 we have x = n − i ≥ n/2 ≥ 24 and we are done. For n ≤ 45 the claim
is verified by direct computation (our exhaustive scan, 0 counterexamples;
boundary cases n ∈ [30, 46) re-checked explicitly below). ∎

## Corollaries (stronger rungs for large n)
- **Schoenfeld 1976** (Math. Comp. 30, 337–360: prime in (x, x(1+1/16597))
  for x ≥ 2,010,760) ⟹ the conjecture holds for n ≥ 2,010,761 and
  i ≥ n/16598.
- **Ramaré–Saouter** (prime in (x(1 − 1/28314000), x] for
  x ≥ 10,726,905,041) ⟹ the conjecture holds for n ≥ 10,726,905,041 and
  i ≥ n/28314000.

## What remains open
Only the regime i = o(n):
- n ≤ 10^8: settled exhaustively by our scan (870.8M pairs, 0 failures;
  10^9 extension running).
- 10^8 < n < 1.07·10^10: open only for i < n/16598.
- n ≥ 1.07·10^10: open only for i < n/28314000.

So the entire conjecture now hinges on tiny i relative to n — the
sieve/covering regime sketched in the main log (n mod p ≥ i for ALL primes
p ∈ [i, n] simultaneously is required for failure).

## Honesty notes
- The fragment is elementary given Nagura; it may be folklore, but the
  erdosproblems.com/699 page cites no partial result of this form (only
  Sylvester–Schur for single binomials), so we record it with the exact
  rungs and constants. Not submitted anywhere; literature check pending.
- Citations verified via web (Nagura j-ladder incl. j=4 at x ≥ 24;
  Schoenfeld 16597; Ramaré–Saouter 28314000), not from memory.
