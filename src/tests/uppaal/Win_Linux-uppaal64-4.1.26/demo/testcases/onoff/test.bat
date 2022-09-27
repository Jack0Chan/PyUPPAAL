@echo off

copy app\\AppC.java app\\App.java
javac -cp . app\\App.java
for /f %%i in ('dir /b *.code') DO (
  echo %%i
  copy %%i app\\Test.java
  javac -cp . app\\Test.java
  java -ea -cp . app.Test
)