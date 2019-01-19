*** Settings ***
Documentation    This is a demo suite.

Resource   ../../resources/Demo/keywords/demo_keywords.robot

*** Variables ***


*** Test Cases ***
Demo Test
    [Tags]    Demo
    log  This is a demo test.
