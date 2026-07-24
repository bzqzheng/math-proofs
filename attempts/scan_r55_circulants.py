"""
R(5,5) circulant lottery: does any circulant graph on 43 vertices avoid
both K5 and independent-5? If yes, R(5,5) >= 44 (bound stands at 43 since
Exoo 1989; upper bound 46 via Angeltveit-McKay).

Search: connection sets S ⊆ {1..21} for C_43(S); WLOG 1 ∈ S (scale by
min(S)^{-1} mod 43 — isomorphic), so 2^20 ≈ 1.05M candidates. Complement
of a circulant is a circulant, so checking both ω ≤ 4 and α ≤ 4 on each
covers the full space.

Oracle: bitset backtracking with rotational symmetry — test only cliques /
independent sets containing vertex 0.
"""

import os
import time

P = 43
HALF = 21  # distances 1..21

t0 = time.time()
LIMIT = int(os.environ.get("LIMIT", 1 << 20))
REPORT_EVERY = 50000

adj = [0] * P  # adjacency bitsets, filled per candidate


def has_clique5_or_ind5():
    # K5 containing vertex 0
    N0 = adj[0]
    v1 = N0
    while v1:
        b1 = v1 & (-v1)
        v1 ^= b1
        i1 = b1.bit_length() - 1
        N1 = N0 & adj[i1]
        v2 = N1
        while v2:
            b2 = v2 & (-v2)
            v2 ^= b2
            i2 = b2.bit_length() - 1
            N2 = N1 & adj[i2]
            v3 = N2
            while v3:
                b3 = v3 & (-v3)
                v3 ^= b3
                i3 = b3.bit_length() - 1
                if N2 & adj[i3]:
                    return True  # K5
    # independent 5 containing vertex 0: non-neighbors of 0 (exclude 0 itself)
    M0 = ((1 << P) - 1) & ~adj[0] & ~1
    w1 = M0
    while w1:
        b1 = w1 & (-w1)
        w1 ^= b1
        i1 = b1.bit_length() - 1
        M1 = M0 & ~adj[i1]
        w2 = M1
        while w2:
            b2 = w2 & (-w2)
            w2 ^= b2
            i2 = b2.bit_length() - 1
            M2 = M1 & ~adj[i2]
            w3 = M2
            while w3:
                b3 = w3 & (-w3)
                w3 ^= b3
                i3 = b3.bit_length() - 1
                if M2 & ~adj[i3]:
                    return True  # independent 5
    return False


checked = 0
hits = 0
for mask in range(1, LIMIT, 2):  # bit0 (=distance 1) always set: 1 ∈ S
    S = [d for d in range(1, HALF + 1) if mask >> (d - 1) & 1]
    for v in range(P):
        a = 0
        for d in S:
            a |= (1 << ((v + d) % P)) | (1 << ((v - d) % P))
        adj[v] = a
    checked += 1
    if not has_clique5_or_ind5():
        hits += 1
        print(f"*** R(5,5) >= 44 WITNESS: S={S}", flush=True)
    if checked % REPORT_EVERY == 0:
        print(f"checked={checked:,} hits={hits} elapsed={time.time()-t0:.0f}s", flush=True)

print(f"\ndone: {checked:,} circulants checked, {hits} witnesses. {time.time()-t0:.0f}s", flush=True)
if hits == 0:
    print("=> no circulant (5,5)-graph on 43 vertices exists; bound unchanged.")
