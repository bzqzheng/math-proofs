"""
Erdős #287 — search for an Egyptian fraction 1 = sum_{i=1}^k 1/n_i
with 1 < n_1 < ... < n_k and n_{i+1} - n_i <= 2 for all i.
Such a representation would be a counterexample (max gap < 3).
"""
import time
from fractions import Fraction

def search_k(k, n1_max=None):
    """Search for a counterexample with given k."""
    t0 = time.time()
    # n1 must be < k (since k/n1 > sum >= 1)
    if n1_max is None:
        n1_max = k - 1
    # Upper bound on last term: n_k <= n1 + 2(k-1)
    def rec(pos, last, chosen, cur_sum):
        # pos = number of terms chosen so far
        # last = last chosen integer
        # chosen = list of chosen integers
        # cur_sum = Fraction sum so far
        if pos == k:
            if cur_sum == 1:
                return chosen[:]
            return None
        remaining = k - pos
        # next term must be last+1 or last+2 (if pos>0), or n1 if pos==0
        if pos == 0:
            candidates = range(2, n1_max + 1)
        else:
            candidates = [last + 1, last + 2]
        for nxt in candidates:
            new_sum = cur_sum + Fraction(1, nxt)
            if new_sum > 1:
                continue
            # lower bound on sum of remaining terms: each >= nxt+1 (since distinct and gap>=1)
            # but with gap <=2, the smallest possible remaining terms are nxt+1, nxt+2, ...
            # Actually the minimal sum of remaining terms is sum of reciprocals of the next
            # `remaining` integers starting from nxt+1, respecting gaps <=2.
            # The smallest possible are nxt+1, nxt+2, ..., nxt+remaining.
            min_remaining = sum(Fraction(1, nxt + j) for j in range(1, remaining + 1))
            if new_sum + min_remaining > 1:
                continue
            # upper bound: take the largest possible remaining terms, nxt+2, nxt+4, ...
            # but that's not a useful upper bound for pruning (sum smaller).
            # Instead, check that we can still reach 1 with remaining terms.
            # The max sum with remaining terms is when they are as small as possible, already used.
            # So only lower-bound pruning helps.
            res = rec(pos + 1, nxt, chosen + [nxt], new_sum)
            if res:
                return res
        return None

    return rec(0, 0, [], Fraction(0,1)), time.time() - t0

def main():
    for k in range(2, 41):
        sol, elapsed = search_k(k)
        if sol:
            print(f"COUNTEREXAMPLE k={k}: {sol} elapsed={elapsed:.2f}s")
            return
        print(f"k={k}: no counterexample elapsed={elapsed:.2f}s", flush=True)

if __name__ == "__main__":
    main()
