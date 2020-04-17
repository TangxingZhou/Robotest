*** Settings ***
Library     uuid
Library     String
Library     Collections
Library     libraries/utils/JSONLib.py
Library     libraries.utils.os_ext.OSExt

*** Keywords ***
kube_requestEvenForUnsuccessfulCode
    [Arguments]     ${kw}   @{args}
    ${result}   ${response}=    Run Keyword And Ignore Error    ${kw}   @{args}
    Return From Keyword If  '${result}' == 'PASS'   ${result}   ${response}
    ${body}=    Get Regexp Matches      ${response}     HTTP response body: (.*)\n  1
    ${body}=    Loads Strings To JSON   ${body[0]}
    [Return]    ${result}   ${body}

kube_checkResourceExists
    [Arguments]     ${kw}   @{args}
    ${result}   ${response}=    kube_requestEvenForUnsuccessfulCode     ${kw}   @{args}
    # 如果返回体的kind为Status，且code=404，则表示不存在
    ${exists}=      Run Keyword If  "${result}" == "FAIL"
    ...                 Set Variable If     '${response["kind"]}' == 'Status' and '${response["code"]}' == '404'    False   True
    ...             ELSE    Set Variable    True
    [Return]    ${exists}

kube_waitForExpectedStatus
    [Arguments]     ${kw}       @{args}
    Wait Until Keyword Succeeds     ${TIME_OUT}     ${TIME_INTERVAL}    ${kw}   @{args}

Generate UUID
    [Arguments]     ${start}=0  ${end}=${None}
    ${id}=  UUID1
    ${id}=  Format String   {}  ${id}
    ${id}=  Get Substring   ${id}   ${start}    ${end}
    [Return]    ${id}
