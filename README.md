This project is based on robotframework which is implemented by python. Also, it utilize SeleniumLibrary to run tests on browsers.
You can visit some references as below:
    http://robotframework.org/robotframework/
    http://robotframework.org/robotframework/RobotFrameworkUserGuide.html
    http://robotframework.org/SeleniumLibrary/SeleniumLibrary.html
    
<br/>

* * *

## Some more features
1. Run tests in parallel
2. Browser Headless Mode
   > **Headless:Y**
3. Run tests with remote selenium server
   > **RemoteMachine:localhost**
   > **RemotePort:4444**
4. Save results into Dashboard Database
   > **ReportToDB:Y**
   
5. Send email reports after runs
   > **SendEmail:Y**
6. Update the Jira execution status that is automated by tests. For this case, you need to add the jira id into the **[Tags]** of tests.
   > **UpdateJira:Y**
7. The tests can be run in Jenkins or TeamCity.

## Install Dependencies
```{r, engine='bash', count_lines}
python -m pip install --user requirements.txt
```
    
<br/>

## Run tests

#### Run in single process
```{r, engine='bash', count_lines}
run_tests
```

#### Run in parallel
```{r, engine='bash', count_lines}
python -m libs.pabot.pabot --verbose --processes 5 --argumentfile runners/project/subproject/Internal_Chrome_Smoke.txt
```
