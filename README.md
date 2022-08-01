Currently, it is under development. APIs are changing.

# Introduction

pyUPPAAL is a research tool that can simulate, verify and modify UPPAAL models with python. It can also help to analyze counter-examples in .xml format. Note that the implementations are based on verifyta and the built-in xml package.
With this package, you can do

1. run any UPPAAL commands with multi-process that is valid with verifyta.

2. modify a .xml model, including templates, declarations, system declarations, and queries. It has a powerful method find_all_patterns that can get all different untimed traces that can explain current inputs-obs.

3. analyze a counter-example file, and return input-observation-based analysis.

4. analyze the SMC simulation results.

# Quick Start

Please check [tmp doc-yuque](https://www.yuque.com/docs/share/befff524-05cf-4276-be93-e507b65e6c73?).


[Demos](https://github.com/Jack0Chan/pyuppaal/blob/main/src/tests/demo.ipynb)

