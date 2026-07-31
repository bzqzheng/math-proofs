#!/bin/bash
# Grimm #375 production run to 1e12, sharded x8 by N_START (stitch-exactness
# gate-verified: shards re-verify the boundary block exactly once).
# Total measured cost ~9 core-hours -> ~70-90 min wall at 8 shards on M4 Max.
set -u
cd "$(dirname "$0")"
mkdir -p logs
run_shard() {
  local lo=$1 hi=$2 tag=$3
  N_START=$lo N_MAX=$hi PROGRESS=2e10 ./grimm > "logs/grimm_1e12_$tag.log" 2>&1
  echo "shard $tag done: $(grep -c 'CANDIDATE' logs/grimm_1e12_$tag.log || true) counterexample candidates"
}
export -f run_shard
xargs -P 8 -n 3 bash -c 'run_shard "$@"' _ <<'SHARDS'
2 125000000000 s1
125000000000 250000000000 s2
250000000000 375000000000 s3
375000000000 500000000000 s4
500000000000 625000000000 s5
625000000000 750000000000 s6
750000000000 875000000000 s7
875000000000 1000000000000 s8
SHARDS
echo GRIMM-1E12-ALL-DONE
