#!/usr/bin/env bash

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
    if [[ ! -x "$(command -v virsh)" ]]; then yum_install_packages virt-manager; fi
    # Install guestmount
    if [[ ! -x "$(command -v guestmount)" ]]; then yum_install_packages libguestfs libguestfs-tools; fi
    # Install bc
    if [[ ! -x "$(command -v bc)" ]]; then yum_install_packages bc; fi
    # Install sshpass
    if [[ ! -x "$(command -v sshpass)" ]]; then yum_install_packages sshpass; fi
}

env_init

WORKSPACE=$(cd `dirname $0`; pwd)

# Owncloud Params
OWNCLOUD_FILE_API="http://172.16.1.97:8080/remote.php/webdav/TEMPLATE"
OWNCLOUD_USERNAME="public"
OWNCLOUD_PASSWORD="public"

CONF_FILE=$WORKSPACE/$1
[ ! -f $CONF_FILE ] && echo "$CONF_FILE does not exist." && exit 1
HOST_NUM=`cat $CONF_FILE | shyaml get-length nodes`
for i in `seq 1 $HOST_NUM`; do
    HOST_HOSTNAME=$(cat $CONF_FILE | shyaml keys-0 nodes.`expr $i - 1`)
    HOST_IP=$(cat $CONF_FILE | shyaml get-value nodes.`expr $i - 1`.$HOST_HOSTNAME.ip)
    HOST_NETMASK=$(cat $CONF_FILE | shyaml get-value nodes.`expr $i - 1`.$HOST_HOSTNAME.netmask)
    HOST_GATEWAY=$(cat $CONF_FILE | shyaml get-value nodes.`expr $i - 1`.$HOST_HOSTNAME.gateway)
    HOST_OS=$(cat $CONF_FILE | shyaml get-value nodes.`expr $i - 1`.$HOST_HOSTNAME.os)
    HOST_MEM=$(cat $CONF_FILE | shyaml get-value nodes.`expr $i - 1`.$HOST_HOSTNAME.memory)
    HOST_CPU=$(cat $CONF_FILE | shyaml get-value nodes.`expr $i - 1`.$HOST_HOSTNAME.vcpu)
    HOST_DISKPATH=$(cat $CONF_FILE | shyaml get-value nodes.`expr $i - 1`.$HOST_HOSTNAME.diskpath)
    HOST_DISK_NUM=$(cat $CONF_FILE | shyaml get-length nodes.`expr $i - 1`.$HOST_HOSTNAME.datadisks)
    HOST_DISKLIST=$(cat $CONF_FILE | shyaml keys nodes.`expr $i - 1`.$HOST_HOSTNAME.datadisks)
    HOST_DISKARR=(${HOST_DISKLIST// /})
    HOST_CAPACITYLIST=$(cat $CONF_FILE | shyaml values nodes.`expr $i - 1`.$HOST_HOSTNAME.datadisks)
    HOST_CAPACITYARR=(${HOST_CAPACITYLIST// /})
    VM_NAME=${HOST_OS}_${HOST_IP//./_}
    HOST_TOTAL_SPACE=0
    for((m=0; m<${#HOST_CAPACITYARR[*]}; m++)); do
        HOST_TOTAL_SPACE=`echo "$HOST_TOTAL_SPACE + ${HOST_CAPACITYARR[$m]%G}" | bc`
    done


:<<!
STEP 1
Select One Available Data DISKPATH
!
if [[ -z "$HOST_DISKPATH" ]]; then
    MOUNTPOINT=`df -h|cat -n|awk -F ' ' '{print $7}'`
    declare -A dic
    index=0
    for line in ${MOUNTPOINT}; do
        let index++
        if [[ "$line" =~ "/mnt/disk" ]]; then
            printrow=${index}"p"
            avail_volume=`df -h | sed -n ${printrow}|awk -F ' ' '{print $4}'`
            if [[ "$avail_volume" =~ "T" ]];then
                avail_volume_value=`echo ${avail_volume%T}`
                dic[$line]=`echo "${avail_volume_value} * 1000" | bc `
            else
                avail_volume_value=`echo ${avail_volume%G}`
                dic[$line]=${avail_volume_value}
            fi
        fi
    done
    for key in $(echo ${!dic[*]}); do
        value=${dic[$key]}
        if [[ ${value%.*} -gt $HOST_TOTAL_SPACE ]]; then
            HOST_DISKPATH=${key}
            break
        else
            echo "NO ENOUGH SPACE!!"
            exit 1
        fi
    done
fi


:<<!
STEP 2
Download OS Model File & Create Data Disks
!
if [[ ! -f /root/${HOST_OS}_model.qcow2 ]]; then
   curl -u ${OWNCLOUD_USERNAME}:${OWNCLOUD_PASSWORD} ${OWNCLOUD_FILE_API}/${HOST_OS}/${HOST_OS}_model.qcow2 --output /root/${HOST_OS}_model.qcow2
fi
[[ ! -d $HOST_DISKPATH/image ]] && mkdir -p $HOST_DISKPATH/image
cp /root/${HOST_OS}_model.qcow2  ${HOST_DISKPATH}/image/${VM_NAME}.qcow2
for((n=0; n<${HOST_DISK_NUM}; n++)); do
    qemu-img  create -f qcow2 ${HOST_DISKPATH}/image/${VM_NAME}_${HOST_DISKARR[$n]}.qcow2 ${HOST_CAPACITYARR[$n]} || exit 1
    source_file[$n]=`echo ${HOST_DISKPATH}/image/${VM_NAME}_${HOST_DISKARR[$n]}.qcow2`
done


:<<!
STEP 3
Create VM Host
!
virt-install --name ${VM_NAME} --ram ${HOST_MEM} --vcpu ${HOST_CPU} --os-variant Generic --disk path=${HOST_DISKPATH}/image/${VM_NAME}.qcow2,bus=virtio --vnc --network bridge=br0,model=virtio --wait=0 --boot hd || exit 1
if [[ ! -d /media/virtimage ]];then
    mkdir -p /media/virtimage
else
    rm -rf /media/virtimage && mkdir -p /media/virtimage
fi
sleep 5s && virsh destroy ${VM_NAME} || exit 1

case ${HOST_OS} in
    "centos77")
        guestmount -d ${VM_NAME} -m /dev/sda3 --rw /media/virtimage || exit 1
        echo "${HOST_HOSTNAME}" > /media/virtimage/etc/hostname || exit 1
        ;;
    "centos72" | "centos74" | "centos76")
        guestmount -d ${VM_NAME} -m /dev/centos/root --rw /media/virtimage || exit 1
        echo "${HOST_HOSTNAME}" > /media/virtimage/etc/hostname || exit 1
        ;;
    "centos67")
        guestmount -d ${VM_NAME} -m /dev/mapper/VolGroup-lv_root --rw /media/virtimage || exit 1
        eval sed -i 's/localhost.localdomain/${HOST_HOSTNAME}/g' /media/virtimage/etc/sysconfig/network || exit 1
        ;;
    *)
        echo "Not Support OS" && exit 1
        ;;
esac
# if [ $i -eq 1 ]; then
#     echo "bash -x /root/init.sh 3.5.2" >> /media/virtimage/etc/rc.d/rc.local
#     echo "export HOSTIP=${HOST_IP}" >> /media/virtimage/root/.bashrc
#     cluster_hosts=""
#     cluster_ips=""
#     for host_name in ${HOSTS_HOSTNAME[@]}; do cluster_hosts=$cluster_hosts,$host_name; done
#     for ip in ${HOSTS_IP[@]}; do cluster_ips=$cluster_ips,$ip; done
#     echo "export TOS_CLUSTER_HOSTS_NAME=${cluster_hosts:1}" >> /media/virtimage/root/.bashrc
#     echo "export TOS_CLUSTER_HOSTS_IP=${cluster_ips:1}" >> /media/virtimage/root/.bashrc
# else
#     echo "bash -x /root/init.sh" >> /media/virtimage/etc/rc.d/rc.local
# fi
echo "bash -x /root/init.sh" >> /media/virtimage/etc/rc.d/rc.local
chmod +x /media/virtimage/etc/rc.d/rc.local
cat > /media/virtimage/etc/sysconfig/network-scripts/ifcfg-eth0 <<EOF
TYPE=Ethernet
BOOTPROTO=static
DEFROUTE=yes
PEERDNS=yes
PEERROUTES=yes
NAME=eth0
DEVICE=eth0
ONBOOT=yes
IPADDR=${HOST_IP}
GATEWAY=${HOST_GATEWAY}
NETMASK=${HOST_NETMASK}
EOF
sed -i 's/.*UseDNS.*/UseDNS no/' /media/virtimage/etc/ssh/sshd_config
sed -i 's/.*GSSAPIAuthentication.*/GSSAPIAuthentication no/' /media/virtimage/etc/ssh/sshd_config
sed -i 's/.*StrictHostKeyChecking.*/StrictHostKeyChecking no/' /media/virtimage/etc/ssh/ssh_config
sed -i 's/SELINUX=.*/SELINUX=disabled/' /media/virtimage/etc/selinux/config
cp ${WORKSPACE}/init.sh /media/virtimage/root/
# cp ${WORKSPACE}/Python-3.5.2.tgz /media/virtimage/root/
# sleep 5s
umount /media/virtimage && rm -rf /media/virtimage || exit 1


:<<!
STEP 4
Add disks for VM
!
VM_XML_PATH=/etc/libvirt/qemu
KVM_DISKS_TMP=/tmp/kvm_disks.txt
DiskRow=`cat -n ${VM_XML_PATH}/${VM_NAME}.xml|grep "</disk>"|awk -F ' ' '{print $1}'`
InsertRow=`expr ${DiskRow} + 1`
[[ -f $KVM_DISKS_TMP ]] && rm -f $KVM_DISKS_TMP
for((k=0; k<${HOST_DISK_NUM}; k++)); do
cat >> $KVM_DISKS_TMP << EOF
    <disk type='file' device='disk'>
      <driver name='qemu' type='qcow2'/>
      <source file='${source_file[$k]}'/>
      <target dev='${HOST_DISKARR[$k]}' bus='virtio'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x0`expr ${k} + 11`' function='0x0'/>
    </disk>
EOF
done
cat $KVM_DISKS_TMP | while read line; do
    echo ${line} | sed -i "${InsertRow}i\\${line}" ${VM_XML_PATH}/${VM_NAME}.xml
    InsertRow=$((${InsertRow} + 1))
done
virsh define ${VM_XML_PATH}/${VM_NAME}.xml
virsh start ${VM_NAME}
# sleep 30
num=0
while [ $num -lt 120 ]; do
    if ping ${HOST_IP} -c 1 -w 1 > /dev/null; then
        break
    else
        let num++
    fi
done
if [ $num -eq 120 ]; then
    echo >&2 "${VM_NAME}@${HOST_IP} is not reachable within 2 mins."
else
    echo "${VM_NAME}@${HOST_IP} is reachable now."
fi
done


:<<!
STEP 5
Create VM Snapshot
!
for ((i=0; i<$HOST_NUM; i++)); do
    HOST_HOSTNAME=$(cat $CONF_FILE | shyaml keys-0 nodes.$i)
    HOST_IP=$(cat $CONF_FILE | shyaml get-value nodes.$i.$HOST_HOSTNAME.ip)
    HOST_OS=$(cat $CONF_FILE | shyaml get-value nodes.$i.$HOST_HOSTNAME.os)
    HOST_SNAPSHOT=$(cat $CONF_FILE | shyaml get-value nodes.$i.$HOST_HOSTNAME.snapshot)
    VM_NAME=${HOST_OS}_${HOST_IP//./_}
    num=0
    while [ $num -lt 600 ]; do
        if sshpass -p123456 ssh -o StrictHostKeyChecking=no root@${HOST_IP} 'ps -ef | grep -v grep | grep -q /root/init.sh'; then
            sleep 1
            let num++
        else
            break
        fi
    done
    if [ $num -eq 600 ]; then
        echo >&2 "/root/init.sh is still running at ${HOST_IP} after 10 mins, won't create snapshot for ${VM_NAME}."
    else
        echo "Create snapshot for ${VM_NAME}."
        if [[ -n ${HOST_SNAPSHOT} ]]; then
            virsh snapshot-create-as ${VM_NAME} ${HOST_SNAPSHOT} || exit 1
        else
            virsh snapshot-create-as ${VM_NAME} mostclean || exit 1
        fi
    fi
done
