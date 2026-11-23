.PHONY: help test compare test-cpu test-cache test-integration harvard shared report synth demo
PYTHON ?= python3
PROG ?= prog1
help:
	@echo 'make test              Run CPU, cache and integrated verification'
	@echo 'make compare           Run original Harvard/shared cycle comparison'
	@echo 'make test-cache        Run cache unit tests and trace benchmarks'
	@echo 'make test-integration  Run 36 cached-CPU configurations'
	@echo 'make harvard PROG=prog1 / make shared PROG=prog1'
	@echo 'make report            Generate final PDF, charts and Markdown results'
	@echo 'make synth             Run Yosys structural synthesis (requires yosys)'
test:
	$(PYTHON) scripts/verify.py all
compare test-cpu:
	$(PYTHON) scripts/verify.py cpu
test-cache:
	$(PYTHON) scripts/verify.py cache
test-integration:
	$(PYTHON) scripts/verify.py integration
harvard:
	$(PYTHON) scripts/verify.py cpu --architecture harvard --program $(PROG)
shared:
	$(PYTHON) scripts/verify.py cpu --architecture shared --program $(PROG)
report:
	$(PYTHON) scripts/report.py
synth:
	$(PYTHON) scripts/synth.py
demo:
	$(PYTHON) scripts/demo.py
