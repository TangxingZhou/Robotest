*** Settings ***
Documentation    This is a demo suite.
Resource    resources/base/setups.robot

Resource   ../../resources/Demo/keywords/demo_keywords.robot

Suite Setup  Init Suite Variables
*** Variables ***


*** Test Cases ***
Demo Test
    [Tags]    Demo
    log  This is a demo test.
    Init and Start Browser and Go to Entry Page
