#!/usr/bin/env python3
"""
grimm_reference.py — slow, obviously-correct reference + mandatory oracle
gates for grimm.c (Erdős #375, Grimm's conjecture).

Reference semantics (no reduction anywhere in the "full" path):
  * full_assignment(a, b): factor EVERY member with sympy.factorint, build
    the complete bipartite graph members x (all prime divisors), solve with
    Hopcroft–Karp, and validate the returned assignment (distinct primes,
    each dividing its member). This is the conjecture tested directly.
  * reduced_check(a, b): the reduction — divide each member by ALL primes
    <= k (k = block length); members with cofactor 1 are the constrained
    (k-smooth) ones; match them into the primes <= k. Must agree with the
    full path (gate b checks this on every block <= 1e6) and with the C
    engine (on every block <= 1e7).

Gates (I5/I12 discipline — all must pass before any production run):
  gate a  known-positive: HK unit-tested vs brute force on random tiny
          graphs; block 8..10 yields exactly {8:2, 9:3, 10:5}; tricky
          blocks containing prime powers (2^13=8192; 121=11^2, 125=5^3 in
          114..126; 529=23^2 in 524..540) verified by full matching, and
          full == reduced on each.
  gate b  exact agreement: C engine vs this reference on ALL blocks below
          1e7 (block-by-block OK/FAIL + identical smooth-member and match
          counts); additionally the reduction itself is validated against
          full sympy matchings on ALL blocks below 1e6.
  gate c  gap cross-check: engine record-gap lines below 1e9 must equal
          the hardcoded OEIS A000230/A005250 first-occurrence table.

Usage:
  python grimm_reference.py gate        # all gates (builds engine if needed)
  python grimm_reference.py a|b|c       # a single gate
  python grimm_reference.py block A B   # debug: print full assignment for A..B
"""

import os
import random
import re
import subprocess
import sys
import time
from collections import deque

from sympy import factorint, nextprime, prevprime, primerange

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(HERE, "grimm")
ENGINE_SRC = os.path.join(HERE, "grimm.c")

sys.setrecursionlimit(100000)

SMALL_PRIMES = list(primerange(2, 70000))  # covers every k <= 65536 (KCAP)

# OEIS A000230 (prime p starting a record gap) x A005250 (the gap), p < 1e9.
A005250_BELOW_1E9 = [
    (3, 2), (7, 4), (23, 6), (89, 8), (113, 14), (523, 18), (887, 20),
    (1129, 22), (1327, 34), (9551, 36), (15683, 44), (19609, 52),
    (31397, 72), (155921, 86), (360653, 96), (370261, 112), (492113, 114),
    (1349533, 118), (1357201, 132), (2010733, 148), (4652353, 154),
    (17051707, 180), (20831323, 210), (47326693, 220), (122164747, 222),
    (189695659, 234), (191912783, 248), (387096133, 250), (436273009, 282),
]

BLOCK_RE = re.compile(r"^block: a=(\d+) b=(\d+) k=(\d+) smooth=(\d+) match=(\d+) ok=(\d+)")
GAP_RE = re.compile(r"record-gap: p=(\d+) gap=(\d+)")


# ---------------------------------------------------------------- matching

def hopcroft_karp(adj, n_right):
    """Max bipartite matching. adj[u] = list of right nodes. Returns
    (matching_size, match_l) with match_l[u] = right node or -1."""
    n_left = len(adj)
    match_l = [-1] * n_left
    match_r = [-1] * n_right

    def bfs():
        dist = [-1] * n_left
        dq = deque()
        for u in range(n_left):
            if match_l[u] < 0:
                dist[u] = 0
                dq.append(u)
        found = False
        while dq:
            u = dq.popleft()
            for v in adj[u]:
                w = match_r[v]
                if w < 0:
                    found = True
                elif dist[w] < 0:
                    dist[w] = dist[u] + 1
                    dq.append(w)
        return found, dist

    def dfs(u, dist):
        for v in adj[u]:
            w = match_r[v]
            if w < 0 or (dist[w] == dist[u] + 1 and dfs(w, dist)):
                match_l[u] = v
                match_r[v] = u
                return True
        dist[u] = -1
        return False

    matching = 0
    while True:
        found, dist = bfs()
        if not found:
            break
        for u in range(n_left):
            if match_l[u] < 0 and dfs(u, dist):
                matching += 1
    return matching, match_l


def brute_max_matching(adj, n_right):
    """Exponential brute force (tiny graphs only): max number of left nodes
    matchable to distinct right nodes."""
    used = [False] * n_right

    def go(u):
        if u == len(adj):
            return 0
        best = go(u + 1)  # leave u unmatched
        for v in adj[u]:
            if not used[v]:
                used[v] = True
                best = max(best, 1 + go(u + 1))
                used[v] = False
        return best

    return go(0)


# ------------------------------------------------------- reference oracles

def full_assignment(a, b):
    """Direct test of the conjecture on block a..b: sympy factorization of
    every member, complete bipartite graph, exact matching. Returns a
    validated dict {member: prime} or None if no assignment exists."""
    members = list(range(a, b + 1))
    facs = {m: sorted(factorint(m)) for m in members}
    primes = sorted({p for fs in facs.values() for p in fs})
    idx = {p: i for i, p in enumerate(primes)}
    adj = [[idx[p] for p in facs[m]] for m in members]
    matching, match_l = hopcroft_karp(adj, len(primes))
    if matching < len(members):
        return None
    asg = {m: primes[v] for m, v in zip(members, match_l)}
    # validate: distinct primes, each dividing its member
    assert len(set(asg.values())) == len(members)
    for m, p in asg.items():
        assert m % p == 0
    return asg


def reduced_check(a, b):
    """The reduction: only k-smooth members are constrained. Returns
    (ok, n_smooth, n_matched)."""
    k = b - a + 1
    pk = [p for p in SMALL_PRIMES if p <= k]
    smooth = []
    for m in range(a, b + 1):
        rem, fs = m, []
        for p in pk:
            if rem == 1:
                break
            if rem % p == 0:
                fs.append(p)
                while rem % p == 0:
                    rem //= p
        if rem == 1:
            smooth.append(fs)
    if not smooth:
        return True, 0, 0
    idx = {p: i for i, p in enumerate(pk)}
    adj = [[idx[p] for p in fs] for fs in smooth]
    matching, _ = hopcroft_karp(adj, len(pk))
    return matching == len(smooth), len(smooth), matching


def blocks_upto(n):
    """Maximal composite runs (a, b) closed by a prime <= n — exactly the
    blocks the C engine reports with N_MAX=n."""
    ps = list(primerange(2, n + 1))
    for prev, p in zip(ps, ps[1:]):
        if p - prev >= 2:
            yield prev + 1, p - 1


# ------------------------------------------------------------------ engine

def ensure_engine():
    if (not os.path.exists(ENGINE)) or os.path.getmtime(ENGINE_SRC) > os.path.getmtime(ENGINE):
        print("building engine: clang -O3 -o grimm grimm.c -lm", flush=True)
        subprocess.run(["clang", "-O3", "-o", ENGINE, ENGINE_SRC, "-lm"],
                       check=True, cwd=HERE)


def run_engine(n_max, n_start=2, dump_blocks=False, timeout=3600):
    env = dict(os.environ)
    env["N_MAX"] = str(n_max)
    env["N_START"] = str(n_start)
    if dump_blocks:
        env["DUMP_BLOCKS"] = "1"
    r = subprocess.run([ENGINE], env=env, capture_output=True, text=True,
                       timeout=timeout, cwd=HERE)
    if "FATAL" in r.stderr:
        raise RuntimeError(f"engine stderr: {r.stderr}")
    return r.stdout


# -------------------------------------------------------------------- gates

def gate_a():
    t0 = time.time()
    # a.1: Hopcroft–Karp must be exact — unit test vs brute force.
    rng = random.Random(375)
    for _ in range(300):
        nl, nr = rng.randint(1, 7), rng.randint(1, 7)
        adj = [[v for v in range(nr) if rng.random() < 0.4] for _ in range(nl)]
        m_hk, _ = hopcroft_karp([row[:] for row in adj], nr)
        m_bf = brute_max_matching(adj, nr)
        assert m_hk == m_bf, (adj, nr, m_hk, m_bf)
    print("gate a.1 OK: hopcroft-karp == brute force on 300 random tiny graphs",
          flush=True)

    # a.2: the canonical known-positive block.
    asg = full_assignment(8, 10)
    assert asg == {8: 2, 9: 3, 10: 5}, asg
    print("gate a.2 OK: block 8..10 assignment is exactly {8:2, 9:3, 10:5}",
          flush=True)

    # a.3: tricky known-positive blocks; full (sympy, direct) must agree
    # with the reduction on each.
    tricky = [114, 524, 8192]
    for center in tricky:
        a, b = prevprime(center) + 1, nextprime(center) - 1
        asg = full_assignment(a, b)
        assert asg is not None, f"full matching FAILED on {a}..{b}"
        ok, s, m = reduced_check(a, b)
        assert ok and m == s, f"reduced matching FAILED on {a}..{b}"
        print(f"gate a.3 OK: block {a}..{b} (k={b - a + 1}) full==reduced, "
              f"smooth={s}", flush=True)
        if center == 114:
            assert asg[121] == 11 and asg[125] == 5  # prime powers: one option
        if center == 524:
            assert asg[529] == 23  # 23^2, non-smooth (23 > k=17): private prime
        if center == 8192:
            assert asg[8192] == 2 and s == 1  # 2^13 is the ONLY smooth member
    print(f"gate a PASSED ({time.time() - t0:.1f}s)\n", flush=True)


def gate_b(n_engine=10_000_000, n_full=1_000_000):
    t0 = time.time()
    ensure_engine()
    out = run_engine(n_engine, dump_blocks=True)
    eng = {}
    for line in out.splitlines():
        mm = BLOCK_RE.match(line)
        if mm:
            a, b, k, s, match, ok = mm.groups()
            eng[int(a)] = (int(b), int(k), int(s), int(match), int(ok))
        assert "CANDIDATE" not in line, line
    n_cmp = n_full_checked = 0
    for a, b in blocks_upto(n_engine):
        ok, s, m = reduced_check(a, b)
        e = eng.pop(a, None)
        assert e is not None and e[0] == b, f"block enumeration mismatch at a={a}"
        assert (e[2], e[3], e[4]) == (s, m, int(ok)), (
            f"engine vs reference mismatch on {a}..{b}: engine={e}, ref=({s},{m},{ok})")
        n_cmp += 1
        if b <= n_full:
            assert (full_assignment(a, b) is not None) == ok, (
                f"reduction mismatch on {a}..{b}: full={not ok}")
            n_full_checked += 1
    assert not eng, f"engine reported {len(eng)} extra blocks"
    print(f"gate b OK: {n_cmp} blocks below 1e7 agree block-by-block "
          f"(OK/FAIL + smooth + match counts); {n_full_checked} blocks below 1e6 "
          f"additionally agree with full sympy matchings", flush=True)
    print(f"gate b PASSED ({time.time() - t0:.1f}s)\n", flush=True)


def gate_c(n_max=1_000_000_000):
    t0 = time.time()
    ensure_engine()
    out = run_engine(n_max)
    recs = [(int(p), int(g)) for p, g in GAP_RE.findall(out)]
    assert recs == A005250_BELOW_1E9, (
        "record gaps below 1e9 differ from OEIS A000230/A005250:\n"
        f"engine={recs}\ntable ={A005250_BELOW_1E9}")
    assert "CANDIDATE" not in out, "counterexample candidate below 1e9?!"
    done = [ln for ln in out.splitlines() if ln.startswith("done:")]
    print(f"gate c OK: all {len(recs)} record prime gaps below 1e9 match "
          f"OEIS A000230/A005250; no counterexamples. engine {done[0] if done else ''}",
          flush=True)
    print(f"gate c PASSED ({time.time() - t0:.1f}s)\n", flush=True)


def gate():
    t0 = time.time()
    gate_a()
    gate_b()
    gate_c()
    print(f"ALL GATES PASSED (total {time.time() - t0:.1f}s)", flush=True)


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] == "gate":
        gate()
    elif args[0] in ("a", "b", "c"):
        {"a": gate_a, "b": gate_b, "c": gate_c}[args[0]]()
    elif args[0] == "block" and len(args) == 3:
        a, b = int(args[1]), int(args[2])
        print(full_assignment(a, b) or f"NO ASSIGNMENT for {a}..{b}")
    else:
        sys.exit(__doc__)
