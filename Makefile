PYTHON ?= python3

.PHONY: check
check:
	@set -eu; \
	out=$$(mktemp -d "$${TMPDIR:-/tmp}/yeet-check.XXXXXX"); \
	$(PYTHON) verify_package.py; \
	$(PYTHON) evidence/historical/verify.py --output "$$out/historical"; \
	$(PYTHON) evidence/risky-receipts/verify.py --output "$$out/risky-receipts"; \
	$(PYTHON) evidence/current/verify.py --output "$$out/current"; \
	$(PYTHON) evidence/edge-model/verify.py --output "$$out/edge-model"; \
	$(PYTHON) evidence/public-search/verify_public_image.py; \
	for part in historical risky-receipts current edge-model; do \
	  for generated in "$$out/$$part/"*; do \
	    cmp "$$generated" "evidence/$$part/$${generated##*/}"; \
	  done; \
	done; \
	printf '\nPASS: all calculations reproduce the stored results byte for byte.\n'; \
	printf 'Generated results: %s\n' "$$out"
