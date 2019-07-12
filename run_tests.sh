#!/usr/bin/env bash

set -e
exec_dir=`pwd`

if [ "$1" = "--init" ]; then
    python3 -m pip install --user -r requirements.txt
elif [ "$1" = "--selenium-server" ]; then
    if [ $(ps -ef | grep -v grep | grep selenium-server | wc -l) -ne 0 ]; then
        for pid in $(pidof selenium-server)
        do
            kill $pid
        done
        sleep 2
    fi
    sh resources/web_drivers/selenium_server/start_selenium_server.sh $exec_dir
else
    python3 -m run_robot $*
fi
# python3 -m run_robot --argumentfile runners/Demo/Internal_Chrome.txt
