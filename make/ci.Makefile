ifndef MK_CI
MK_CI=1


ifneq "$(or $(GITHUB_ACTIONS), $(CI))" ""
$(info Running in CI mode)
INSIDE_CI=1
else
NOT_INSIDE_CI=1
endif

# CI WORKFLOW

.PHONY: lint lint-isort lint-black lint-flake

lint: lint-isort lint-black lint-flake ## Run all linters

ifdef INSIDE_CI
# Inside the CI process, we want to run isort with the --diff flag and black with
# the --check flag to not change the files but fail if changes should be made
lint-isort: clean ## Run isort
	poetry run isort -rc . --check-only

lint-black: ## Run black
	poetry run black --check .
endif

ifdef NOT_INSIDE_CI
# Outside of the CI process, run isort and black normally
lint-isort: clean
	poetry run isort -rc .

lint-black:
	poetry run black .
endif

lint-flake: ## Run flake8
	poetry run flake8 .

.PHONY: test

test: ## Run tests
	poetry run coverage run -m pytest
	poetry run coverage report -m

# CLEANING

.PHONY: clean clean-python clean-coverage

clean: clean-python clean-coverage ## Remove generated data

clean-python: ## Remove python artifacts
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete

clean-coverage: ## Remove coverage reports
	rm -rf coverage

endif
