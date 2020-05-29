#!/usr/bin/env bash

domains=()

workspace=$(cd `dirname $0`; pwd)
default_time_out=300

function yum_install_packages {
    for package in $*; do
        yum -y install $package
        if [[ $? -ne 0 ]]; then
            echo >&2 "[YUM Error]: Fail to install $package."
            exit 1
        fi
    done
}

function env_init {
    # Install pip
    if [[ ! -x "$(command -v pip)" ]]; then yum_install_packages epel-release python-pip; fi
    # Install shyaml
    if [[ ! -x "$(command -v shyaml)" ]]; then
        pip install shyaml -i https://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com
        if [[ $? -ne 0 ]]; then
            echo >&2 "[PIP Error]: Fail to install shyaml."
            exit 1
        fi
    fi
    # Install guestmount
    if [[ ! -x "$(command -v guestmount)" ]]; then yum_install_packages libguestfs libguestfs-tools; fi
    # Install bc
    if [[ ! -x "$(command -v bc)" ]]; then yum_install_packages bc; fi
    # Install sshpass
    if [[ ! -x "$(command -v sshpass)" ]]; then yum_install_packages sshpass; fi
}

function get_domain_status() {
    if [ -z $1 ]; then
        echo >&2 "[Domain Error]: Domain name is not specified."
    else
        local status=$(virsh domstate $1 2>/dev/null)
        if [ $? -ne 0 ]; then
            echo >&2 "[Domain Error]: Domain $1 is not found."
        fi
        echo $status
    fi
}

function start_domains {
    for domain in $*; do
        local status=$(get_domain_status $domain)
        if [ "$status" = "shut off" -o "$status" = "关闭" ]; then
            echo >&2 "[Domain Info]: Starting $domain."
            virsh start $domain
            [ $? -ne 0 ] && echo >&2 "[Domain Error]: Fails to start $domain." && continue
            local stop=0
            while [ $stop -lt $default_time_out ]; do
                sleep 1
                virsh list --state-running --name | grep -q "^${domain}$"
                if [ $? -eq 0 ]; then
                    echo >&2 "[Domain Info]: $domain is successfully started."
                    break
                else
                    stop=`expr $stop + 1`
                fi
            done
            if [ $stop -eq $default_time_out ]; then
                echo >&2 "[Domain Error]: Fails to start $domain within ${default_time_out}s."
            fi
        else
            echo >&2 "[Domain Warning]: Status of $domain is $status, won't start it."
        fi
    done
}

function shutdown_domains() {
    for domain in $*; do
        local status=$(get_domain_status $domain)
        if [ "$status" = "running" ]; then
            echo  >&2 "[Domain Info]: Shutting down $domain."
            virsh shutdown $domain
            [ $? -ne 0 ] && echo >&2 "[Domain Error]: Fails to shutdown $domain." && continue
            local stop=0
            while [ $stop -lt $default_time_out ]; do
                sleep 1
                virsh list --state-shutoff --name | grep -q "^${domain}$"
                if [ $? -eq 0 ]; then
                    echo  >&2 "[Domain Info]: $domain is successfully shutdown."
                    break
                else
                    stop=`expr $stop + 1`
                fi
            done
            if [ $stop -eq $default_time_out ]; then
                echo >&2 "[Domain Error]: Fails to shutdown $domain within ${default_time_out}s."
            fi
        else
            echo  >&2 "[Domain Warning]: Status of $domain is $status, won't shutdown it."
        fi
    done
}

function reboot_domains {
    for domain in $*; do
        local status=$(get_domain_status $domain)
        if [ "$status" = "running" ]; then
            echo >&2 "[Domain Info]: Rebooting $domain."
            virsh reboot $domain
            [ $? -ne 0 ] && echo >&2 "[Domain Error]: Fails to reboot $domain." && continue
            local stop=0
            while [ $stop -lt $default_time_out ]; do
                sleep 1
                virsh list --state-running --name | grep -q "^${domain}$"
                if [ $? -eq 0 ]; then
                    echo >&2 "[Domain Info]: $domain is successfully reboot."
                    break
                else
                    stop=`expr $stop + 1`
                fi
            done
            if [ $stop -eq $default_time_out ]; then
                echo >&2 "[Domain Error]: Fails to reboot $domain within ${default_time_out}s."
            fi
        elif [ "$status" = "shut off" -o "$status" = "关闭" ]; then
            start_domains $domain
        else
            echo >&2 "[Domain Warning]: Status of $domain is $status, won't reboot it."
        fi
    done
}

function delete_domains {
    for domain in $*; do
        local status=$(get_domain_status $domain)
        if [ "$status" = "running" -o "$status" = "shut off" -o "$status" = "关闭" ]; then
            echo >&2 "[Domain Info]: Deleting $domain."
            local domain_disk_files=$(virsh domblklist $domain | sed -n '3,$p')
            delete_snapshots_for_domain $domain
            virsh destroy $domain && virsh undefine $domain
            [ $? -ne 0 ] && echo >&2 "[Domain Error]: Fails to delete $domain." && continue
            local stop=0
            while [ $stop -lt $default_time_out ]; do
                sleep 1
                virsh list --all --name | grep -q "^${domain}$"
                if [ $? -ne 0 ]; then
                    echo >&2 "[Domain Info]: $domain is successfully deleted."
                    for disk_file in ${domain_disk_files[@]}; do
                        if [ -f $disk_file ]; then
                            echo >&2 "[Domain Info]: Deleting disk file $disk_file for $domain."
                            rm -f $disk_file
                        fi
                    done
                    break
                else
                    stop=`expr $stop + 1`
                fi
            done
            if [ $stop -eq $default_time_out ]; then
                echo >&2 "[Domain Error]: Fails to delete $domain within ${default_time_out}s."
            fi
        else
            echo >&2 "[Domain Warning]: Status of $domain is $status, won't delete it."
        fi
    done
}

function attach_disk_for_domains {
    for domain in $*; do
        local domain_disk_files=$(virsh domblklist $domain | sed -n '3,$p')
        local disks=()
        local sources=()
        local found=1
        local source_folder=/root
        for disk_file in ${domain_disk_files[@]}; do
            if [ -f $disk_file ]; then
                disks=(${disks[@]} $disk_file)
                source_folder=${disk_file%/*}
            else
                sources=(${sources[@]} $disk_file)
            fi
        done
        for ((i=0; i<${#disks[@]}; i++)); do
            if [ "${disks[$i]}" = "$disk_symbol" ]; then
                echo >&2 "[Disk Error]: Disk symbol $disk_symbol exists for domain $domain."
                found=0
                break
            fi
        done
        if [ $found -eq 0 ]; then
            continue
        else
            shutdown_domains $domain
            qemu-img create -f qcow2 $source_folder/${domain}_$disk_symbol.qcow2 $disk_size
            virsh attach-disk --domin $domain  --source $source_folder/${domain}_$disk_symbol.qcow2 --target $disk_symbol --subdriver qcow2 --config --live
            start_domains $domain
        fi
    done
}

function resize_disk_for_domains {
    for domain in $*; do
        local domain_disk_files=$(virsh domblklist $domain | sed -n '3,$p')
        local disks=()
        local sources=()
        for disk_file in ${domain_disk_files[@]}; do
            if [ -f $disk_file ]; then
                disks=(${disks[@]} $disk_file)
            else
                sources=(${sources[@]} $disk_file)
            fi
        done
        for ((i=0; i<${#disks[@]}; i++)); do
            if [ "${disks[$i]}" = "$disk_symbol" ]; then
                shutdown_domains $domain
                qemu-img resize ${sources[$i]} $disk_size  # qemu-img resize /root/test.qcow2 +1G
                start_domains $domain
                break
            fi
        done
    done
}

function create_snapshots_for_domains {
    for domain in $*; do
        domain_has_snapshot $domain $snapshot_name
        if [ $? -ne 0 ]; then
            shutdown_domains $domain
            echo >&2 "[Snapshot Info]: Creating snapshot $snapshot_name for domain $domain."
            virsh snapshot-create-as --domain $domain --name $snapshot_name &
            start_domains $domain
        fi
    done
    wait
}

function revert_snapshots_for_domains {
    for domain in $*; do
        domain_has_snapshot $domain $snapshot_name
        if [ $? -eq 0 ]; then
            shutdown_domains $domain
            echo >&2 "[Snapshot Info]: Reverting snapshot $snapshot_name for domain $domain."
            virsh snapshot-revert $domain $snapshot_name &
        fi
    done
    wait
    for domain in $*; do
        reboot_domains $domain
    done
}

function list_snapshots_for_domains {
    for domain in $*; do
        local status=$(get_domain_status $domain)
        if [ -z $status ]; then
            echo >&2 "[Domain Error]: $domain is not found."
        else
            echo >&2 "[Snapshot Info]: List snapshots for domain $domain."
            virsh snapshot-list $domain
        fi
    done
}

function delete_snapshot_for_domains {
    for domain in $*; do
        domain_has_snapshot $domain $snapshot_name
        if [ $? -eq 0 ]; then
            echo >&2 "[Snapshot Info]: Deleting snapshot $snapshot_name for domain $domain."
            virsh snapshot-delete $domain $snapshot_name
        fi
    done
}

function domain_has_snapshot {
    local has=1
    if [ -z $1 ]; then
        echo >&2 "[Domain Error]: Domain name is not specified."
    else
        if [ -z $2 ]; then
            echo >&2 "[Snapshot Error]: Snapshot name is not specified."
        else
            local status=$(get_domain_status $1)
            if [ -z $status ]; then
                echo >&2 "[Domain Error]: $1 is not found."
            else
                virsh snapshot-list --name $1 | grep -q "^$2$"
                if [ $? -eq 0 ]; then
                    has=0
                    echo >&2 "[Snapshot Info]: Domain $1 has snapshot $2."
                else
                    echo >&2 "[Snapshot Info]: Domain $1 does not have snapshot $2."
                fi
            fi
        fi
    fi
    return $has
}

function delete_snapshots_for_domain {
    if [ -z $1 ]; then
        echo >&2 "[Domain Error]: Please give the domain name to delete its snapshots."
        return 1
    else
        local snapshots=$(virsh snapshot-list --name $1)
        if [ $? -eq 0 ]; then
            for snapshot in $snapshots; do
                echo >&2 "[Snapshot Info]: Deleting snapshot $snapshot for domain $domain."
                virsh snapshot-delete $domain $snapshot
            done
        else
            echo >&2 "[Domain Error]: Fails to list snapshots for domain $1."
        fi
        return $?
    fi
}

function get_domains {
    if [ ${#domains[@]} -eq 0 ]; then
        if [ -z $cluster_name ]; then
            echo >&2 "[Args Error]: No domains are specified. Please set domains with option --domains [domain1,domain2] or set cluster name with option --cluster <cluster name>."
            exit 1
        else
            local nodes_num=`cat ${cluster_name}.yml | shyaml get-length nodes`
            for i in `seq 1 $nodes_num`; do
                local node_hostname=$(cat ${cluster_name}.yml | shyaml keys-0 nodes.`expr $i - 1`)
                local os=$(cat ${cluster_name}.yml | shyaml get-value nodes.`expr $i - 1`.$node_hostname.os)
                local ip=$(cat ${cluster_name}.yml | shyaml get-value nodes.`expr $i - 1`.$node_hostname.ip)
                domains=(${domains[@]} ${os}_${ip//./_})
            done
        fi
    fi
}

while [[ $# -gt 0 ]]
do
    key="$1"
    case $key in
    --action)
        # create, start, shutdown, reboot, attach-disk, resize-disk, create-snapshot, list-snapshot, revert-snapshot, delete-snapshot
        action=$2
        if [ -z $action -o ${action:0:1} = "-" ]; then
            echo >&2 "[Args Error]: Action is not specified."
            exit 2
        fi
        shift 2
        ;;
    --domains)
        domains=$2
        if [ -z $domains -o ${domains:0:1} = "-" ]; then
            echo >&2 "[Args Error]: Domains are not specified."
            exit 2
        fi
        domains=(${domains//,/ })
        shift 2
        ;;
    --snapshot-name)
        snapshot_name=$2
        if [ -z $snapshot_name -o ${snapshot_name:0:1} = "-" ]; then
            echo >&2 "[Args Error]: Snapshot name is not specified."
            exit 2
        fi
        shift 2
        ;;
    --disk-symbol)
        disk_symbol=$2
        if [ -z $disk_symbol -o ${disk_symbol:0:1} = "-" ]; then
            echo >&2 "[Args Error]: Disk symbol is not specified."
            exit 2
        fi
        shift 2
        ;;
    --disk-size)
        disk_size=$2
        if [ -z $disk_size -o ${disk_size:0:2} = "--" ]; then
            echo >&2 "[Args Error]: Disk Size is not specified."
            exit 2
        fi
        shift 2
        ;;
    --cluster)
        cluster_name=$2
        if [ -z $cluster_name -o ${cluster_name:0:1} = "-" ]; then
            echo >&2 "[Args Error]: Cluster name is not specified."
            exit 2
        else
            if [ ! -f ${cluster_name}.yml ]; then
                echo >&2 "[Args Error]: Config file ${cluster_name}.yml for cluster $cluster_name is not found."
                exit 1
            fi
        fi
        shift 2
        ;;
    *)
        shift
        ;;
    esac
done

get_domains
if [ $action = "create" ]; then
    if [ -z $cluster_name ]; then
        echo >&2 "[Args Error]: Cluster name should be specified with option --cluster [cluster name]."
        exit 1
    else
        bash kvm_install.sh ${cluster_name}.yml
    fi
elif [ $action = "start" ]; then
    start_domains ${domains[*]}
elif [ $action = "shutdown" ]; then
    shutdown_domains ${domains[*]}
elif [ $action = "reboot" ]; then
    reboot_domains ${domains[*]}
elif [ $action = "delete" ]; then
    delete_domains ${domains[*]}
elif [ $action = "attach-disk" ]; then
    if [ -z $disk_symbol ]; then
        echo >&2 "[Args Error]: Disk symbol should be specified with option --disk-symbol [disk symbol]."
        exit 1
    elif [ -z $disk_size ]; then
        echo >&2 "[Args Error]: Disk size should be specified with option --disk-size [disk size]."
        exit 1
    else
        attach_disk_for_domains ${domains[*]}
    fi
elif [ $action = "resize-disk" ]; then
    if [ -z $disk_symbol ]; then
        echo >&2 "[Args Error]: Disk symbol should be specified with option --disk-symbol [disk symbol]."
        exit 1
    elif [ -z $disk_size ]; then
        echo >&2 "[Args Error]: Disk size should be specified with option --disk-size [disk size]."
        exit 1
    else
        resize_disk_for_domains ${domains[*]}
    fi
elif [ $action = "create-snapshot" ]; then
    if [ -z $snapshot_name ]; then
        echo >&2 "[Args Error]: Snapshot name should be specified with option --snapshot-name [snapshot name]."
        exit 1
    else
        create_snapshots_for_domains ${domains[*]}
    fi
elif [ $action = "list-snapshot" ]; then
    list_snapshots_for_domains ${domains[*]}
elif [ $action = "revert-snapshot" ]; then
    if [ -z $snapshot_name ]; then
        echo >&2 "[Args Error]: Snapshot name should be specified with option --snapshot-name [snapshot name]."
        exit 1
    else
        revert_snapshots_for_domains ${domains[*]}
    fi
elif [ $action = "delete-snapshot" ]; then
    if [ -z $snapshot_name ]; then
        echo >&2 "[Args Error]: Snapshot name should be specified with option --snapshot-name [snapshot name]."
        exit 1
    else
        delete_snapshot_for_domains ${domains[*]}
    fi
else
    echo >&2 "[Args Error]: The action \"$action\"is not supported currently."
    exit 2
fi
