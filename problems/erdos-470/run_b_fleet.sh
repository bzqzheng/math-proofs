#!/bin/bash
# Split an (SPF=3, P2, P3, EXPA) subtree by the exponent b of P2 (EXPB partition).
# Usage: ./run_b_fleet.sh <P2> <P3> <EXPA> <budget-seconds-per-shard> <b> [<b>...]
set -u
cd "$(dirname "$0")"
P2=$1; P3=$2; EXPA=$3; BUDGET=$4; shift 4
for b in "$@"; do
  log="logs/odd_prod_1e24_spf3_p2_${P2}_p3_${P3}_expa_${EXPA}_expb_${b}.log"
  echo "[b-fleet] P2=$P2 P3=$P3 a=$EXPA b=$b start $(date)"
  N_CAP=1e24 DELTA_MAX=1e7 TIME_BUDGET=$BUDGET MIN_DEPTH=6 SPF=3 P2=$P2 P3=$P3 EXPA=$EXPA EXPB=$b \
    ./search_odd_weird > "$log" 2>&1
  echo "[b-fleet] P2=$P2 P3=$P3 a=$EXPA b=$b done $(date): $(tail -1 "$log")"
done
echo "[b-fleet] P2=$P2 P3=$P3 a=$EXPA queue complete"
