# Erdős #64 — Erdős–Gyárfás power-of-2 cycles

**Status:** BLOCKED (needs a construction, not enumeration)
**Source:** erdosproblems.com #64 ($1000, tagged falsifiable)

## Statement
Every graph with minimum degree ≥ 3 contains a cycle whose length is a power
of 2. A counterexample is a single finite graph — perfectly checkable — but
any counterexample needs ≥ 30 vertices (known lower bound).

## Results
- nauty-based enumeration of cubic / min-degree-3 graphs explodes well below
  the 30-vertex bound (`scan_64_graph_cycles.py`)
- Raw enumeration is dead; resume only with a structural construction
  (e.g. lifting known small obstructions, or SAT with symmetry breaking).
