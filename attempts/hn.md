# Attempt: Hadwiger–Nelson — 6-chromatic unit-distance graph (Tier-1 #5)

## Status: ORACLE VALIDATED, GENERATION OUT OF REACH THIS ITERATION

## What was done
- Reconstructed the Moser spindle from first principles (two unit lozenges
  hinged at angle 2·asin(1/(2√3))): 7 vertices, degree sequence
  [3,3,3,3,3,3,4] — matches the canonical graph.
- DSATUR exact colorer confirms χ = 4. Oracle (`attempts/hn_probe.py`) is
  validated for any future candidate graph.

## Why generation is not attempted now
- Current state of the art: 5 ≤ χ ≤ 7. de Grey's 5-chromatic graph (2018)
  had 1,581 vertices and took cluster-scale SAT-guided search; Heule's
  trimming was itself a major SAT computation. A 6-chromatic witness is
  strictly harder and likely larger.
- The triangular lattice is only 3-colorable ((i+2j) mod 3 works), so
  lattice patches are dead ends; de Grey's constructions are spindle
  composites — a rich but astronomically large design space, where the
  winning move was SAT-guided trimming, not generation.
- Python DSATUR dies above ~100 hard vertices. A serious attempt needs
  python-sat + de Grey's methodology + weeks of CPU. Low EV this iteration.

## Revisit condition
If the repo gains a SAT solver and idle compute weeks: replicate de Grey's
5-chromatic construction first (validate at scale), then explore spindle
composites with SAT trimming. Until then this stays a validated oracle
with no generator.
