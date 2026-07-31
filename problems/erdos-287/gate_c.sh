#!/bin/bash
# Gate for the C MITM port (mirrors `python mitm_287.py gate`):
#   (a) known-positive:  GAP=3 k=3 must yield a verified (2,3,6)
#   (b) known-negative:  GAP=2 k<=21 must yield zero verified solutions
#   (c) equivalence:     k=22..40 — C vs Python identical first_half,
#                        second_half, and hits == C verified
set -euo pipefail
cd "$(dirname "$0")"
PY=../../.venv/bin/python

clang -O3 -o mitm_287 mitm_287.c -lm
echo "build OK"

echo "--- Python-side gate (spec engine) ---"
$PY mitm_287.py gate

echo "--- C gate (a): GAP=3 k=3 -> (2,3,6) through full pipeline ---"
GAP=3 ./mitm_287 3 3
$PY verify_hits.py 3 hits_287_k3_gap3.txt --gap 3 --expect 2,3,6
echo "gate (a) OK"

echo "--- C gate (b): GAP=2 k<=21 zero verified solutions ---"
for k in $(seq 2 21); do GAP=2 ./mitm_287 "$k" "$k"; done
for k in $(seq 2 21); do $PY verify_hits.py "$k" "hits_287_k${k}_gap2.txt" --expect-none; done
echo "gate (b) OK"

echo "--- gate (c): equivalence k=22..40 (Python --exhaustive vs C) ---"
$PY mitm_287.py --exhaustive 22 40 | tee gate_py_22_40.log
GAP=2 ./mitm_287 22 40 | tee gate_c_22_40.log
: > gate_verify_22_40.log
for k in $(seq 22 40); do
  $PY verify_hits.py "$k" "hits_287_k${k}_gap2.txt" | tee -a gate_verify_22_40.log
done
$PY compare_gate.py gate_py_22_40.log gate_c_22_40.log gate_verify_22_40.log
echo "ALL GATES PASSED"
