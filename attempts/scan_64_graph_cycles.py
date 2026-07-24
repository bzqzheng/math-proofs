"""
Erdős #64 — search for a finite graph with min degree >= 3 and no cycle of
length 2^k for any k >= 2 (no 4-cycle, 8-cycle, 16-cycle, ...).

Strategy: enumerate connected cubic graphs by n, build a cycle basis, then
enumerate all simple cycles as XOR-sums of basis cycles and record their
lengths. A graph is a counterexample iff its minimum degree is >= 3 and no
cycle length is a power of two >= 4.

For efficiency we use Brendan McKay's graph catalog if available; otherwise
a backtracking cubic-graph generator for small n.
"""

import itertools
import os
import sys

import networkx as nx


def is_power_of_two(k):
    return k > 0 and (k & (k - 1)) == 0


def simple_cycle_lengths(G):
    """Yield lengths of all simple cycles in G via cycle-basis enumeration."""
    if G.number_of_nodes() == 0:
        return
    basis = nx.cycle_basis(G)
    if not basis:
        return

    # Convert each basis cycle to edge-frozenset for symmetric-difference.
    basis_edges = [frozenset(map(frozenset, zip(cyc, cyc[1:] + [cyc[0]]))) for cyc in basis]

    seen = set()
    for mask in range(1, 1 << len(basis_edges)):
        # symmetric difference of selected cycles
        edges = frozenset()
        for i in range(len(basis_edges)):
            if mask & (1 << i):
                edges = edges.symmetric_difference(basis_edges[i])
        if not edges or edges in seen:
            continue
        seen.add(edges)
        H = nx.Graph()
        H.add_edges_from((tuple(e) for e in edges))
        # A simple cycle is connected and 2-regular.
        if H.number_of_edges() == H.number_of_nodes() and all(d == 2 for _, d in H.degree()):
            yield H.number_of_nodes()


def is_counterexample(G):
    if not G.nodes():
        return False
    if min(dict(G.degree()).values()) < 3:
        return False
    for L in simple_cycle_lengths(G):
        if L >= 4 and is_power_of_two(L):
            return False
    return True


def cubic_graphs_backtrack(n):
    """Generate connected cubic simple graphs on n labelled vertices (n even, n>=4)."""
    if n % 2 == 1 or n < 4:
        return
    adj = [set() for _ in range(n)]
    half_edges = [[] for _ in range(n)]

    def canonical(G):
        # Very weak canonical form — just sort degrees and adjacency lists.
        # Mainly to skip some duplicates; we don't rely on it for correctness.
        return tuple(tuple(sorted(nei)) for nei in G)

    seen = set()

    def extend(v):
        if v == n:
            # all vertices degree 3
            if all(len(adj[i]) == 3 for i in range(n)):
                sig = canonical(adj)
                if sig not in seen:
                    seen.add(sig)
                    G = nx.Graph()
                    G.add_nodes_from(range(n))
                    for i in range(n):
                        for j in adj[i]:
                            if i < j:
                                G.add_edge(i, j)
                    if nx.is_connected(G):
                        yield G
            return
        need = 3 - len(adj[v])
        if need < 0:
            return
        if need == 0:
            yield from extend(v + 1)
            return
        # choose `need` neighbors from vertices > v with degree < 3
        candidates = [u for u in range(v + 1, n) if len(adj[u]) < 3 and u not in adj[v]]
        if len(candidates) < need:
            return
        for chosen in itertools.combinations(candidates, need):
            for u in chosen:
                adj[v].add(u)
                adj[u].add(v)
            yield from extend(v)
            for u in chosen:
                adj[v].remove(u)
                adj[u].remove(v)

    yield from extend(0)


def main():
    max_n = int(os.environ.get("MAX_N", 16))
    for n in range(4, max_n + 1, 2):
        print(f"n={n}", flush=True)
        count = 0
        found = 0
        for G in cubic_graphs_backtrack(n):
            count += 1
            if is_counterexample(G):
                found += 1
                print(f"*** COUNTEREXAMPLE n={n} edges={sorted(G.edges())}", flush=True)
        print(f"  checked {count} connected cubic graphs, counterexamples={found}", flush=True)
        if found:
            break


if __name__ == "__main__":
    main()
