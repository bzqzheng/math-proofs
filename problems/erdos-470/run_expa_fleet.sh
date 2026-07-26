#!/bin/bash
# EXPA sub-shard runner: SPF=3 P2=5 P3=7 monster subtree, split by fixing the
# exponent a of 3 (union over a=1..amax = full monster, disjoint partition).
# Usage: ./run_expa_fleet.sh <budget-seconds-per-shard> <a> [<a>...]
set -u
cd "$(dirname "$0")"
BUDGET=$1; shift
for a in "$@"; do
  log="logs/odd_prod_1e24_spf3_p2_5_p3_7_expa_${a}.log"
  echo "[expa] a=$a start $(date)"
  N_CAP=1e24 DELTA_MAX=1e7 TIME_BUDGET=$BUDGET MIN_DEPTH=6 SPF=3 P2=5 P3=7 EXPA=$a \
    ./search_odd_weird > "$log" 2>&1
  echo "[expa] a=$a done $(date): $(tail -1 "$log")"
done
echo "[expa] queue complete"
