#!/usr/bin/env bash

set -e
exec_dir=`pwd`
selenium_server_starter_dir=resources/web_drivers/selenium_server

function terminate_service() {
    if [ $(ps -ef | grep -v grep | grep $1 | wc -l) -ne 0 ]; then
        for pid in $(ps -ef | grep -v grep | grep $1 | awk '{print $2}')
        do
            echo $pid
            kill $pid
        done
        sleep 2
    fi
}

if [ "$1" = "--init" ]; then
    python3 -m pip install --user -r requirements.txt
elif [ "$1" = "--sss" ]; then
    terminate_service selenium-server
    cd $selenium_server_starter_dir
    bash start_selenium_server.sh $exec_dir
    cd -
elif [ "$1" = "--tss" ]; then
    terminate_service selenium-server
else
    python3 -m run_robot $*
fi
# python3 -m run_robot --argumentfile runners/Demo/Internal_Chrome.txt
