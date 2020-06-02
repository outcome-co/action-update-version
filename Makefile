
ifneq "$(or $(GITHUB_ACTIONS), $(CI))" ""
$(info Running in CI mode)
INSIDE_CI=1
else
NOT_INSIDE_CI=1
endif

# VARIABLES

APP_NAME = $(shell docker run --rm -v $$(pwd):/work/ outcomeco/action-read-toml:latest --path /work/pyproject.toml --key tool.poetry.name)
APP_VERSION = $(shell docker run --rm -v $$(pwd):/work/ outcomeco/action-read-toml:latest --path /work/pyproject.toml --key tool.poetry.version) 

DOCKER_NAMESPACE = $(shell docker run --rm -v $$(pwd):/work/ outcomeco/action-read-toml:latest --path /work/pyproject.toml --key tool.docker.namespace)
DOCKER_REGISTRY= $(DOCKER_NAMESPACE)/$(APP_NAME)

ifndef BUILD_SYSTEM_REQUIREMENTS
# If the BUILD_SYSTEM_REQUIREMENTS variable is not defined, fetch it using the docker
BUILD_SYSTEM_REQUIREMENTS = $(shell docker run --rm -v $$(pwd):/work/ outcomeco/action-read-toml:latest --path /work/pyproject.toml --key build-system.requires)
endif

# DOCKER

.PHONY: docker-build docker-clean docker-publish docker-info

docker-build: ## Build the docker image
	docker build --build-arg BUILD_SYSTEM_REQUIREMENTS="$(BUILD_SYSTEM_REQUIREMENTS)" -t $(DOCKER_REGISTRY):$(APP_VERSION) .
	docker tag $(DOCKER_REGISTRY):$(APP_VERSION) $(DOCKER_REGISTRY):latest

docker-clean: ## Delete the docker image
	docker image rm $(DOCKER_REGISTRY)

docker-publish: docker-build ## Build and publish the docker image
	docker push $(DOCKER_REGISTRY):$(APP_VERSION)
	docker push $(DOCKER_REGISTRY):latest

# We use $(info) instead of @echo to avoid passing the variables to the shell
# as they can contain special chars like '>' that redirect the output
# We need the trailing comment else make complains that there's 'nothing to do'
# in the target
docker-info: ## Print useful info on the docker image
	$(info ::set-output name=docker_registry::$(DOCKER_REGISTRY))
	$(info ::set-output name=docker_tag::$(APP_VERSION))
	$(info ::set-output name=docker_build_args::$(BUILD_SYSTEM_REQUIREMENTS))
	@#

# SETUP

.PHONY: install-build-system ci-setup dev-setup production-setup lint test

install-build-system: ## Install poetry
	# We pass the variable through echo/xargs to avoid whitespacing issues 
	echo "$(BUILD_SYSTEM_REQUIREMENTS)" | xargs pip install

ci-setup: install-build-system ## Install the dependencies for CI environments
	poetry install --no-interaction --no-ansi

dev-setup: install-build-system ## Install the dependencies for dev environments
	./pre-commit.sh
	poetry install

production-setup: install-build-system ## Install the dependencies for production environments
	poetry config virtualenvs.create false
	poetry install --no-dev --no-interaction --no-ansi

# CI WORKFLOW

.PHONY: lint lint-isort lint-black lint-flake

lint: clean lint-isort lint-black lint-flake ## Run all linters

ifdef INSIDE_CI
# Inside the CI process, we want to run isort with the --diff flag and black with
# the --check flag to not change the files but fail if changes should be made
lint-isort: ## Run isort
	poetry run isort -rc . --check-only

lint-black: ## Run black
	poetry run black --check .
endif

ifdef NOT_INSIDE_CI
# Outside of the CI process, run isort and black normally
lint-isort:
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

# HELP

.PHONY: help
.DEFAULT_GOAL := help

# This target reads the Makefile and extracts all the targets that have a comment
# to display a help message
help: ## Display this help message
	@echo $(MAKEFILE_LIST) | tr ' ' '\n' | sort | uniq | xargs grep -h -E '^[a-zA-Z_-]+:.*?## .*$$' | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
