# Progress notes — math-proof campaign

Last updated: 2026-07-24

## Active background scans

| Task | Problem | Command / file | Current status | Timeout |
|---|---|---|---|---|
| `bash-53si6yjm` | Erdős #699 binomial gcd | `problems/erdos-699/scan_699.py` to `10^9` | `n ≈ 576M`, `5.7B` cases checked, **0 counterexamples** | 6 h (~45 min left) |
| `bash-51p87u8h` | Erdős #470 odd weird | `problems/erdos-470/search_odd_weird` SPF=3 shard to `10^24` | `141B` nodes, `262,801` candidates, **0 weird** | 7 h (~2.8 h left) |

## Completed attempts

- **#779 Fortunate numbers** — no composite Fortunate number up to `n = 780` (time budget).
- **#458 lcm inequality** — no counterexample up to `k = 10^7`; min margin `0.15415` at `k = 4`.
- **#993 tree independence-polynomial unimodality** — deprioritized after extensive search.
  - SA on general trees: best ratio `0.962`.
  - Kadrawi–Levit families `3,k,k+j` / `3*,k,k+j`: clean to `k=100, j=30`; best `0.990`.
  - Pure spiders `S(a,b,c)`: clean to arm length `50`; all unimodal.
  - Pure star-arms: clean to `m_i = 120`; best `0.994`.
  - Caterpillars: clean in exhaustive sweep `L≤6, A≤12`; SA record near-miss `0.995652` at `n=463` (`a=[100,97,90,73,98]`).
  - Literature calibration (Reynolds Zenodo v3; Hibi–Kara–Vien arXiv Apr 2026): conjecture open, verified to `n=29`, known bush families pushed to `60` vertices without non-unimodal tree.

## Started / partial

- **#287 Egyptian-fraction gaps** — searching for `1 = Σ 1/n_i` with `1<n_1<...<n_k` and all gaps `≤2`. No counterexample for `k ≤ 21`; backtracking cost explodes at `k=22`.

## Blocked / deprioritized

- **#64 power-of-2 cycles** — raw cubic/min-degree-3 enumeration explodes before the 30-vertex lower bound. Needs a construction, not more CPU.
- **#1052 unitary perfect / #398 Brocard** — search space enormous, no near-miss signal.

## Compounding insights

1. **Verification asymmetry is the master filter.** Every attackable problem here is falsifiable by a single finite object with a fast mechanical check.
2. **Local search plateaus.** #993 and its caterpillar sub-problem both climb to `0.99+` fitness without producing a witness — a strong signal that either the conjecture holds or the counterexample is structurally distant.
3. **Literature calibration beats blind search.** The Reynolds preprint saved days of redundant computation on tree families already analyzed to `n=60`.
4. **Negative results are citable.** Extending clean verification bounds is real progress, even without a counterexample.
