#!/bin/bash
# Split an (SPF=3, P2, P3) subtree by the exponent a of 3 (EXPA partition).
# Usage: ./run_a_fleet.sh <P2> <P3> <budget-seconds-per-shard> <a> [<a>...]
set -u
cd "$(dirname "$0")"
P2=$1; P3=$2; BUDGET=$3; shift 3
for a in "$@"; do
  log="logs/odd_prod_1e24_spf3_p2_${P2}_p3_${P3}_expa_${a}.log"
  echo "[a-fleet] P2=$P2 P3=$P3 a=$a start $(date)"
  N_CAP=1e24 DELTA_MAX=1e7 TIME_BUDGET=$BUDGET MIN_DEPTH=6 SPF=3 P2=$P2 P3=$P3 EXPA=$a \
    ./search_odd_weird > "$log" 2>&1
  echo "[a-fleet] P2=$P2 P3=$P3 a=$a done $(date): $(tail -1 "$log")"
done
echo "[a-fleet] P2=$P2 P3=$P3 queue complete"
