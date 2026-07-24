#!/bin/bash
# Sharded exhaustive k=9 run. Each depth-5 prefix is an independent, resumable job.
cd "$(dirname "$0")"
mkdir -p k9
NPROC=${NPROC:-8}
run_one() {
  pfx="$1"; tag=$(echo "$pfx" | tr ',' '_')
  [ -f "k9/$tag.done" ] && return
  /usr/bin/time -p ./ppn 9 "$pfx" "k9/$tag.defer" > "k9/$tag.out" 2> "k9/$tag.time"
  mv "k9/$tag.out" "k9/$tag.done"
}
export -f run_one
grep -v '^$' k9_prefixes_even.txt | xargs -P "$NPROC" -I{} bash -c 'run_one "$@"' _ {}
echo "ALL SHARDS DONE"
