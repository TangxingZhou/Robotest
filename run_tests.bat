@echo off
:: call robot --argumentfile runners/Demo/Internal_Chrome.txt
call robot --variable BROWSER:Firefox --name Firefox --log none --report none --output out\fx.xml login
call robot --variable BROWSER:IE --name IE --log none --report none --output out\ie.xml login
call rebot --name Login --outputdir out --output login.xml out\fx.xml out\ie.xml