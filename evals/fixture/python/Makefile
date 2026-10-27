.PHONY: verify

verify:
	ruff check .
	pyright
	PYTHONPATH=src lint-imports
	pytest -q
