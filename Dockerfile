FROM python:3.8 AS build-env

ARG BUILD_SYSTEM_REQUIREMENTS

WORKDIR /build

COPY Makefile poetry.lock pyproject.toml /build/

# We need the Makefiles on this path so we can still "include make/*.Makefile"
COPY make/ /build/make/

# Provide the BUILD_SYSTEM_ARGUMENTS to the Makefile
RUN BUILD_SYSTEM_REQUIREMENTS=${BUILD_SYSTEM_REQUIREMENTS} make install-build-system
RUN poetry export -f requirements.txt -o requirements.txt --without-hashes 

FROM python:3.8-slim-buster

RUN apt-get update && apt-get install -y --no-install-recommends git  

WORKDIR /app

COPY --from=build-env /build/requirements.txt /app/
COPY ./bin /app/bin

RUN pip install --no-cache -r requirements.txt

ENTRYPOINT [ "/app/bin/entrypoint.sh" ]
