
$env:PYTHONPATH = $PSScriptRoot
.\.venv\Scripts\activate.ps1

function SSH-Login-With-Key($ip, $user="root") {
    ssh -o NumberOfPasswordPrompts=0 -o StrictHostKeyChecking=no $user@$ip hostname>/dev/null
    if ($? -eq $false) {
        if (-not(test-path "$env:USERPROFILE\.ssh\*" -include id_rsa)) {
            ssh-keygen -t rsa -f "$env:USERPROFILE/.ssh/id_rsa"
        }
        sh ssh-copy-id -i "$env:USERPROFILE/.ssh/id_rsa.pub" $user@$ip
    }
}

function Get-TOS-Cluster-Info($ip, $user="root") {
    SSH-Login-With-Key $ip $user
    $Kubectl_Nodes_Info = "
    if [ -x `"`"`$(command -v kubectl)`"`" ]; then
        for node in `$(kubectl get node --no-headers|awk '{print `$1}')
        do
            node_ip=`$(kubectl get node `$node --no-headers -o=jsonpath='{.status.addresses[?(@.type==`"`"InternalIP`"`")].address}')
            cluster_nodes=`$cluster_nodes,`$node_ip,`$node
            master=`$(kubectl get node `$node --no-headers -o=jsonpath='{.metadata.labels.master}')
            if [ `"`"`$master`"`" = `"true`" ]
            then
                master_nodes=`$master_nodes,`$node
            fi
        done
        echo `$(hostname):`${master_nodes:1}:`${cluster_nodes:1}
    else
        echo `"`"`"`"
    fi
    " -replace "\r", ""
    return $(ssh $user@$ip $Kubectl_Nodes_Info)
}

function Parse-Robot-Start-Suite($start_suite=".\tests") {
    if (test-path $start_suite -pathType container) {
        $suite_dir = $start_suite
    }
    elseif (test-path $start_suite -pathType leaf) {
        $suite_dir = split-path $start_suite -parent
    }
    else {
        write-host "[RUN ERROR]: The start path $start_suite is not specified or doesn't exists." -foregroundcolor red
        exit(1)
    }
    $pathes = $suite_dir -split "\\"
    if ($pathes.Count -lt 2) {
        write-host "[RUN WARNING]: Tests belong to an unknown project." -foregroundcolor yellow
        $script:project, $sub_project = "Unknown", "`"`""
    }
    else {
        $script:project = $pathes[1]
        if ($pathes.Count -lt 3) {
            $sub_project = "`"`""
        }
        else {
            $sub_project = $pathes[2]
        }
    }
    return "--variable", "LOCAL_HOST:$env:COMPUTERNAME", "--variable", "Project:$script:project", "--variable", "Sub_Project:$sub_project"
}

if ($args[0] -eq "--init") {
    python -m pip install --user -r requirements.txt
}
elseif ($args[0] -eq "--cluster") {
    if ($args.count -lt 2) {
        write-host "[RUN ERROR]: TOS main node IP is a must." -foregroundcolor red
        exit(1)
    }
    elseif ($args.count -eq 2) {
        write-host "[RUN ERROR]: The path for tests to run is a must." -foregroundcolor red
        exit(1)
    }
    $args[-1] = $args[-1].trim('.').trim('\')
    $run_arguments = Parse-Robot-Start-Suite $args[-1]
    $login_pwd = "123456"
    if ($args[1] -eq "localhost" -or $args[1] -eq "127.0.0.1") {
        $cluster_info=$(bash .\scripts\TOS\cluster.sh)
    }
    else {
        $login = $args[1] -split ":"
        $login_ip = $login[0]
        if ($login.Count -eq 1) {
            $login_pwd = "123456"
        } else {
            $login_pwd = $login[1]
        }
        $cluster_info = $(Get-TOS-Cluster-Info $login_ip "root")
    }
    if ($cluster_info -eq "") {
        write-host "[RUN ERROR]: Unable to get the TOS cluster info." -foregroundcolor red
        exit(1)
    }
    $tos_nodes = $cluster_info -split ":"
    $tos_nodes = $tos_nodes[-1] -split ","
    for ($i=0; $i -lt $tos_nodes.count; $i++) {
        if ($i % 2 -eq 1) {
            $node_ip, $node_host = $tos_nodes[$i - 1], $tos_nodes[$i]
            if((get-content $env:windir\System32\drivers\etc\hosts |?{$_ -match "\s$node_host"}) -eq $null) {
                "`n$node_ip $node_host" | Out-File -FilePath "$env:windir\System32\drivers\etc\hosts" -Append -encoding ascii
                write-host "[RUN WARNING]: Add TOS node info of `"$node_ip $node_host`" into $env:windir\System32\drivers\etc\hosts." -foregroundcolor yellow
            }
        }
    }
    $run_arguments = $run_arguments + "--variablefile" + "variables\$script:project\variables.py:${cluster_info}:$login_pwd" + $args[2..$args.count]
    python -m run_robot $run_arguments
}
else {
    python -m run_robot $args
}