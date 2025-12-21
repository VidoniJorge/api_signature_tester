install:
	@echo "Installing dependencies..."
	uv sync

run:
	@echo "Running the application..."
	python -m src.main

help:
	@echo "Makefile commands:"
	@echo "  install - Install project dependencies"
	@echo "  run     - Run the application"
	@echo "  help    - Show this help message"
	@echo "  publish - Publish the package to Test PyPI"

publish:
	@echo "Publishing the package..."
	@# Fail fast if the token is not set (use env export or pass on the make command line)
	@if [ -z "$(TEST_PYPI_API_TOKEN)" ]; then \
		echo "ERROR: TEST_PYPI_API_TOKEN is not set. Export it (export TEST_PYPI_API_TOKEN=...) or run:\\n  TEST_PYPI_API_TOKEN=... make publish"; \
		exit 1; \
	fi
	uv publish --index api_signature_tester --username __token__ --password $(TEST_PYPI_API_TOKEN)
