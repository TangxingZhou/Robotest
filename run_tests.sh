#!/usr/bin/env bash

set -e

workspace=$(cd `dirname $0`; pwd)
PYTHONPATH=$workspace
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
    OLD_IFS="$IFS"
    IFS="/"
    paths=(${@:$#})
    IFS="$OLD_IFS"
    if [ -d ${@:$#} ]; then
        :
    elif [ -f ${@:$#} ]; then
        unset paths[`expr ${#paths[*]} - 1`]
    else
        echo "[RUN ERROR]: The start path is not specified or doesn't exists."
        exit 1
    fi
    if [ -z ${paths[1]} ]; then
        echo "[RUN ERROR]: Tests must belong to a certain project."
        exit 1
    else
        project=${paths[1]}
        if [ -z ${paths[2]} ]; then
            sub_project=""
        else
            sub_project=${paths[2]}
        fi
        python3 -m run_robot \
        --nostatusrc \
        --variable LOCAL_HOST:`hostname` \
        --variable Project:$project \
        --variable Sub_Project:$sub_project \
        --variablefile resources/$project/variables.py \
        $*
    fi
fi
# python3 -m run_robot --argumentfile runners/Demo/Internal_Chrome.txt
