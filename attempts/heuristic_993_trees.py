"""
Erdős #993 — heuristic search for a tree with non-unimodal independence sequence.

Seeds: the two n=26 trees from Kadrawi–Levit (2023) with non-log-concave
independence polynomials (still unimodal), and the n=30 near-miss from the
BrettRey/erdos-problem-993 repo.

Search operators (all preserve tree-ness):
- add_leaf(v): attach a new leaf to vertex v.
- remove_leaf(): delete a random leaf (not on a seed-essential path).
- rewire_leaf(): detach a leaf and re-attach elsewhere.
- subdivide_edge(u,v): replace edge uv with u-w-v where w is new.
- contract_leaf_edge(): contract an edge incident to a leaf.

Fitness rewards deep valleys in the coefficient sequence.
A counterexample = fitness < 0 (i.e. a local minimum exists).
"""

import copy
import json
import math
import os
import random
import sys
import time

import networkx as nx


def seed_t1():
    """3,k,k structure with k=4 (n=26)."""
    G = nx.Graph()
    G.add_nodes_from(range(26))
    center, v1, v2, v3 = 0, 1, 2, 3
    G.add_edges_from([(center, v1), (center, v2), (center, v3)])
    # v1: three K2's
    idx = 4
    for _ in range(3):
        a, b = idx, idx + 1
        G.add_edges_from([(v1, a), (a, b)])
        idx += 2
    # v2: four K2's
    for _ in range(4):
        a, b = idx, idx + 1
        G.add_edges_from([(v2, a), (a, b)])
        idx += 2
    # v3: four K2's
    for _ in range(4):
        a, b = idx, idx + 1
        G.add_edges_from([(v3, a), (a, b)])
        idx += 2
    return G


def seed_t2():
    """3*,k,k+1 structure with k=3 (n=26)."""
    G = nx.Graph()
    G.add_nodes_from(range(26))
    center, v1, v2, v3 = 0, 1, 2, 3
    G.add_edges_from([(center, v1), (center, v2), (center, v3)])
    idx = 4
    # v1: P4 (4-5-6-7)
    G.add_edges_from([(v1, 4), (4, 5), (5, 6), (6, 7)])
    idx = 8
    # v1: two K2's
    for _ in range(2):
        a, b = idx, idx + 1
        G.add_edges_from([(v1, a), (a, b)])
        idx += 2
    # v2: three K2's
    for _ in range(3):
        a, b = idx, idx + 1
        G.add_edges_from([(v2, a), (a, b)])
        idx += 2
    # v3: four K2's
    for _ in range(4):
        a, b = idx, idx + 1
        G.add_edges_from([(v3, a), (a, b)])
        idx += 2
    return G


def seed_n30_from_json():
    """Load the n=30 near-miss from BrettRey's repo if available locally."""
    path = "attempts/best_roots_tree_n30.json"
    if not os.path.exists(path):
        return None
    with open(path) as f:
        data = json.load(f)
    adj = data.get("best_adj", [])
    n = len(adj)
    G = nx.Graph()
    G.add_nodes_from(range(n))
    for u, nb in enumerate(adj):
        for v in nb:
            if u < v:
                G.add_edge(u, v)
    return G


def independence_polynomial_tree(G, root=0):
    """Return list coeffs[k] = # independent k-sets of tree G."""
    n = G.number_of_nodes()
    if n == 0:
        return [1]
    # reindex nodes to 0..n-1 if needed
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

    dp0 = {}
    dp1 = {}
    for v in reversed(order):
        children = [u for u in adj[v] if parent[u] == v]
        cur0 = [1]
        cur1 = [1]
        for u in children:
            du = [a + b for a, b in zip(dp0[u], dp1[u])]
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
            cur0 = new0
            cur1 = new1
        dp0[v] = cur0
        dp1[v] = [0] + cur1
    total = [a + b for a, b in zip(dp0[root], dp1[root])]
    return total


def valley_depth(coeffs):
    """
    Return the deepest valley in the coefficient sequence.
    A valley at position k means coeffs[k-1] > coeffs[k] < coeffs[k+1].
    Depth = min(coeffs[k-1]-coeffs[k], coeffs[k+1]-coeffs[k]).
    Return -depth if a valley exists, otherwise 0 (and positive means no valley).
    """
    best = 0.0
    has_valley = False
    for k in range(1, len(coeffs) - 1):
        if coeffs[k - 1] > coeffs[k] and coeffs[k + 1] > coeffs[k]:
            d = min(coeffs[k - 1] - coeffs[k], coeffs[k + 1] - coeffs[k])
            if d > best:
                best = d
                has_valley = True
    if not has_valley:
        # no valley: return a positive score measuring how close to a valley
        # we are.  We want to minimize this.
        min_deficit = float("inf")
        for k in range(1, len(coeffs) - 1):
            deficit = max(0, coeffs[k] - coeffs[k - 1]) + max(0, coeffs[k] - coeffs[k + 1])
            if deficit < min_deficit:
                min_deficit = deficit
        return min_deficit if min_deficit != float("inf") else 1.0
    return -best


def is_unimodal(coeffs):
    for k in range(1, len(coeffs) - 1):
        if coeffs[k - 1] > coeffs[k] and coeffs[k + 1] > coeffs[k]:
            return False
    return True


def relabel_tree(G):
    """Relabel nodes to 0..n-1 and return connected tree (or None)."""
    if not nx.is_tree(G) or not nx.is_connected(G):
        return None
    return nx.convert_node_labels_to_integers(G, first_label=0)


def mutate(G, max_retry=10):
    """Apply one random mutation preserving tree-ness."""
    for _ in range(max_retry):
        H = G.copy()
        n = H.number_of_nodes()
        op = random.choice(["add_leaf", "remove_leaf", "rewire_leaf",
                            "subdivide_edge", "contract_leaf"])

        if op == "add_leaf":
            v = random.choice(list(H.nodes()))
            new_node = n
            H.add_edge(v, new_node)

        elif op == "remove_leaf":
            leaves = [v for v in H.nodes() if H.degree(v) == 1]
            if len(leaves) <= 3:
                continue
            v = random.choice(leaves)
            H.remove_node(v)

        elif op == "rewire_leaf":
            leaves = [v for v in H.nodes() if H.degree(v) == 1]
            if not leaves:
                continue
            leaf = random.choice(leaves)
            parent = next(iter(H.neighbors(leaf)))
            H.remove_edge(parent, leaf)
            new_parent = random.choice([v for v in H.nodes() if v != leaf])
            H.add_edge(new_parent, leaf)
            if not nx.is_tree(H):
                continue

        elif op == "subdivide_edge":
            edges = list(H.edges())
            if not edges:
                continue
            u, v = random.choice(edges)
            H.remove_edge(u, v)
            new_node = n
            H.add_edges_from([(u, new_node), (new_node, v)])

        elif op == "contract_leaf":
            leaves = [v for v in H.nodes() if H.degree(v) == 1]
            if len(leaves) <= 3:
                continue
            leaf = random.choice(leaves)
            H.remove_node(leaf)

        H = relabel_tree(H)
        if H is not None:
            return H
    return G


def local_search(seed, max_steps=100000, seed_name="seed"):
    best_G = seed
    best_coeffs = independence_polynomial_tree(best_G)
    best_fit = valley_depth(best_coeffs)
    print(f"{seed_name}: n={seed.number_of_nodes()} initial fitness={best_fit:.2f} unimodal={is_unimodal(best_coeffs)}")
    t0 = time.time()
    last_print = 0
    for step in range(1, max_steps + 1):
        cand = mutate(best_G)
        coeffs = independence_polynomial_tree(cand)
        fit = valley_depth(coeffs)
        # accept if strictly better, or with small probability if equal/worse
        if fit < best_fit or (fit == best_fit and random.random() < 0.1):
            best_G = cand
            best_coeffs = coeffs
            best_fit = fit
            if not is_unimodal(best_coeffs):
                print(f"COUNTEREXAMPLE at step {step}! n={best_G.number_of_nodes()} coeffs={best_coeffs}")
                print(f"edges={sorted(best_G.edges())}")
                return best_G, best_coeffs
        if step - last_print >= 1000:
            print(f"{seed_name}: step {step} best_fit={best_fit:.2f} n={best_G.number_of_nodes()} elapsed={time.time()-t0:.1f}s")
            last_print = step
    print(f"{seed_name}: no counterexample in {max_steps} steps. best_fit={best_fit:.2f} n={best_G.number_of_nodes()}")
    return best_G, best_coeffs


def main():
    random.seed(0)
    seeds = [("T1_3_4_4", seed_t1()), ("T2_3star_3_4", seed_t2())]
    n30 = seed_n30_from_json()
    if n30 is not None:
        seeds.append(("n30_near_miss", n30))
    for name, G in seeds:
        local_search(G, max_steps=20000, seed_name=name)


if __name__ == "__main__":
    main()
