#!/bin/bash
# Resume of run_mining.sh after the M1 Pro -> M4 Max migration: the 12 regions
# whose logs were never produced, plus a fresh full-budget whale (5_7_1_1_1 was
# truncated at 3075/3600 s when the old fleet was stopped). The 12 completed
# 900 s logs from the old machine are valid (candidate arrival is front-loaded)
# and are NOT re-run. Whale first so xargs schedules it on slot 1.
set -u
cd "$(dirname "$0")"
mkdir -p mining
run_one() {
  local p2=$1 p3=$2 a=$3 b=$4 c=$5 budget=$6
  N_CAP=1e24 DELTA_MAX=1e7 MIN_DEPTH=6 SPF=3 P2=$p2 P3=$p3 EXPA=$a EXPB=$b EXPC=$c \
    TIME_BUDGET=$budget DUMP=1 ./search_odd_weird > "mining/${p2}_${p3}_${a}_${b}_${c}.log" 2>&1
  echo "region $p2,$p3,$a,$b,$c: $(grep -c '^CAND' mining/${p2}_${p3}_${a}_${b}_${c}.log) candidates"
}
export -f run_one
xargs -P 8 -n 6 bash -c 'run_one "$@"' _ <<'REGIONS'
5 7 1 1 1 3600
5 13 1 4 1 900
5 11 1 1 1 900
5 11 6 1 1 900
5 11 4 1 1 900
5 11 3 1 1 900
5 13 2 2 1 900
5 7 1 3 1 900
5 13 3 3 1 900
5 7 1 1 3 900
5 7 1 3 2 900
5 13 5 1 1 900
5 13 1 1 1 900
REGIONS
echo MINING-REST-DONE
