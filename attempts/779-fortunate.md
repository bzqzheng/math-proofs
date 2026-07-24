# Attempt: Erdős #779 — Fortune's conjecture (falsifiable)

## Status: PROBE COMPLETE, DEPRIORITIZED (2026-07-24)

## Approach
Falsification channel (Ordowski): composite a(n) requires a prime gap after
p_n# larger than p_{n+1}². Scanner computes a(n) = nextprime(p_n#) − p_n#
with full primality proof per candidate (sympy BPSW).

## Results
- Reached only n = 300 in the 1500s budget (sympy isprime is the bottleneck
  at 500+-digit primorials). No composite a(n); max ratio a(n)/p_{n+1}² =
  0.333 (needs > 1 to falsify).
- Coverage is far below the external frontier; the probe adds confidence in
  the pipeline, nothing else.

## Verdict
Not competitive without gmpy2/GMP-grade primality testing (10-100x on
multi-thousand-digit numbers) and a much longer run. The falsification
channel requires a *record-shattering* prime gap — a rare-event lottery
with no tunable structure (unlike #470's δ-window). Deprioritized; revisit
only if gmpy2 is installed and task slots are idle.
