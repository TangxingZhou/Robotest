*** Settings ***
Library  DateTime
Library  SeleniumLibrary

*** Keywords ***
Capture Page Screenshot With Timestamp
    ${now stamp}=   Get Current Timestamp
    Capture Page Screenshot     ${SUITE NAME}_${TEST NAME}_${now stamp}.png

Capture Element Screenshot With Timestamp
    [Arguments]     ${locator}
    ${now stamp}=   Get Current Timestamp
    Scroll Element Into View    ${locator}
    Capture Element Screenshot  ${locator}  ${SUITE NAME}_${TEST NAME}_${now stamp}.png

Get Current Timestamp
    [Arguments]     ${format}=%Y-%m-%d_%H-%M-%S
    ${now}=     Get Current Date
    ${now stamp}=   Convert Date    ${now}  ${format}
    [Return]    ${now stamp}
