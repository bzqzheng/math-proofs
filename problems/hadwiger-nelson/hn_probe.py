"""
Hadwiger–Nelson probe: unit-distance graph chromatic-number oracle.

Builds the Moser spindle (7 vertices, chi=4) and validates a DSATUR exact
colorer on it. Foundation for any future 6-chromatic search (currently
5 <= chi(plane) <= 7; a finite 6-chromatic unit-distance graph is the
witness that would make history).
"""

import math
from itertools import combinations

TOL = 1e-9


def unit_distance_edges(pts):
    n = len(pts)
    adj = [set() for _ in range(n)]
    for i, j in combinations(range(n), 2):
        d2 = (pts[i][0] - pts[j][0]) ** 2 + (pts[i][1] - pts[j][1]) ** 2
        if abs(d2 - 1.0) < TOL:
            adj[i].add(j)
            adj[j].add(i)
    return adj


def dsatur_chromatic(adj, k_max=8):
    """Exact chromatic number via DSATUR with branch-and-bound (small graphs)."""
    n = len(adj)
    color = [-1] * n
    best = [k_max + 1]

    def bt(v, k):
        if k >= best[0]:
            return
        if v == n:
            best[0] = k
            return
        # order: uncolored vertex with max saturation
        order = sorted(
            (u for u in range(n) if color[u] == -1),
            key=lambda u: -len({color[w] for w in adj[u] if color[w] != -1}),
        )
        u = order[0]
        used = {color[w] for w in adj[u] if color[w] != -1}
        for c in range(k):
            if c not in used:
                color[u] = c
                bt(v + 1, k)
                color[u] = -1
        if k + 1 < best[0]:  # try a new color
            color[u] = k
            bt(v + 1, k + 1)
            color[u] = -1

    for k in range(1, k_max + 1):
        best[0] = k_max + 1
        bt(0, k)
        if best[0] <= k:
            return k
    return None


def moser_spindle():
    # Two rhombi (60°/120°) sharing a vertex; classic 7-vertex construction.
    s3 = math.sqrt(3)
    pts = [
        (0.0, 0.0),
        (1.0, 0.0),
        (1.5, s3 / 2),
        (0.5, s3 / 2),   # rhombus 1: 0,1,2,3 (lozenge with unit sides+short diag)
        # second lozenge hinged at vertex 0, rotated so far vertices are unit apart
    ]
    # rhombus 2: rotate rhombus 1 by angle theta around vertex 0 such that
    # vertex 2 and its image are at distance 1.
    # |R(th) p2 - p2| = 1 with |p2| = sqrt(3) -> th = 2*asin(1/(2*sqrt(3)))
    th = 2 * math.asin(1 / (2 * s3))
    c, s = math.cos(th), math.sin(th)
    for (x, y) in [(1.0, 0.0), (1.5, s3 / 2), (0.5, s3 / 2)]:
        pts.append((c * x - s * y, s * x + c * y))
    return pts


pts = moser_spindle()
adj = unit_distance_edges(pts)
deg = sorted(len(a) for a in adj)
chi = dsatur_chromatic(adj)
print(f"Moser spindle: {len(pts)} vertices, degrees {deg}, chi = {chi}")
assert chi == 4, "Moser spindle must be 4-chromatic!"
print("oracle validated on the canonical 4-chromatic unit-distance graph.")
