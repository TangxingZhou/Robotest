#!/usr/bin/env bash

set -x
selenium_server_version=3.141.59
selenium_server_logs_dir=$1

nohup java -jar selenium-server-standalone-$selenium_server_version.jar -role hub -hubConfig hub_config.json > $selenium_server_logs_dir/selenium_server_hub.log &
sleep 2
nohup java -DWebdriver.chrome.driver=../chromedriver -jar selenium-server-standalone-$selenium_server_version.jar -role node -nodeConfig node_config.json > $selenium_server_logs_dir/selenium_server_node.log &
