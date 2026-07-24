"""
Erdős #993 — heuristic search v2 for a tree with non-unimodal independence sequence.

Fitness: max over interior k of min(c[k-1], c[k+1]) / c[k].
A value > 1 means a strict local minimum (valley) -> counterexample.
The BrettRey repo reports near-miss ratio ~0.866 on an n=30 tree; we want
> 1.

Search: simulated annealing with small local mutations that preserve tree-ness.
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
    idx = 4
    for _ in range(3):
        a, b = idx, idx + 1
        G.add_edges_from([(v1, a), (a, b)])
        idx += 2
    for _ in range(4):
        a, b = idx, idx + 1
        G.add_edges_from([(v2, a), (a, b)])
        idx += 2
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
    G.add_edges_from([(v1, 4), (4, 5), (5, 6), (6, 7)])
    idx = 8
    for _ in range(2):
        a, b = idx, idx + 1
        G.add_edges_from([(v1, a), (a, b)])
        idx += 2
    for _ in range(3):
        a, b = idx, idx + 1
        G.add_edges_from([(v2, a), (a, b)])
        idx += 2
    for _ in range(4):
        a, b = idx, idx + 1
        G.add_edges_from([(v3, a), (a, b)])
        idx += 2
    return G


def seed_n30():
    path = "attempts/best_roots_tree_n30.json"
    if not os.path.exists(path):
        return None
    with open(path) as f:
        data = json.load(f)
    adj = data.get("best_adj", [])
    G = nx.Graph()
    G.add_nodes_from(range(len(adj)))
    for u, nb in enumerate(adj):
        for v in nb:
            if u < v:
                G.add_edge(u, v)
    return G


def independence_polynomial_tree(G, root=0):
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
    from itertools import zip_longest
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


def fitness(coeffs):
    """Return max_k min(c[k-1], c[k+1]) / c[k].  >1 means valley."""
    best = -float("inf")
    for k in range(1, len(coeffs) - 1):
        if coeffs[k] == 0:
            continue
        r = min(coeffs[k - 1], coeffs[k + 1]) / coeffs[k]
        if r > best:
            best = r
    return best


def is_unimodal(coeffs):
    for k in range(1, len(coeffs) - 1):
        if coeffs[k - 1] > coeffs[k] and coeffs[k + 1] > coeffs[k]:
            return False
    return True


def relabel_tree(G):
    if G.number_of_nodes() == 0 or not nx.is_tree(G) or not nx.is_connected(G):
        return None
    return nx.convert_node_labels_to_integers(G, first_label=0)


def mutate(G, max_n=120):
    """Small local mutation preserving tree-ness."""
    for _ in range(40):
        H = G.copy()
        n = H.number_of_nodes()
        # bias away from growth when near cap
        if n >= max_n:
            op = random.choice(["remove_leaf", "contract_leaf", "rewire_leaf"])
        else:
            op = random.choice(["add_leaf", "remove_leaf", "rewire_leaf",
                                "subdivide_edge", "contract_leaf"])
        if op == "add_leaf":
            v = random.choice(list(H.nodes()))
            H.add_edge(v, n)
        elif op == "remove_leaf":
            leaves = [v for v in H.nodes() if H.degree(v) == 1]
            if len(leaves) <= 3:
                continue
            H.remove_node(random.choice(leaves))
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
            u, v = random.choice(list(H.edges()))
            H.remove_edge(u, v)
            H.add_edges_from([(u, n), (n, v)])
        elif op == "contract_leaf":
            leaves = [v for v in H.nodes() if H.degree(v) == 1]
            if len(leaves) <= 3:
                continue
            H.remove_node(random.choice(leaves))
        H = relabel_tree(H)
        if H is not None:
            return H
    return G


def simulated_annealing(seed, seed_name, max_steps=100000, T0=0.1, cooling=0.9999):
    G = seed
    coeffs = independence_polynomial_tree(G)
    fit = fitness(coeffs)
    best_G, best_coeffs, best_fit = G, coeffs, fit
    T = T0
    t0 = time.time()
    last_print = 0
    print(f"{seed_name}: n={G.number_of_nodes()} initial fitness={fit:.6f} unimodal={is_unimodal(coeffs)}")
    for step in range(1, max_steps + 1):
        cand = mutate(G)
        c_coeffs = independence_polynomial_tree(cand)
        c_fit = fitness(c_coeffs)
        delta = c_fit - fit
        if delta > 0 or random.random() < math.exp(delta / T):
            G, coeffs, fit = cand, c_coeffs, c_fit
            if fit > best_fit:
                best_G, best_coeffs, best_fit = G, coeffs, fit
                if best_fit > 1.0:
                    print(f"COUNTEREXAMPLE at step {step}! n={best_G.number_of_nodes()} fitness={best_fit:.6f}")
                    print(f"coeffs={best_coeffs}")
                    print(f"edges={sorted(best_G.edges())}")
                    return best_G, best_coeffs
        T *= cooling
        if step - last_print >= 2000:
            print(f"{seed_name}: step {step} best_fit={best_fit:.6f} cur_fit={fit:.6f} n={G.number_of_nodes()} T={T:.4f} elapsed={time.time()-t0:.1f}s")
            last_print = step
    print(f"{seed_name}: no counterexample in {max_steps} steps. best_fit={best_fit:.6f} n={best_G.number_of_nodes()}")
    return best_G, best_coeffs


def main():
    random.seed(1)
    seeds = [("T1_3_4_4", seed_t1()), ("T2_3star_3_4", seed_t2())]
    n30 = seed_n30()
    if n30 is not None:
        seeds.append(("n30_near_miss", n30))
    for name, G in seeds:
        simulated_annealing(G, name, max_steps=50000, T0=0.05, cooling=0.99995)


if __name__ == "__main__":
    main()
