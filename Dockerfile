# syntax = docker/dockerfile:1.0-experimental

FROM python:3.8 AS build-dependencies

WORKDIR /app

COPY bootstrap.sh tasks.py poetry.lock pyproject.toml ./
RUN ./bootstrap.sh --build-system-only

RUN inv setup.production

FROM python:3.8-slim-buster

ARG APP_VENV=/app/.venv
ARG APP_SITE_PACKAGES=${APP_VENV}/lib/python3.8/site-packages/

RUN apt-get update && apt-get install -y --no-install-recommends 'git=1:2.20.1-2+deb10u3' && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy dependencies
# We commit after these steps to cache setup and dependencies copy
COPY --from=build-dependencies ${APP_VENV} ${APP_VENV}
WORKDIR /app

COPY src/ ./src/

ENV PYTHONPATH=/app/src:${APP_SITE_PACKAGES} PATH=${PATH}:${APP_VENV}/bin

ENTRYPOINT [ "python", "/app/src/action.py" ]
