@echo off

REM Prepare the application (correct):
copy app\\AppC.java app\\App.java
javac -cp . app\\App.java

REM Prepare and run each test case:
for /f %%testcase in ('dir /b TestCase-*.code') DO (
    echo %%testcase
    copy %%testcase app\\TestCase.java
    javac -cp . app\\TestCase.java
    java -ea -cp . app.TestCase
)
