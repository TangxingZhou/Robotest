*** Settings ***
Library     libraries.utils.os_ext.OSExt
Library     SSHLibrary

*** Keywords ***
Open Connection And Log In
    [Arguments]         ${host}         ${username}     ${password}
    Open Connection     ${host}
    Login               ${username}     ${password}

Execute Command And Verify Return Code
    [Arguments]         ${command}          ${expected_rc}=${0}
    ${out}  ${rc}=      Execute Command     ${command}              return_rc=True
    Should Be Equal     ${rc}               ${expected_rc}
    [Return]            ${out}

Execute Command On Host
    [Arguments]         ${host}         ${username}     ${password}     ${command}  ${expected_rc}=${0}
    Open Connection And Log In  ${host}     ${username}     ${password}
    ${out}=     Execute Command And Verify Return Code  ${command}  ${expected_rc}
    Close Connection
    [Return]            ${out}

Execute Commands In An Interactive Session
    [Arguments]         @{commands}
    :FOR    ${command}  IN  @{commands}
    \   Write   ${command}
    ${out}=     Read
    [Return]    ${out}

Execute Shell Scripts
    [Arguments]             ${script_file}          ${expected_rc}=${0}
    ${path}     ${file}=    Split Path              ${script_file}
    Put File                ${script_file}          mode=0755
    Start Command           sh ${file}
    ${out}  ${rc}=          Read Command Output     return_rc=True
    Should Be Equal         ${rc}                   ${expected_rc}
    [Return]    ${out}
