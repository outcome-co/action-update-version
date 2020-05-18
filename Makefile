APP_NAME = action-update-version
APP_VERSION = $(shell cat VERSION)

DOCKER_NAMESPACE = outcomeco
DOCKER_REGISTRY= $(DOCKER_NAMESPACE)/$(APP_NAME)

.PHONY: docker-build docker-run docker-clean docker-publish docker-info

docker-build:
	docker build -t $(DOCKER_REGISTRY):$(APP_VERSION) .
	docker tag $(DOCKER_REGISTRY):$(APP_VERSION) $(DOCKER_REGISTRY):latest

docker-clean:
	docker image rm $(DOCKER_REGISTRY)

docker-publish: docker-build
	docker push $(DOCKER_REGISTRY):$(APP_VERSION)
	docker push $(DOCKER_REGISTRY):latest

docker-info:
	@echo ::set-output name=DOCKER_REGISTRY::$(DOCKER_REGISTRY)
	@echo ::set-output name=docker_tag::$(APP_VERSION)

.PHONY: dev-setup lint test

dev-setup:
	# NOOP

lint:
	# NOOP

test:
	# NOOP
