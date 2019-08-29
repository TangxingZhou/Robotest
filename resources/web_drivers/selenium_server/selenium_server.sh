#!/usr/bin/env bash

set -e

selenium_server_starter_dir=resources/web_drivers/selenium_server
selenium_server_version=3.141.59
chrome_driver_path=../chromedriver
selenium_server_logs_dir=`pwd`/out

function terminate_selenium_server() {
    if [ $(ps -ef | grep -v grep | grep selenium-server | wc -l) -ne 0 ]; then
        for pid in $(ps -ef | grep -v grep | grep selenium-server | awk '{print $2}')
        do
            kill $pid
        done
        sleep 2
    fi
}

function start_selenium_server() {
    nohup java -jar selenium-server-standalone-$selenium_server_version.jar -role hub -hubConfig hub_config.json \
    > $selenium_server_logs_dir/selenium_server_hub.log &
    sleep 2
    nohup java -Dwebdriver.chrome.driver=$chrome_driver_path -jar selenium-server-standalone-$selenium_server_version.jar \
    -role node -nodeConfig node_config.json > $selenium_server_logs_dir/selenium_server_node.log &
}

if [ "$1" = "-s" ]; then
    terminate_selenium_server
    cd $selenium_server_starter_dir
    start_selenium_server
    cd -
elif [ "$1" = "-t" ]; then
    terminate_selenium_server
fi
