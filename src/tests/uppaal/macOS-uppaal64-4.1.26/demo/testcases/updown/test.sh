#!/usr/bin/env bash

# Prepare the application (correct):
cp app/AppC.java app/App.java
javac -cp . app/App.java

# Prepare and run each test case:
for testcase in TestCase-*.java
do
    echo "$testcase"
    cp "$testcase" app/TestCase.java
    javac -cp . app/TestCase.java
    java -ea -cp . app.TestCase
done
