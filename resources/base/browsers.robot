*** Settings ***
Library     String
Library     SeleniumLibrary

*** Variables ***
&{Executable}               Chrome=chromedriver     Ie=IEDriverServer.exe   Edge=MicrosoftWebDriver.exe     Firefox=geckodriver
@{Chrome Default Options}   start-maximized     enable-automation   disable-infobars    test-type
&{Chrome Prefs}             download.prompt_for_download=${False}   download.default_directory=${Download Directory}
${Internal Proxy URL}       http://xxx.com
${External Proxy URL}       xxx.com:8080
@{Headless Browsers}        Chrome  Firefox
${Trusted URIS}             .xxx.net,.xxx.com

*** Keywords ***
Init and Start Browser
    [Arguments]     ${browser}
    ${browser}=     Upper First Letter of String    ${browser}
    ${options}=     Run Keyword If  '${browser}'=='Chrome'      Set Chrome Options
    ...     ELSE IF                 '${browser}'=='Ie'          Set IE Options
    ...     ELSE IF                 '${browser}'=='Edge'        Set Edge Options
    ...     ELSE IF                 '${browser}'=='Firefox'     Set Firefox Options
    ...     ELSE                    Fail    ${browser} is not supported currently.
    ${options}=     Set Browser Proxy   ${options}
    ${options}=     Set Headless Mode   ${options}
    Init Webdriver

Set Chrome Options
    ${options}=     Evaluate    sys.modules['selenium.webdriver'].ChromeOptions()   sys, selenium.webdriver
    :FOR    ${option}   IN      @{Chrome Default Options}
    \   Call Method     ${options}  add_argument    ${option}
    ${int_or_ext}=  Get Variable Value  ${IntExt}       INTERNAL
    ${int_or_ext}=  Call Method         ${int_or_ext}   upper
    Call Method     ${options}  set_capability              intExt                  ${int_or_ext}
    Call Method     ${options}  set_capability              acceptInsecureCerts     ${True}
    Call Method     ${options}  add_experimental_option     useAutomationExtension  ${False}
    Call Method     ${options}  add_experimental_option     prefs                   ${Chrome Prefs}
    [Return]    ${options}

Set IE Options
    ${options}=     Evaluate    sys.modules['selenium.webdriver'].InternetExplorerOptions()     sys, selenium.webdriver
    ${options.ignore_protected_mode_settings}=  Set Variable    ${True}
    [Return]    ${options}

Set Edge Options
    ${options}=     Evaluate    sys.modules['selenium.webdriver'].EdgeOptions()     sys, selenium.webdriver
    ${options.page_load_strategy}=  Set Variable    normal
    [Return]    ${options}

Set Firefox Options
    ${options}=     Evaluate    sys.modules['selenium.webdriver'].FirefoxOptions()  sys, selenium.webdriver
    ${profile}=     Evaluate    sys.modules['selenium.webdriver'].FirefoxProfile()  sys, selenium.webdriver
    Call Method     ${profile}  set_preference  network.negotiate-auth.trusted-uris     ${Trusted URIS}
    Call Method     ${profile}  set_preference  network.negotiate-auth.delegation-uris  ${Trusted URIS}
    Call Method     ${profile}  set_preference  plugin.state.flash  0
    ${options.profile}=                 Set Variable    ${profile}
    ${options.accept_insecure_certs}=   Set Variable    ${True}
    [Return]    ${options}

Set Browser Proxy
    [Arguments]     ${options}
    ${browser}=     Get Browser Name From Options       ${options}
    Return From Keyword If  '${browser}'!='Firefox'     ${options}
    ${int_or_ext}=  Get Variable Value  ${IntExt}       INTERNAL
    ${int_or_ext}=  Call Method         ${int_or_ext}   upper
    ${proxy}=           Evaluate    sys.modules['selenium.webdriver'].Proxy()   sys, selenium.webdriver
    ${manual type}=     Evaluate    sys.modules['selenium.webdriver.common.proxy'].ProxyType.MANUAL     sys, selenium.webdriver
    ${proxy.proxy_type}=            Set Variable        ${manual type}
    ${proxy.proxy_autoconfig_url}=  Set Variable If     '${int_or_ext}'=='INTERNAL'     ${Internal Proxy URL}
    ${proxy.http_proxy}=            Set Variable If     '${int_or_ext}'=='EXTERNAL'     ${External Proxy URL}
    ${proxy.ssl_proxy}=             Set Variable If     '${int_or_ext}'=='EXTERNAL'     ${External Proxy URL}
    ${proxy.ftp_proxy}=             Set Variable If     '${int_or_ext}'=='EXTERNAL'     ${External Proxy URL}
    Call Method     ${options}  set_capability  proxy   ${proxy}
    [Return]    ${options}

Set Headless Mode
    [Arguments]     ${options}
    ${headless mode}=   Get Variable Value  ${Headless}     N
    ${browser}=     Get Browser Name From Options       ${options}
    Return From Keyword If  '${headless mode}'=='N'     ${options}
    Run Keyword If  '${browser}' in @{Headless Browsers}    Call Method     ${options}  set_headless
    ...     ELSE    Fail    ${browser} does not supporte headless mode.
    [Return]    ${options}

Init Webdriver
    [Arguments]     ${options}
    ${remote host}=     Get Variable Value  ${RemoteMachine}    ${Empty}
    ${remote port}=     Get Variable Value  ${RemotePort}       ${Empty}
    ${browser}=         Get Browser Name From Options           ${options}
    Run Keyword If  '${remote host}'=='${Empty}' or '${remote port}'=='${Empty}'
    ...             Create Webdriver    ${browser}  options=${options}  #executable_path=${Executable.${browser}}
    ...     ELSE    Create Webdriver    Remote      options=${options}  command_executor=http://${remote host}:${remote port}/wd/hub

Upper First Letter of String
    [Arguments]     ${str}
    ${first}=   Get Substring   ${str}  0   1
    ${left}=    Get Substring   ${str}  1
    ${str}=     Set Variable    ${first.upper()}${left}
    [Return]    ${str}

Get Browser Name From Options
    [Arguments]     ${options}
    ${browser}=     Replace String Using Regexp     ${options.KEY}  (.*:/Options)   ${Empty}
    ${browser}=     Upper First Letter of String    ${browser}
    [Return]    ${browser}

Go To Entry Page
    [Arguments]     ${url}
    Go To   ${url}
    Wait For Condition  return document.readyState == "complete"    30
