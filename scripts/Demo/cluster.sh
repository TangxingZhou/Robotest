#!/usr/bin/env bash
set -e

function get_kubernetes_version() {
    local ver=$(kubectl --version|grep -o "v[\.0-9]*")
    echo ${ver:1}
}

function apiserver_insecure_port_enable() {
    sed -i 's/\(.*insecure-bind-address\).*/\1=0.0.0.0 \\/g' /opt/kubernetes/manifests-multi/kube-apiserver.manifest
    timeout 2m bash -c "while true; do { curl $(hostname):8080/api/v1/nodes>>/dev/null 2>&1 && if [ $? -eq 0 ]; then break; else sleep 1; fi; } || { sleep 1; }; done"
    local rc=$?
    if [ $rc -ne 0 ]; then
        echo "[INIT WARNNING] Kube API \"$(hostname):8080\" is not ready within 2mins."
        exit $rc
    fi
}

function get_cluster_nodes() {
    if [ -x "$(command -v kubectl)" ]; then
        for node in $(kubectl get node --no-headers|awk '{print $1}')
        do
            node_ip=$(kubectl get node $node --no-headers -o=jsonpath='{.status.addresses[?(@.type=="InternalIP")].address}')
            cluster_nodes=$cluster_nodes,$node_ip,$node
            master=$(kubectl get node $node --no-headers -o=jsonpath='{.metadata.labels.master}')
            if [ "$master" = "true" ]
            then
                master_nodes=$master_nodes,$node
            fi
        done
    else
        OLD_IFS="$IFS"
        IFS=","
        TOS_NODES_IP=($TOS_CLUSTER_HOSTS_IP)
        TOS_NODES_HN=($TOS_CLUSTER_HOSTS_NAME)
        IFS="$OLD_IFS"
        for ((i=`expr ${#TOS_NODES_HN[@]} - 1`; i >= 0; i--)); do
            node_host_name=${TOS_NODES_HN[i]}
            node_host_ip=${TOS_NODES_IP[i]}
            cluster_nodes=$cluster_nodes,$node_host_ip,$node_host_name
            node_host_name_upper=$(echo $node_host_name | tr 'a-z' 'A-Z')
            node_roles=$(printenv | grep "TOS_CLUSTER_NODE_${node_host_name_upper//-/_}_ROLES" | awk -F '=' '{print $2}')
            if [ -z $node_roles ]; then
                continue
            else
                OLD_IFS="$IFS"
                IFS=","
                node_roles=($node_roles)
                IFS="$OLD_IFS"
            fi
            for role in ${node_roles[@]}; do
                if [ "$role" = "master" ]; then
                    master_nodes=$master_nodes,$node_host_name
                    break
                fi
            done
        done
    fi
    echo $(hostname):${master_nodes:1}:${cluster_nodes:1}
}

if [ "$1" = "version" ]; then
    get_kubernetes_version
else
    apiserver_insecure_port_enable
    get_cluster_nodes
fi
