ifndef MK_SETUP
MK_SETUP=1


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

endif