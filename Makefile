PY := .venv/bin/python

.PHONY: verify verify-jacobian verify-erdos-164 verify-unit-distance \
        scan-699 scan-458 scan-779 scan-287 new

## verify: run all independent re-verifications of external claims
verify: verify-jacobian verify-erdos-164 verify-unit-distance

verify-jacobian:
	$(PY) problems/jacobian-dim3/verify_jacobian_counterexample.py

verify-erdos-164:
	$(PY) problems/erdos-164/verify_primitive_set_conjecture.py

verify-unit-distance:
	$(PY) problems/unit-distance/verify_unit_distance_baseline.py

## scan-*: reproduce our own bounds (long-running; see logs/ for milestones)
scan-699:
	N_MAX=1e9 $(PY) problems/erdos-699/scan_699.py

verify-erdos-375:
	$(PY) problems/erdos-375/grimm_reference.py gate

scan-375:
	cd problems/erdos-375 && clang -O3 -o grimm grimm.c -lm && N_MAX=1e10 ./grimm

scan-458:
	$(PY) problems/erdos-458/scan_458_fast.py

scan-779:
	$(PY) problems/erdos-779/scan_fortunate.py

scan-287:
	$(PY) problems/erdos-287/scan_287_gaps.py

## new: scaffold a problem directory — usage: make new ID=erdos-XXX
new:
	@test -n "$(ID)" || (echo "usage: make new ID=<name>"; exit 1)
	@cp -r problems/TEMPLATE problems/$(ID)
	@echo "scaffolded problems/$(ID) — register it in problems/README.md"
