ifndef MK_ENV
MK_ENV=1

# Try to load a local .env file, the '-' silences the error if the file doesn't exist
-include .env
# Try to load build secrets if we're in a Docker
-include /run/secrets/build-secrets

include make/env*.Makefile

SHELL = /bin/bash
SHELL_DEBUG ?= 1

# Determine whether we're in a CI environment such as Github Actions
# Github Actions defines a GITHUB_ACTIONS=true variable
#
# Generic tools can set CI=true 
ifneq "$(or $(GITHUB_ACTIONS), $(CI), $(PRE_COMMIT))" ""
$(info Running in CI mode)
NOT_INSIDE_CI=0
INSIDE_CI=1
SHELL_DEBUG=1
else
NOT_INSIDE_CI=1
INSIDE_CI=0
endif

ifeq ($(SHELL_DEBUG),1)
SHELL = /bin/bash -x
endif

# Are we in a git repo?
IN_GIT = $(shell ((test -d .git && echo "1") || echo "0") 2> /dev/null)

ifeq ($(IN_GIT),1)
GIT_BRANCH := $(shell git rev-parse --abbrev-ref HEAD)
GIT_BRANCH_NORMAL = $(shell echo $(GIT_BRANCH) | tr '[_/]' '-')

# The master branch can be called HEAD when checked out in a detached state
ifeq ($(GIT_BRANCH),master)
IN_GIT_MAIN=1
else ifeq ($(GIT_BRANCH),HEAD)
IN_GIT_MAIN=1
else
IN_GIT_MAIN=0
endif

else
IN_GIT_MAIN=0
endif

COMMIT_SHA1 = $(shell git rev-parse --short=8 HEAD)
PLATFORM = $(shell echo $$(uname -s) | tr '[:upper:]' '[:lower:]')

empty :=
space := $(empty) $(empty)

# The goal of generate_gcp_credentials is to make sure we have a GOOGLE_APPLICATION_CREDENTIALS defined
# pointing to an existing file containing GCP credentials
ifndef GOOGLE_APPLICATION_CREDENTIALS 
# If GOOGLE_APPLICATION_CREDENTIALS is not defined we cannot authenticate to GCR
generate-gcp-credentials: 
	$(error You need to define a GOOGLE_APPLICATION_CREDENTIALS environment variable)
else
ifeq (,$(wildcard ${GOOGLE_APPLICATION_CREDENTIALS}))
# If GOOGLE_APPLICATION_CREDENTIALS doesn't point to an existing file, we need to generate it from the encoded credentials
# This is used during CI, since an encoded version of the credentials key file is passed as a secret to the Github environment
ifndef GOOGLE_APPLICATION_CREDENTIALS_ENCODED
# If GOOGLE_APPLICATION_CREDENTIALS_ENCODED is not defined, we cannot generate credentials file
generate-gcp-credentials:
	$(error You need to define a GOOGLE_APPLICATION_CREDENTIALS_ENCODED environment variable to generate your GCP credentials)
else
# We generate credentials file
generate-gcp-credentials:
	@mkdir -p $$(dirname ${GOOGLE_APPLICATION_CREDENTIALS}) && echo ${GOOGLE_APPLICATION_CREDENTIALS_ENCODED} | base64 -d > ${GOOGLE_APPLICATION_CREDENTIALS}
endif
else
# If GOOGLE_APPLICATION_CREDENTIALS points to an existing file, everything is set, nothing needs to be done
generate-gcp-credentials:
	@#noop
endif
endif


ifndef GITHUB_REF
current-git-tag:
	$(error GITHUB_REF needs to be defined to output the current tag)
else
# As releases are only triggered by push on tags beginning with 'v*', GITHUB_REF will be the version tag in the format `refs/tags/v1.2.3`.
# The syntax `#refs/tags/` is a paramater expansion that will expand `refs/tags/v1.2.3` to `v1.2.3`.
# For more see https://www.gnu.org/software/bash/manual/html_node/Shell-Parameter-Expansion.html
current-git-tag:
	@echo ::set-output name=tag::$${GITHUB_REF#refs/tags/}
endif


-include make/vars*.Makefile

endif
