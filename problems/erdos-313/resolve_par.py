"""Parallel resolver for t=2 nodes deferred by the C engine (factoring route)."""
import sys, re, os
from multiprocessing import Pool
from gmpy2 import mpz, is_prime
from ppn2 import factorize, divisors_from


def parse(line):
    why, rest = line.split(" ", 1)
    t = int(re.search(r"t=(\d+)", rest).group(1))
    P = [int(x) for x in re.search(r"P=([\d,]*)", rest).group(1).split(",") if x]
    N = mpz(re.search(r"N=(\d+)", rest).group(1))
    A = mpz(re.search(r"A=(\d+)", rest).group(1))
    return why, t, P, N, A


def work(line):
    why, t, P, N, A = parse(line)
    if t != 2:
        return ("UNRESOLVED", line)
    m = P[-1] if P else 1
    M = N*N + A
    out = []
    for u in divisors_from(factorize(M)):
        if u*u > M:
            break
        if (u + N) % A:
            continue
        q1 = (u + N)//A
        if q1 <= m or not is_prime(q1):
            continue
        v = M//u
        if (v + N) % A:
            continue
        q2 = (v + N)//A
        if q2 > q1 and is_prime(q2):
            out.append(P + [int(q1), int(q2)])
    return ("OK", out)


if __name__ == "__main__":
    lines = [l.strip() for l in open(sys.argv[1]) if l.strip()]
    nproc = int(sys.argv[2]) if len(sys.argv) > 2 else os.cpu_count()
    nsol = 0; unres = 0
    with Pool(nproc) as pool:
        for i, (tag, res) in enumerate(pool.imap_unordered(work, lines, chunksize=8)):
            if tag == "UNRESOLVED":
                unres += 1; print("UNRESOLVED:", res, flush=True)
            else:
                for s in res:
                    nsol += 1
                    n = 1
                    for x in s:
                        n *= x
                    print(f"*** SOLUTION: {s}  n={n}", flush=True)
            if (i+1) % 2000 == 0:
                print(f"  ..{i+1}/{len(lines)}", file=sys.stderr, flush=True)
    print(f"resolved {len(lines)} deferrals: solutions={nsol} unresolved={unres}")
