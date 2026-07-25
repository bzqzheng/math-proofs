#!/bin/bash
# Sequential P3 sub-sub-shard runner for the odd-weird sweep.
# Usage: ./run_p3_fleet.sh <P2> <budget-seconds-per-shard> <p3> [<p3>...]
# Each sub-shard: SPF=3, forced second prime P2, forced third prime P3,
# MIN_DEPTH=6 (Liddy–Riedl prune). Completeness of the P3 union over the
# viable set was validated at 1e9 (tested counts match full P2 exactly).
set -u
cd "$(dirname "$0")"
P2=$1; BUDGET=$2; shift 2
for q in "$@"; do
  log="logs/odd_prod_1e24_spf3_p2_${P2}_p3_${q}.log"
  echo "[fleet] P2=$P2 P3=$q start $(date)"
  N_CAP=1e24 DELTA_MAX=1e7 TIME_BUDGET=$BUDGET MIN_DEPTH=6 SPF=3 P2=$P2 P3=$q \
    ./search_odd_weird > "$log" 2>&1
  echo "[fleet] P2=$P2 P3=$q done $(date): $(tail -1 "$log")"
done
echo "[fleet] P2=$P2 queue complete"
