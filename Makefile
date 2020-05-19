APP_NAME = $(shell docker run --rm -v $$(pwd):/work/ outcomeco/action-read-toml:latest --path /work/pyproject.toml --key tool.poetry.name)
APP_VERSION = $(shell docker run --rm -v $$(pwd):/work/ outcomeco/action-read-toml:latest --path /work/pyproject.toml --key tool.poetry.version) 

DOCKER_NAMESPACE = outcomeco
DOCKER_REGISTRY= $(DOCKER_NAMESPACE)/$(APP_NAME)

ifndef BUILD_SYSTEM_REQUIREMENTS
# If the BUILD_SYSTEM_REQUIREMENTS variable is not defined, fetch it using the docker
BUILD_SYSTEM_REQUIREMENTS = $(shell docker run --rm -v $$(pwd):/work/ outcomeco/action-read-toml:latest --path /work/pyproject.toml --key build-system.requires)
endif

.PHONY: docker-build docker-clean docker-publish docker-info

docker-build:
	docker build --build-arg BUILD_SYSTEM_REQUIREMENTS="$(BUILD_SYSTEM_REQUIREMENTS)" -t $(DOCKER_REGISTRY):$(APP_VERSION) .
	docker tag $(DOCKER_REGISTRY):$(APP_VERSION) $(DOCKER_REGISTRY):latest

docker-clean:
	docker image rm $(DOCKER_REGISTRY)

docker-publish: docker-build
	docker push $(DOCKER_REGISTRY):$(APP_VERSION)
	docker push $(DOCKER_REGISTRY):latest

docker-info:
	@echo ::set-output name=DOCKER_REGISTRY::$(DOCKER_REGISTRY)
	@echo ::set-output name=docker_tag::$(APP_VERSION)

.PHONY: install-build-system ci-setup dev-setup production-setup lint test

install-build-system:
	# We pass the variable through echo/xargs to avoid whitespacing issues 
	echo "$(BUILD_SYSTEM_REQUIREMENTS)" | xargs pip install

ci-setup: install-build-system
	poetry install --no-interaction --no-ansi

dev-setup: install-build-system
	./pre-commit.sh
	poetry install

production-setup: install-build-system
	poetry config virtualenvs.create false
	poetry install --no-dev --no-interaction --no-ansi

lint:
	# NOOP

test:
	# NOOP
