ifndef MK_VARS_PY
MK_VARS_PY=1

APP_NAME = $(shell $(READ_PYPROJECT_KEY) tool.poetry.name)
APP_VERSION = $(shell $(READ_PYPROJECT_KEY) tool.poetry.version)

endif
