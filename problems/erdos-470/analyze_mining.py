#!/usr/bin/env python3
"""Near-miss mining analysis for Erdos #470 (compounding substrate).

Reads problems/erdos-470/mining/*.log (CAND n delta [(p,a),...] lines from
DUMP=1 runs), dedupes by n, and produces:

  1. candidates.csv.gz  — full dataset: n, delta, omega, abundancy_minus_2, region
  2. delta-distribution stats (overall + per region)
  3. near-miss metrics for the --metrics-top candidates with smallest delta:
     for each, run-length of consecutive expressible values ending at delta
     (weird candidates have run-length 0; 1-2 = near-miss) and the expressible
     count in the window [delta-999, delta].
  4. MINING-report.md — summary tables.

Usage: python analyze_mining.py [--metrics-top N]   (default N=50000)
"""
import gzip
import os
import re
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
MINING = os.path.join(HERE, "mining")

CAND_RE = re.compile(r"^CAND (\d+) (\d+) \[([^\]]*)\]")
FAC_RE = re.compile(r"\((\d+), (\d+)\)")


def proper_divisors(fac, n):
    divs = [1]
    for p, a in fac:
        divs = [d * p ** e for d in divs for e in range(a + 1)]
    return [d for d in divs if d < n]


def near_miss(n, delta, divs):
    mask = (1 << (delta + 1)) - 1  # cap the bitset at delta (else shifts explode)
    bits = 1
    for d in divs:
        if d <= delta:
            bits = (bits | (bits << d)) & mask
    # expressible count in [delta-999, delta]
    lo = max(0, delta - 999)
    window = (bits >> lo) & ((1 << 1000) - 1)
    wcount = bin(window).count("1")
    # run-length of consecutive expressible values ending at delta
    run = 0
    b = (bits >> delta) & 1
    if b:
        run = 1
        x = delta - 1
        while x >= 0 and (bits >> x) & 1:
            run += 1
            x -= 1
    return wcount, run


def main():
    metrics_top = 50000
    if "--metrics-top" in sys.argv:
        metrics_top = int(sys.argv[sys.argv.index("--metrics-top") + 1])

    cand = {}  # n -> (delta, fac, region)
    for fn in sorted(os.listdir(MINING)):
        if not fn.endswith(".log"):
            continue
        region = fn[:-4]
        with open(os.path.join(MINING, fn)) as f:
            for line in f:
                m = CAND_RE.match(line)
                if not m:
                    continue
                n = int(m.group(1))
                if n in cand:
                    continue
                delta = int(m.group(2))
                fac = [(int(p), int(a)) for p, a in FAC_RE.findall(m.group(3))]
                cand[n] = (delta, fac, region)
    rows = sorted((n, d, len(f), f, r) for n, (d, f, r) in cand.items())
    print(f"candidates (deduped): {len(rows)}")

    # ---- dataset ----
    out_csv = os.path.join(HERE, "candidates.csv.gz")
    with gzip.open(out_csv, "wt") as g:
        g.write("n,delta,omega,abundancy_minus_2,region\n")
        for n, d, omega, fac, region in rows:
            g.write(f"{n},{d},{omega},{d / n:.6e},{region}\n")
    print(f"wrote {out_csv} ({os.path.getsize(out_csv) / 1e6:.1f} MB)")

    # ---- delta distribution ----
    ds = sorted(d for _, d, _, _, _ in rows)
    n_rows = len(ds)
    def pct(q):
        return ds[min(n_rows - 1, int(q * n_rows))]
    print(f"delta: min={ds[0]} p25={pct(.25)} median={pct(.5)} p75={pct(.75)} "
          f"p99={pct(.99)} max={ds[-1]}")
    by_region = defaultdict(list)
    for n, d, omega, fac, region in rows:
        by_region[region].append((n, d))
    print("\nper-region (top 10 by count):")
    for region, lst in sorted(by_region.items(), key=lambda kv: -len(kv[1]))[:10]:
        rds = sorted(d for _, d in lst)
        print(f"  {region}: {len(lst)} cand, delta med={rds[len(rds)//2]}, "
              f"min={rds[0]}, max={rds[-1]}")

    # ---- near-miss metrics on smallest-delta candidates ----
    sel = sorted(rows, key=lambda r: r[1])[:metrics_top]
    results = []
    for n, d, omega, fac, region in sel:
        divs = proper_divisors(fac, n)
        wcount, run = near_miss(n, d, divs)
        results.append((run, wcount, n, d, omega, region))
    results.sort()
    out_md = os.path.join(HERE, "MINING-report.md")
    with open(out_md, "w") as g:
        g.write("# Near-miss mining report — Erdos #470 candidate substrate\n\n")
        g.write(f"Candidates analyzed: {len(rows)} (deduped). Near-miss metrics on the "
                f"{len(sel)} smallest-delta candidates.\n\n")
        g.write("## Closest-to-weird (smallest run-length = barely semiperfect)\n\n")
        g.write("| run | window_count | n | delta | omega | region |\n|---|---|---|---|---|---|\n")
        for run, wcount, n, d, omega, region in results[:40]:
            g.write(f"| {run} | {wcount} | {n} | {d} | {omega} | {region} |\n")
        g.write("\n## Delta distribution\n\n")
        g.write(f"min={ds[0]} p25={pct(.25)} median={pct(.5)} p75={pct(.75)} "
                f"p99={pct(.99)} max={ds[-1]}\n")
    print(f"wrote {out_md}")
    print("\ntop-10 closest-to-weird (run, window, n, delta, omega, region):")
    for r in results[:10]:
        print("  ", r)


if __name__ == "__main__":
    main()
