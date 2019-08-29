#!/usr/bin/env bash

set -e

selenium_server_starter_dir=resources/web_drivers/selenium_server

if [ "$1" = "--init" ]; then
    python3 -m pip install --user -r requirements.txt
elif [ "$1" = "--sss" ]; then
    bash $selenium_server_starter_dir/selenium_server.sh -t
    bash $selenium_server_starter_dir/selenium_server.sh -s
elif [ "$1" = "--tss" ]; then
    bash $selenium_server_starter_dir/selenium_server.sh -t
elif [ "$1" = "--testdoc" ]; then
    shift
    python3 -m robot.testdoc $*
else
    python3 -m run_robot $*
fi
# python3 -m run_robot --argumentfile runners/Demo/Internal_Chrome.txt
