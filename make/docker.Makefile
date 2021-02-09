ifndef MK_DOCKER
MK_DOCKER=1

.PHONY: docker-build docker-push docker-gcr-login

DOCKERFILE ?= Dockerfile
DOCKER_BUILDKIT ?= 1

export DOCKER_BUILDKIT

ifeq ($(IN_GIT_MAIN),1)
DOCKER_TAG_VERSION = $(APP_VERSION)
else
DOCKER_TAG_VERSION = $(APP_VERSION)-$(GIT_BRANCH_NORMAL)
endif

DOCKER_IMAGE_NAME = $(DOCKER_REPOSITORY)/$(APP_NAME):$(DOCKER_TAG_VERSION)
DOCKER_IMAGE_NAME_WITH_REGISTRY = $(DOCKER_REGISTRY)/$(DOCKER_IMAGE_NAME)

DOCKER_BUILD_ARG_VARS += APP_VERSION=$(DOCKER_TAG_VERSION) APP_NAME=$(APP_NAME)

ifdef APP_ENV
DOCKER_BUILD_ARG_VARS += APP_ENV=$(APP_ENV)
endif

DOCKER_BUILD_ARGS += --build-arg $(subst $(space), --build-arg ,$(DOCKER_BUILD_ARG_VARS))

docker-build:  ## Build docker image
	docker build -t $(DOCKER_IMAGE_NAME_WITH_REGISTRY) -f $(DOCKERFILE) $(DOCKER_BUILD_ARGS) .

docker-push: docker-login ## Push the docker image to the registry
	docker push $(DOCKER_IMAGE_NAME_WITH_REGISTRY)

docker-login: ## Login to the public docker registry
	echo $(DOCKER_TOKEN) | docker login -u $(DOCKER_USERNAME) --password-stdin

endif
