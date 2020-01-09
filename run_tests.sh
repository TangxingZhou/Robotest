#!/usr/bin/env bash

set -e

workspace=$(cd `dirname $0`; pwd)
PYTHONPATH=$workspace
selenium_server_starter_dir=resources/web_drivers/selenium_server

function terminate_service() {
    if [ $(ps -ef | grep -v grep | grep $1 | wc -l) -ne 0 ]; then
        for pid in $(ps -ef | grep -v grep | grep $1 | awk '{print $2}')
        do
            kill $pid
        done
        sleep 2
    fi
}

function parse_robot_start_suite() {
    OLD_IFS="$IFS"
    IFS="/"
    local paths=($1)
    IFS="$OLD_IFS"
    if [ -d $1 ]; then
        :
    elif [ -f $1 ]; then
        unset paths[-1]
    else
        echo >&2 "[RUN ERROR]: The start path is not specified or doesn't exists."
        exit 1
    fi
    local run_arguments="--variable LOCAL_HOST:`hostname`"
    if [ -z ${paths[1]} ]; then
        echo >&2 "[RUN WARNING]: Tests belong to an unknown project."
        run_arguments="$run_arguments --variable Project:Unknown --variable Sub_Project:\"\""
    else
        run_arguments="$run_arguments --variable Project:${paths[1]}"
        if [ -z ${paths[2]} ]; then
            run_arguments="$run_arguments --variable Sub_Project:\"\""
        else
            run_arguments="$run_arguments --variable Sub_Project:${paths[2]}"
        fi
    fi
    echo $run_arguments
}

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
elif [ "$1" = "--cluster" ]; then
    run_arguments=$(parse_robot_start_suite ${@:$#})
    project=$(echo $run_arguments | grep -oE "\<Project:[^ ]*\>" | awk -F ':' '{print $2}')
    OLD_IFS="$IFS"
    login_pwd=123456
    if [ "$2" = "localhost" -o "$2" = "127.0.0.1" ]; then
        cluster_info=$(scripts/TOS/cluster.sh)
    else
        IFS=":"
        login=($2)
        login_ip=${login[0]}
        if [ -z ${login[1]} ]; then :; else login_pwd=${login[1]}; fi
        cluster_info=$(sshpass -p$login_pwd ssh root@$login_ip 'bash -s' < scripts/$project/cluster.sh)
    fi
    shift 2
    TOS_NODES=($cluster_info)
    IFS=","
    TOS_NODES=(${TOS_NODES[-1]})
    IFS="$OLD_IFS"
    for ((i=0; i<${#TOS_NODES[*]}; i++)); do
        if [ `expr $i % 2` -eq 1 ]; then
            grep -q "${TOS_NODES[$i]}" /etc/hosts || echo "${TOS_NODES[`expr $i - 1`]} ${TOS_NODES[$i]}" >> /etc/hosts && continue
        fi
    done
    run_arguments="$run_arguments --variablefile variables/$project/variables.py:$cluster_info:$login_pwd"
    python3 -m run_robot $run_arguments $*
else
    run_arguments=$(parse_robot_start_suite ${@:$#})
    run_arguments="$run_arguments --variablefile resources/$(echo $run_arguments | grep -oE "\<Project:[^ ]*\>" | awk -F ':' '{print $2}')/variables.py"
    python3 -m run_robot $run_arguments $*
fi
# python3 -m run_robot --argumentfile runners/Demo/Internal_Chrome.txt
