FROM python:3.8.3

ARG BUILD_SYSTEM_REQUIREMENTS

WORKDIR /app

COPY Makefile poetry.lock pyproject.toml /app/

# We need the Makefiles on this path so we can still "include make/*.Makefile"
COPY make make

# Provide the BUILD_SYSTEM_ARGUMENTS to the Makefile
RUN BUILD_SYSTEM_REQUIREMENTS=${BUILD_SYSTEM_REQUIREMENTS} make production-setup

COPY ./bin /app/bin

ENTRYPOINT [ "/app/bin/entrypoint.sh" ]
