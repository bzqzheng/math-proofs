#!/bin/bash
# Near-miss mining: DUMP=1 candidate harvest over the 25 abundancy-frontier
# spine regions documented in RESULTS.md. Each region runs TIME_BUDGET seconds
# (candidate arrival is front-loaded: ~98% in the first ~72 s on the whale).
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
xargs -P 4 -n 6 bash -c 'run_one "$@"' _ <<'REGIONS'
5 7 1 1 1 3600
5 7 1 2 1 900
5 11 2 1 1 900
5 7 1 1 2 900
5 13 2 1 1 900
5 7 2 1 1 900
5 13 2 1 2 900
5 11 2 3 1 900
5 13 3 1 1 900
5 11 1 3 1 900
5 11 1 2 1 900
5 13 4 2 1 900
5 11 5 1 1 900
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
echo MINING-ALL-DONE
