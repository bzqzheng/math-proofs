#!/bin/bash
# vdW production hunts — idle-core seed filler (niced below flagship jobs).
# Targets: n=171 (r=5) and n=226 (r=6) — one past the published records — and
# n=3704 (r=2,k=7, the W(2,7) marquee). Multi-color params: MAKEMODE=0 TABU=0;
# 2-color params: MAKEMODE=1 TABU=10 (the measured parameter map, see README).
# Each seed is an independent ticket; vdwls self-verifies by full rescan before
# printing FOUND, and any coloring is re-verified by vdw.py check_coloring.
set -u
cd "$(dirname "$0")"
mkdir -p logs colorings
run_seed() {
  local r=$1 k=$2 n=$3 seed=$4 mm=$5 tb=$6
  nice -n 10 env SEED=$seed NOISE=0 MAKEMODE=$mm TABU=$tb MAX_TRIES=1000000 \
    MAX_STEPS=20000000 QUIET=1 \
    ./vdwls $r $k $n "colorings/vdw_r${k}_c${r}_n${n}_s${seed}.col" \
    > "logs/hunt_r${k}_c${r}_n${n}_s${seed}.log" 2>&1
  echo "done r=$r k=$k n=$n seed=$seed: $(tail -1 "logs/hunt_r${k}_c${r}_n${n}_s${seed}.log")"
}
export -f run_seed
xargs -P 6 -n 6 bash -c 'run_seed "$@"' _ <<'JOBS'
5 3 171 1 0 0
5 3 171 2 0 0
6 3 226 1 0 0
6 3 226 2 0 0
2 7 3704 1 1 10
2 7 3704 2 1 10
JOBS
echo HUNTS-DONE
