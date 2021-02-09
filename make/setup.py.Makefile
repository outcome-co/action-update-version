ifndef MK_SETUP_PY
MK_SETUP_PY=1

ifeq ($(PLATFORM),darwin)
# For local usage on OSX
POETRY_ENV += LDFLAGS="-L$$(brew --prefix openssl)/lib"
endif

.PHONY: install-build-system production-setup dev-setup ci-setup cache-friendly-pyproject e2e-setup

install-build-system: ## Install poetry
	# We pass the variable through echo/xargs to avoid whitespacing issues
	$(READ_PYPROJECT_KEY) build-system.requires | xargs pip install

production-setup: install-build-system ## Install the dependencies for production environments
	poetry config virtualenvs.in-project true
	@${POETRY_ENV} poetry install --no-interaction --no-ansi --no-dev

e2e-setup: install-build-system ## Install the dependencies for e2e environments
	poetry config virtualenvs.in-project true
	@${POETRY_ENV} poetry install --no-interaction --no-ansi

ci-setup: install-build-system ## Install the dependencies for CI environments
	@${POETRY_ENV} poetry install --no-interaction --no-ansi

dev-setup: install-build-system ## Install the dependencies for dev environments
	@${POETRY_ENV} poetry install
	./pre-commit.sh

cache-friendly-pyproject:
	sed -e 's/^version[[:space:]]*=.*$$/version = "0.0.1-cache-friendly"/g' pyproject.toml > pyproject.cachefriendly.toml
	mv pyproject.cachefriendly.toml pyproject.toml

endif
