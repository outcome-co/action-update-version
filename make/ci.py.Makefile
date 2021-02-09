ifndef MK_CI_PY
MK_CI_PY=1

# CI WORKFLOW

.PHONY: check check-types lint lint-flake lint-black lint-isort

check: check-types lint ## Run checks and linters

check-types: ## Run mypy
	# Disabled for now
	#poetry run mypy ./bin ./src

lint: clean lint-isort lint-black lint-flake ## Run all linters
	
lint-flake: ## Run flake linting
	poetry run flake8 ./src ./test
	(test -d bin && poetry run flake8 ./bin) || true
	(test -d typings && poetry run flake8 ./typings/**/*.pyi) || true

ifeq ($(INSIDE_CI),0)
# Not inside a CI process
lint-black: ## Run black
	poetry run black .

lint-isort: ## Run isort 
	poetry run isort -rc .
else
# Inside the CI process, we want to run black with the --check flag and isort 
# with the --diff flag to not change the files but fail if changes should be made
lint-black: 
	poetry run black --check .

lint-isort: 
	poetry run isort -rc . --check-only
endif

.PHONY: test test-unit test-integration coverage
TEST_TARGET ?= ./test

define run-pytest
	$(MAKE) clean-coverage
	poetry run coverage run --context=$(COVERAGE_CONTEXT) -m pytest -vvv --ff --maxfail=1 $(TEST_TARGET)
	$(MAKE) coverage
endef

# For all cases, we set the python path
coverage: export PYTHONPATH = src
ifeq ($(INSIDE_CI),0)
# Not inside a CI process
coverage: ## Create coverage reports
	# Run a first coverage, to the console but don't fail based on %
	poetry run coverage report -m --fail-under 0
	# Run a second coverage to output html, and fail according to %
	poetry run coverage html --show-contexts

else
coverage:
	@# Just run converage, and fail according to %
	poetry run coverage report -m
endif # closes ifeq ($(INSIDE_CI),0)

test: test-unit test-integration

# The types of tests to run are controlled by the APP_ENV variable
test-unit: export APP_ENV = test
test-unit: export COVERAGE_CONTEXT = unit-test
test-unit: export PYTHONPATH = src
test-unit: ## Run unit tests
	# Unit tests
	$(call run-pytest)

test-integration: export APP_ENV = integration
test-integration: export COVERAGE_CONTEXT = integration-test
test-integration: export PYTHONPATH = src
test-integration: ## Run integration tests 
	# Integration tests
	$(call run-pytest)


# CLEANING

.PHONY: clean clean-coverage clean-python

clean: clean-coverage clean-python ## Remove generated data

clean-python: ## Remove python artifacts
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
	rm -rf ".pytest_cache"

clean-coverage: ## Remove coverage reports
	# Cleaning coverage files
	rm -rf coverage

endif
