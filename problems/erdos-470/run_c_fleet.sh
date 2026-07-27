#!/bin/bash
# Split an (SPF=3, P2, P3, EXPA, EXPB) subtree by the exponent c of P3 (EXPC partition).
# Usage: ./run_c_fleet.sh <P2> <P3> <EXPA> <EXPB> <budget-seconds-per-shard> <c> [<c>...]
set -u
cd "$(dirname "$0")"
P2=$1; P3=$2; EXPA=$3; EXPB=$4; BUDGET=$5; shift 5
for c in "$@"; do
  log="logs/odd_prod_1e24_spf3_p2_${P2}_p3_${P3}_expa_${EXPA}_expb_${EXPB}_expc_${c}.log"
  echo "[c-fleet] P2=$P2 P3=$P3 a=$EXPA b=$EXPB c=$c start $(date)"
  N_CAP=1e24 DELTA_MAX=1e7 TIME_BUDGET=$BUDGET MIN_DEPTH=6 SPF=3 P2=$P2 P3=$P3 \
    EXPA=$EXPA EXPB=$EXPB EXPC=$c ./search_odd_weird > "$log" 2>&1
  echo "[c-fleet] P2=$P2 P3=$P3 a=$EXPA b=$EXPB c=$c done $(date): $(tail -1 "$log")"
done
echo "[c-fleet] P2=$P2 P3=$P3 a=$EXPA b=$EXPB queue complete"
