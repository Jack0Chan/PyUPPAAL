@echo off

REM Prepare the application (mutant):
copy app\\AppM.java app\\App.java
javac -cp . app\\App.java

REM Prepare and run each test case:
for /f %%testcase in ('dir /b TestCase-*.java') DO (
    echo %%testcase
    copy %%testcase app\\TestCase.java
    javac -cp . app\\TestCase.java
    java -ea -cp . app.TestCase
)
