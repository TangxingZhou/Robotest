#!/usr/bin/env bash
# robot --argumentfile runners/Demo/Internal_Chrome.txt
robot --variable BROWSER:Firefox --name Firefox --log none --report none --output out/fx.xml login
robot --variable BROWSER:IE --name IE --log none --report none --output out/ie.xml login
rebot --name Login --outputdir out --output login.xml out/fx.xml out/ie.xml