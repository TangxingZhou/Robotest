*** Settings ***
Library     String
Library     OperatingSystem
Library     SeleniumLibrary
Resource    browsers.robot
Resource    teardowns.robot

*** Variables ***
${Screenshots Directory}    ${EXECDIR}/out/${Project}/${Sub Project}/snapshots
${Download Directory}       ${EXECDIR}/out/${Project}/${Sub Project}/downloads

*** Keywords ***
Init Suite Variables
    Register Keyword To Run On Failure  Capture Page Screenshot With Timestamp
    Set Suite Variable  ${ENV}  ${ENV.upper()}
    Run Keyword If  '${Project}'=='${None}'         Fail    'Project' variable is not available.
    ...     ELSE                                    Import Variables    ${EXECDIR}/resources/${Project}/variables.py
    Run Keyword If  '${Sub Project}'=='${None}'     Fail    'Project' variable is not available.
    ...     ELSE                                    Set Suite Variable  ${Base URL}     ${${Sub Project}_${ENV}_BASE}
    Create Directory    ${Screenshots Directory}
    Empty Directory     ${Screenshots Directory}
    Create Directory    ${Download Directory}
    Empty Directory     ${Download Directory}
    Set Screenshot Directory    ${Screenshots Directory}

Init and Start Browser and Go to Entry Page
    ${browser}=     Get Variable Value  ${Browser}  Chrome
    Init and Start Browser  ${browser}
    ${url}=         Get Variable Value  ${Base URL}
    Go To Entry Page    ${url}

Add Breakpoint
    Evaluate    pdb.Pdb(stdout=sys.__stdout__).set_trace()  sys, pdb
