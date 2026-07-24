"""
Erdős #993 — search for a tree whose independent-set sequence is not unimodal.

The independent-set polynomial (a.k.a. independence polynomial) of a graph G is
    I(G, x) = sum_{k=0}^{alpha(G)} i_k x^k,
where i_k = number of independent sets of size k.  The conjecture is that every
tree has a unimodal coefficient sequence.

We enumerate all unlabelled trees on n vertices using nauty's `geng -ct`,
parse graph6 strings with networkx, and compute I(G,x) by tree DP.
A counterexample is any tree whose coefficient sequence is not unimodal.

Usage:
    MAX_N=30 .venv/bin/python attempts/scan_993_trees.py
"""

import os
import subprocess
import sys
import time

import networkx as nx


def independence_polynomial_tree(G, root=0):
    """Return list coeffs[k] = # independent k-sets of tree G."""
    # Build rooted tree adjacency (undirected, but parent/child for DP)
    n = G.number_of_nodes()
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

    # DP: dp0[v][k] = # indep sets of size k in subtree of v with v NOT chosen.
    #     dp1[v][k] = # indep sets of size k in subtree of v with v chosen.
    dp0 = {}
    dp1 = {}
    for v in reversed(order):
        # leaf base case
        c0 = [1]  # empty independent set, v excluded
        c1 = [0, 1]  # v chosen -> one set of size 1
        children = [u for u in adj[v] if parent[u] == v]
        if not children:
            dp0[v] = c0
            dp1[v] = c1
            continue
        # merge children
        # start with empty product
        cur0 = [1]
        cur1 = [1]
        from itertools import zip_longest
        for u in children:
            d0 = dp0[u]
            d1 = dp1[u]
            du = [a + b for a, b in zip_longest(d0, d1, fillvalue=0)]
            # cur0 *= du, cur1 *= d0
            new0 = [0] * (len(cur0) + len(du) - 1)
            for i, a in enumerate(cur0):
                if a == 0:
                    continue
                for j, b in enumerate(du):
                    new0[i + j] += a * b
            new1 = [0] * (len(cur1) + len(d0) - 1)
            for i, a in enumerate(cur1):
                if a == 0:
                    continue
                for j, b in enumerate(d0):
                    new1[i + j] += a * b
            cur0 = new0
            cur1 = new1
        dp0[v] = cur0
        # v chosen: shift by 1
        dp1[v] = [0] + cur1
    # root may be chosen or not
    from itertools import zip_longest
    total = [a + b for a, b in zip_longest(dp0[root], dp1[root], fillvalue=0)]
    return total


def is_unimodal(seq):
    """Return True if seq is unimodal (increases then decreases)."""
    if len(seq) <= 2:
        return True
    # Allow initial plateau then strict-ish increase; then decrease.
    i = 0
    while i + 1 < len(seq) and seq[i + 1] >= seq[i]:
        i += 1
    while i + 1 < len(seq) and seq[i + 1] <= seq[i]:
        i += 1
    return i == len(seq) - 1


def check_graph6(g6):
    """Return (coeffs, unimodal) for a graph6 bytes object."""
    G = nx.from_graph6_bytes(g6)
    coeffs = independence_polynomial_tree(G)
    return coeffs, is_unimodal(coeffs)


def main():
    max_n = int(os.environ.get("MAX_N", 25))
    t0 = time.time()
    total_trees = 0
    non_unimodal = 0
    first_example = None
    for n in range(1, max_n + 1):
        if n == 1:
            # single vertex tree
            total_trees += 1
            continue
        if n == 2:
            total_trees += 1
            continue
        proc = subprocess.run(
            ["geng", "-ct", str(n)],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        lines = proc.stdout.splitlines()
        count = 0
        for line in lines:
            if not line:
                continue
            count += 1
            coeffs, uni = check_graph6(line)
            if not uni:
                non_unimodal += 1
                if first_example is None:
                    first_example = (n, line.decode(), coeffs)
                    print(f"COUNTEREXAMPLE n={n} g6={line.decode()} coeffs={coeffs}", flush=True)
        total_trees += count
        print(f"n={n}: {count} trees checked, total non-unimodal so far={non_unimodal} elapsed={time.time()-t0:.1f}s", flush=True)
        if first_example is not None:
            break
    print(f"\ndone: n<={max_n}, total trees={total_trees}, non-unimodal={non_unimodal}")
    if first_example:
        print(f"first counterexample: n={first_example[0]} g6={first_example[1]} coeffs={first_example[2]}")


if __name__ == "__main__":
    main()
