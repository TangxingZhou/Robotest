#!/usr/bin/env bash

# Install some basic tools
set -x
cd `dirname $0`

if [ -z $(grep nameserver /etc/resolv.conf) ]; then
    cat > /etc/resolv.conf <<EOF
search transwarp.local
nameserver 8.8.8.8
nameserver 10.10.0.10
options ndots:5
EOF
fi

yum install -y sshpass java-1.8.0-openjdk git net-tools bind-utils wget ntpdate
if [ ! -x "$(command -v pvcreate)" ]; then
    yum install -y lvm2
fi

# Update the date time
ntpdate cn.pool.ntp.org

# Install chaosblade
# wget http://172.26.5.50:31000/COMMON_SOFTWARE/chaosblade.tar.gz
# tar -xvf chaosblade.tar.gz
# mv chaosblade /usr/local/
# export PATH=/usr/local/chaosblade:$PATH
# rm -f chaosblade.tar.gz

# Format one disk and mount for docker
if grep /var/lib/docker /etc/fstab; then
    :
else
    mkfs.xfs /dev/vdb -n ftype=1
    mkdir -p /var/lib/docker
    uuid=$(blkid /dev/vdb -s UUID | awk -F '"' '{print $2}')
    echo "UUID=$uuid /var/lib/docker xfs defaults,uquota,pquota 0 0" >> /etc/fstab
fi
mount -a

# Add some alias for TOS
if grep JAVA_HOME /root/.bashrc; then
    :
else
    cat >> /root/.bashrc <<EOF
export JAVA_HOME=/usr/lib/jvm/jre

alias puid='puid() { if [ -z \$1 ]; then echo >&2 -e "Get the UID of Pod.\nUsage: puid [pod name] [namespace](default if not given)"; else if [ -z \$2 ]; then ns=default; else ns=\$2; fi; kubectl get po \$1 -n \$ns -o=jsonpath='{.spec.nodeName}'; if [ \$? -eq 0 ]; then echo; kubectl get po \$1 -n \$ns -o=jsonpath='{.metadata.uid}'; echo; fi; fi; }; puid'
alias cdpv='cdpv() { if [ -z \$1 ]; then echo >&2 -e "CD to the local volumes of Pod.\nUsage: cdpv [pod name] [namespace](default if not given)"; else if [ -z \$2 ]; then ns=default; else ns=\$2; fi; pod_host=\$(kubectl get po \$1 -n \$ns -o=jsonpath='{.spec.nodeName}'); if [ \$? -eq 0 ]; then uid=\$(kubectl get po \$1 -n \$ns -o=jsonpath='{.metadata.uid}'); if [ \$pod_host = `hostname` ]; then cd /var/lib/kubelet/pods/\$uid/volumes/transwarp.io~tosdisk-pv; else echo >&2 -e "Please get into the PVs of the pod at:\n\$pod_host\n/var/lib/kubelet/pods/\$uid/volumes/transwarp.io~tosdisk-pv"; fi; fi; fi; }; cdpv'
alias pvcs='pvcs() { if [ -z \$1 ]; then echo >&2 -e "Get PVCs of Pod.\nUsage: pvcs [pod name] [namespace](default if not given)"; else if [ -z \$2 ]; then ns=default; else ns=\$2; fi; pod_pvcs=\$(kubectl get po \$1 -n \$ns -o=jsonpath='{.spec.volumes[*].persistentVolumeClaim.claimName}'); if [ \$? -eq 0 ]; then if [ -z "\$pod_pvcs" ]; then echo >&2 -e "Pod \$1 has no PVCs."; else kubectl get pvc -n \$ns \$pod_pvcs; fi; fi; fi; }; pvcs'
EOF
fi

# Install python3 & pip3
if [ ! -z $1 ]; then
    if [ ! -x "$(command -v python3)" ]; then
        yum install -y gcc zlib-devel bzip2-devel sqlite sqlite-devel openssl-devel
        if [ ! -f Python-$1.tgz ]; then wget https://www.python.org/ftp/python/$1/Python-$1.tgz; fi
        if [ -d Python-$1 ]; then rm -rf Python-$1; fi
        tar -xf Python-$1.tgz
        cd Python-$1
        ./configure
        make && make install
        cd -
        rm -rf Python-$1 Python-$1.tgz
        python3 -m pip install -U pip -i https://mirrors.aliyun.com/pypi/simple
    fi
fi
