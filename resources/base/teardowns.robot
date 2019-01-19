*** Settings ***
Library  DateTime
Library  SeleniumLibrary


*** Variables ***


*** Keywords ***
Provided precondition
    ${now}=     Get Current Date
    ${now_stamp}=   Convert Date    ${now}  %Y-%m-%d_%H-%M-%S
    Capture Page Screenshot     ${TEST_NAME}-${now_stamp}.png