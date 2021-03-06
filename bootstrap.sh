#! /bin/bash

set -e


usage() {
    echo "Usage: ./bootstrap [--build-system-only]"
    exit 1
}

if [ $# -ne 0 ]; then
    if [ $# -ne 1 ] || [ "$1" != '--build-system-only' ]; then
        usage
    fi

build_system_only=1
else
build_system_only=0
fi


# Install dependencies
pip install --upgrade "outcome-devkit>=7.2.0b2"

if [ $build_system_only -eq 1 ]; then
PYTHONPATH=src inv setup.build-system
else
PYTHONPATH=src inv setup.auto
fi
