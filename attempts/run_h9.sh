#!/bin/bash
cd "$(dirname "$0")"; mkdir -p h9
run_h() { pfx="$1"; tag=$(echo "$pfx" | tr ',' '_'); [ -f "h9/$tag.h" ] && return
  HMODE=1 ./ppn "$K" "$pfx" "" 2>/dev/null | grep HEURISTIC | awk '{print $4}' > "h9/$tag.h"; }
export -f run_h; export K
grep -v '^$' "$LIST" | xargs -P "${NP:-3}" -I{} bash -c 'run_h "$@"' _ {}
echo DONE_H
