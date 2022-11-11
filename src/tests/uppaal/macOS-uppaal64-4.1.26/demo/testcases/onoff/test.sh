#/usr/bin/bash

cp app/AppC.java app/App.java
javac -cp . app/App.java
for i in testcase*.code 
do
  echo $i
  cp $i app/Test.java
  javac -cp . app/Test.java
  java -ea -cp . app.Test
done

