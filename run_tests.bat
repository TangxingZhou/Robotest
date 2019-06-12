@echo off


if "%1" == "--init" (
    python3 -m pip install --user -r requirements.txt
) else (
    python3 -m run_robot %*
)
:: python3 -m run_robot --argumentfile runners/Demo/Internal_Chrome.txt
