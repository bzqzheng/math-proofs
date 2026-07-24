#!/bin/bash
# Shard launcher for the C odd-weird engine (./search_odd_weird).
# Design: every odd n has a unique smallest prime factor (SPF), so sharding
# by SPF partitions the search space disjointly and completely.
# Usage: ./run_production.sh <shard>   where shard = A | B | C
#   A: SPF = 3           (dominant shard — most of the tree)
#   B: SPF = 5 or 7
#   C: SPF = 11, 13, ... (all remaining viable first primes)
# Env passthrough: N_CAP (default 1e24), DELTA_MAX (default 1e7),
# TIME_BUDGET (default 14400 = 4h).
# Requires the C binary to accept SPF (start-prime) env var; if it doesn't,
# patch dfs() entry per README.md before running.

set -u
cd "$(dirname "$0")"
BIN=./search_odd_weird
N_CAP=${N_CAP:-1e24}
DELTA_MAX=${DELTA_MAX:-1e7}
TIME_BUDGET=${TIME_BUDGET:-14400}
SHARD=${1:?usage: run_production.sh A|B|C}

run_spf() {
  local p=$1
  echo "[shard $SHARD] starting SPF=$p at $(date)" 
  N_CAP=$N_CAP DELTA_MAX=$DELTA_MAX TIME_BUDGET=$TIME_BUDGET SPF=$p \
    $BIN > "odd_prod_${N_CAP}_spf${p}.log" 2>&1
  echo "[shard $SHARD] finished SPF=$p at $(date)"
}

case $SHARD in
  A) run_spf 3 ;;
  B) run_spf 5; run_spf 7 ;;
  C) for p in 11 13 17 19 23 29 31 37 41 43 47 53; do run_spf $p; done ;;
  *) echo "unknown shard $SHARD" >&2; exit 1 ;;
esac
echo "[shard $SHARD] all done"
