*** Settings ***
Library     SeleniumLibrary

*** Keywords ***
JS Click Element
    [Arguments]     ${locator}
    ${element}=     Get WebElement  ${locator}
    Execute Javascript  arguments[0].click();   ARGUMENTS   ${element}

Run Keyword on New Window
    [Arguments]     ${kw}   @{args}
    @{handles}=     Get Window Handles
    ${count}=       Get Length  ${handles}
    Return From Keyword If  ${count}==${1}  ${False}
    Select Window   NEW
    Run Keyword And Return  ${kw}   @{args}
    Close Window
    Select Window   @{handles}[${count-2}]
