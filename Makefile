SHELL := bash
.ONESHELL:


.PHONY: lint
lint:
	@echo "Running Ruff linter..."
	uv run --only-group lint ruff check --fix


.PHONY: format
format:
	@echo "Running Ruff formatter..."
	uv run --only-group lint ruff format


.PHONY: audit
audit:
	@echo "Running dependency audit..."
	uv run --only-group audit pip-audit


.PHONY: test
test:
	@echo "Running UV sync..."
	uv sync --group test
	@echo "Running Unit Tests..."
	uv run --only-group test pytest -v --disable-warnings tests/

.PHONY: test-coverage
test-coverage:
	@echo "Running UV sync..."
	uv sync --group test
	@echo "Running Unit Tests with coverage..."
	uv run --only-group test pytest -v --disable-warnings --cov=sds_common --cov-report=term-missing --cov-report=html:htmlcov tests/

.PHONY: test-parallel
test-parallel:
	@echo "Running Unit Tests in parallel..."
	uv sync --group test
	uv run --only-group test pytest -n auto -v --disable-warnings tests/


.PHONY: bump
bump:
	@echo "🔼 Bumping project version..."
	uv run --only-group version-check python .github/scripts/bump_version.py
	@echo "🔄 Generating new lock file..."
	uv lock

.PHONY: install
install: ## Install dependencies
	uv sync


.PHONY: build-dist
build-dist: install ## Build tar and wheel
	uv build

.PHONY: publish-dist
publish-dist: build-dist ## Publish to artifact registry (must be logged into gcloud)
	uv run --only-group publish twine upload \
		--repository-url https://europe-west2-python.pkg.dev/ons-sds-ci/sds-python-packages \
		--verbose dist/sds_common-*
