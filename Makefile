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
	uv publish --index api_signature_tester --username __token__ --password $TEST_PYPI_API_TOKEN
