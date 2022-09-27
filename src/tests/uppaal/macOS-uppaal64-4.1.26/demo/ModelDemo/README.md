# UPPAAL Java API Demo

This directory contains a sample Java project code demonstrating the use of `lib/model.jar`.
The source code assumes that this project is inside Uppaal distribution and can find Uppaal files.

The `lib/model.jar` library offers an API to create Uppaal model documents.
The `lib/model-javadoc.jar` includes the Javadoc documentation for this library.
In particular see `com.uppaal.model.core2.Document` class documentation for creating model documents.

The library can also be used to connect to engine (for simulation and verification), but then `uppaal.jar` must be included on class path.
See the documentation for `com.uppaal.engine.Engine` class to connect to Uppaal engine.

Use the following commands to compile and run:

```sh
cd demo/ModelDemo
ant clean jar
cd ../../
java -cp uppaal.jar:lib/model.jar:demo/ModelDemo/dist/ModelDemo.jar ModelDemo hardcoded
```

The run will produce `ModelDemo.xml` model file, a some sample traces `ModelDemo.xtr` and some human freindly messages to standard output.

`ModelDemo` can also read an external model file (use Control+C to stop):

```sh
java -cp uppaal.jar:lib/model.jar:demo/ModelDemo/dist/ModelDemo.jar ModelDemo demo/train-gate.xml
```

Marius Mikucionis
marius@cs.aau.dk
