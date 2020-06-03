ifndef MK_BUILD
MK_BUILD=1


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
	$(info ::set-output name=docker_build_args:: BUILD_SYSTEM_REQUIREMENTS=$(BUILD_SYSTEM_REQUIREMENTS))
	@#

endif
