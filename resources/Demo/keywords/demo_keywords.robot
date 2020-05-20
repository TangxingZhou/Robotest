*** Settings ***
Resource    common.robot

*** Variables ***


*** Keywords ***
Demo Keyword
    log  This is a demo keyword.

kube_execCommandInPod
    [Documentation]     For more details, please refer to https://github.com/kubernetes-client/python/blob/master/examples/pod_exec.py
    [Arguments]     ${namespace}        ${name}         @{cmd}
    Import Library  kubernetes.stream
    ${v1_api}=      Get Library Instance    kubernetes.client.api.core_v1_api.CoreV1Api
    ${response}=    Stream                  ${v1_api.connect_get_namespaced_pod_exec}
    ...             ${name}     ${namespace}    command=${cmd}
    ...             stderr=${True}  stdin=${False}  stdout=${True}  tty=${False}
    [Return]    ${response}

kube_addPolicies
    [Documentation]
    ...     Add ingress/egress policies for network policy.
    ...     :param type[${type}]: The type of network policy, ingress or egress.
    ...     :param ports: Ports in list for ingress or egress policies.
    ...     :param netpols: Ingress or egress policies in map for network policy, empty map by default.
    ...     :param policies: Ingress or egress policies in list for network policy, empty list by default.
    ...     :return: json/map
    [Arguments]         ${type}     ${ports}    ${netpols}=${Empty}     ${policies}=${Empty}
    ${type}=    Convert TO Lowercase    ${type}
    Run Keyword If  '${type}' not in ['ingress', 'egress']  Fail    ${type} is invaild type for network policy.
    ${netpols}=     Run Keyword If  "${netpols}" == "${Empty}"      Create Dictionary
    ...                     ELSE    Set Variable    ${netpols}
    ${policies}=    Run Keyword If  "${policies}" == "${Empty}"     Create List
    ...                     ELSE    Set Variable    ${policies}
    ${netpol}=  Create List
    ${key}=     Set Variable If     '${type}' == 'ingress'  from    to
    ${len}=     Get Length  ${policies}
    ${np}=      Run Keyword If  ${len} == ${0}  Create Dictionary
    ...                 ELSE    Create Dictionary   ${key}=${policies}  ports=${ports}
    ${netpol}=  Add Object To JSON  ${netpol}       $           ${np}
    ${netpols}=     Set Value To JSON   ${netpols}  $.${type}   ${netpol}
    [Return]    ${netpols}
