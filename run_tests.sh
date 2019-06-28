#!/usr/bin/env bash

set -e

if [ "$1" = "--init" ]; then
    python3 -m pip install --user -r requirements.txt
else
    python3 -m run_robot $*
fi
# python3 -m run_robot --argumentfile runners/Demo/Internal_Chrome.txt
