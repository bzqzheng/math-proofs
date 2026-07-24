"""
Erdős #993 — scan the Kadrawi–Levit infinite families for a non-unimodal tree.

Families:
  3,k,k+j : center v0 -> v1,v2,v3; v1 has three K2's; v2 has k K2's;
            v3 has (k+j) K2's.  Order n = 10 + 4k + 2j.
  3*,k,k+j: center v0 -> v1,v2,v3; v1 has P4 ∪ K2 ∪ K2;
            v2 has k K2's; v3 has (k+j) K2's.  Order n = 14 + 4k + 2j.

For each family, scan a range of (k,j) and report the first non-unimodal tree.
"""

import os
import sys
import time

from itertools import zip_longest
import networkx as nx


def ip_tree(G, root=0):
    n = G.number_of_nodes()
    if n == 0:
        return [1]
    adj = {v: set(G.neighbors(v)) for v in G.nodes()}
    parent = {root: None}
    order = [root]
    stack = [root]
    while stack:
        v = stack.pop()
        for u in adj[v]:
            if u not in parent:
                parent[u] = v
                order.append(u)
                stack.append(u)
    dp0, dp1 = {}, {}
    for v in reversed(order):
        children = [u for u in adj[v] if parent[u] == v]
        cur0, cur1 = [1], [1]
        for u in children:
            du = [a + b for a, b in zip_longest(dp0[u], dp1[u], fillvalue=0)]
            new0 = [0] * (len(cur0) + len(du) - 1)
            for i, a in enumerate(cur0):
                if a == 0:
                    continue
                for j, b in enumerate(du):
                    new0[i + j] += a * b
            new1 = [0] * (len(cur1) + len(dp0[u]) - 1)
            for i, a in enumerate(cur1):
                if a == 0:
                    continue
                for j, b in enumerate(dp0[u]):
                    new1[i + j] += a * b
            cur0, cur1 = new0, new1
        dp0[v] = cur0
        dp1[v] = [0] + cur1
    return [a + b for a, b in zip_longest(dp0[root], dp1[root], fillvalue=0)]


def is_unimodal(coeffs):
    for k in range(1, len(coeffs) - 1):
        if coeffs[k - 1] > coeffs[k] and coeffs[k + 1] > coeffs[k]:
            return False
    return True


def make_3_k_kj(k, j):
    """3,k,k+j family."""
    n = 10 + 4 * k + 2 * j
    G = nx.Graph()
    G.add_nodes_from(range(n))
    center, v1, v2, v3 = 0, 1, 2, 3
    G.add_edges_from([(center, v1), (center, v2), (center, v3)])
    idx = 4
    for _ in range(3):
        a, b = idx, idx + 1
        G.add_edges_from([(v1, a), (a, b)])
        idx += 2
    for _ in range(k):
        a, b = idx, idx + 1
        G.add_edges_from([(v2, a), (a, b)])
        idx += 2
    for _ in range(k + j):
        a, b = idx, idx + 1
        G.add_edges_from([(v3, a), (a, b)])
        idx += 2
    return G


def make_3star_k_kj(k, j):
    """3*,k,k+j family."""
    n = 14 + 4 * k + 2 * j
    G = nx.Graph()
    G.add_nodes_from(range(n))
    center, v1, v2, v3 = 0, 1, 2, 3
    G.add_edges_from([(center, v1), (center, v2), (center, v3)])
    # v1: P4 (4-5-6-7)
    G.add_edges_from([(v1, 4), (4, 5), (5, 6), (6, 7)])
    idx = 8
    # v1: two K2's
    for _ in range(2):
        a, b = idx, idx + 1
        G.add_edges_from([(v1, a), (a, b)])
        idx += 2
    for _ in range(k):
        a, b = idx, idx + 1
        G.add_edges_from([(v2, a), (a, b)])
        idx += 2
    for _ in range(k + j):
        a, b = idx, idx + 1
        G.add_edges_from([(v3, a), (a, b)])
        idx += 2
    return G


def main():
    K_MAX = int(os.environ.get("K_MAX", 50))
    J_MAX = int(os.environ.get("J_MAX", 20))
    t0 = time.time()
    checked = 0
    best_near_miss = 0.0
    best_params = None
    for family, maker in [("3,k,k+j", make_3_k_kj), ("3*,k,k+j", make_3star_k_kj)]:
        for k in range(1, K_MAX + 1):
            for j in range(0, J_MAX + 1):
                G = maker(k, j)
                coeffs = ip_tree(G)
                checked += 1
                # near-miss ratio
                nm = 0.0
                for idx in range(1, len(coeffs) - 1):
                    if coeffs[idx] == 0:
                        continue
                    r = min(coeffs[idx - 1], coeffs[idx + 1]) / coeffs[idx]
                    if r > nm:
                        nm = r
                if nm > best_near_miss:
                    best_near_miss = nm
                    best_params = (family, k, j, G.number_of_nodes())
                if not is_unimodal(coeffs):
                    print(f"COUNTEREXAMPLE {family} k={k} j={j} n={G.number_of_nodes()}")
                    print(f"coeffs={coeffs}")
                    print(f"checked={checked} elapsed={time.time()-t0:.1f}s")
                    return
    print(f"No counterexample in {checked} family members up to k={K_MAX}, j={J_MAX}.")
    print(f"Best near-miss ratio {best_near_miss:.6f} at {best_params}")
    print(f"elapsed={time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
