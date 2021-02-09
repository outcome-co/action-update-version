# syntax = docker/dockerfile:1.0-experimental

FROM python:3.8 AS build-dependencies

ARG BUILD_SYSTEM_REQUIREMENTS

WORKDIR /app

COPY Makefile poetry.lock pyproject.toml ./
COPY make/ ./make/

# We remove version from pyproject, 
# that way if dependencies have not changed, docker won't rebuild previous steps
RUN make cache-friendly-pyproject
RUN make production-setup

FROM python:3.8-slim-buster

ARG APP_VENV=/app/.venv
ARG APP_SITE_PACKAGES=${APP_VENV}/lib/python3.8/site-packages/

RUN apt-get update && apt-get install -y --no-install-recommends git && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy dependencies
# We commit after these steps to cache setup and dependencies copy
COPY --from=build-dependencies ${APP_VENV} ${APP_VENV}
WORKDIR /app

COPY src/ ./src/

ENV PYTHONPATH=/app/src:${APP_SITE_PACKAGES} PATH=${PATH}:${APP_VENV}/bin

ENTRYPOINT [ "python", "/app/src/action.py" ]
