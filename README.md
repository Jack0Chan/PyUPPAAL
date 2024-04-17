# Introduction

[![Documentation Status](https://readthedocs.org/projects/pyuppaal/badge/?version=latest)](https://pyuppaal.readthedocs.io/en/latest/?badge=latest) 
[![PyPI version](https://badge.fury.io/py/pyuppaal.svg)](https://badge.fury.io/py/pyuppaal)
![](https://img.shields.io/badge/test-passing-brightgreen)
[![Licence](https://img.shields.io/github/license/jack0chan/pyuppaal)](https://opensource.org/licenses/mit-license.php)
![](https://img.shields.io/badge/platform-Windows,%20Linux,%20Darwin-blue) 

`PyUPPAAL` is a python package developed basically for reflecting UPPAAL's model editing, verification, and counter-example parsing operations into scripts. 

Notice: 

- report issues / requirements at: [github-issues](https://github.com/Jack0Chan/PyUPPAAL/issues).
- more demos for basic & advanced usage will come soon.
- [todo] Support for *SMC* analyzing.

<a href="https://github.com/Jack0Chan/PyUPPAAL/blob/main/src/test_demos/Demo1-PipeNet.ipynb">
    <img src="https://raw.githubusercontent.com/Jack0Chan/pyuppaal/main/src/test_demos/figs/readme1.jpg" width="300px" alt="">
</a>
<a href="https://github.com/Jack0Chan/PyUPPAAL/blob/main/src/test_demos/Demo4-Scripted%20Model%20Construction.ipynb">
    <img src="https://raw.githubusercontent.com/Jack0Chan/pyuppaal/main/src/test_demos/figs/readme2.jpg" width="300px" alt="">
</a>
<a href="https://github.com/Jack0Chan/PyUPPAAL/blob/main/src/test_demos/Demo2-Pedestrian.ipynb">
    <img src="https://raw.githubusercontent.com/Jack0Chan/pyuppaal/main/src/test_demos/figs/readme3.jpg" width="300px" alt="">
</a>
<a href="https://github.com/Jack0Chan/PyUPPAAL/blob/main/src/test_demos/Demo5-Trace%20Parser.ipynb">
    <img src="https://raw.githubusercontent.com/Jack0Chan/pyuppaal/main/src/test_demos/figs/readme4.jpg" width="300px" alt="">
</a>
<a href="https://github.com/Jack0Chan/PyUPPAAL/blob/main/src/test_demos/Demo3-Fault%20Diagnosis.ipynb">
    <img src="https://raw.githubusercontent.com/Jack0Chan/pyuppaal/main/src/test_demos/figs/readme5.jpg" width="300px" alt="">
</a>

# Quickstart

## 1. Installation

`pip install pyuppaal`

## 2. Before Coding

Be sure to set the `verifyta_path` in your first line of code, which serves as model checking engine: [Download UPPAAL4.x/5.x](https://uppaal.org/downloads/).

`pyuppaal.set_verifyta_path("your/path/to//verifyta.exe")`


## 3. Load, Edit, and Verify a Model

1. Firstly we load the model [demo.xml](https://github.com/Jack0Chan/PyUPPAAL/blob/main/src/test_demos/demo.xml) shown below. 
2. Then you can verify, and return the verify results as terminal outputs, or parsed SimTrace.
3. In this demo, we just edit the `queries` of the `.xml` model, and we also provide a demo showing how to edit the template, locations, edges, etc.: [Demo-Scripted Model Construction](https://github.com/Jack0Chan/PyUPPAAL/blob/main/src/test_demos/Demo4-Scripted%20Model%20Construction.ipynb).

<img src=https://raw.githubusercontent.com/Jack0Chan/pyuppaal/main/src/test_demos/figs/demo.png width=250 />


```python
import pyuppaal
from pyuppaal import UModel

print(f"pyuppaal version: {pyuppaal.__version__}\n")
pyuppaal.set_verifyta_path(r"C:\Users\10262\Documents\GitHub\cav2024\bin\uppaal64-4.1.26\bin-Windows\verifyta.exe")

umodel = UModel('demo.xml') # load the model
umodel.queries = ['E<> P1.pass']

# verify and return the terminal result.
print(f"======== terminal res ========\n{umodel.verify()}")

# verify and return the parsed trace as simulation trace: SimTrace.
simulation_trace = umodel.easy_verify() 
print("======== parsed res ========") 
print(f"untime pattern: {simulation_trace.untime_pattern}")
print(f"full trace: {simulation_trace}")
```

## 4. Find all patterns

Now we want find all possible patterns that leads to `P1.pass`. The red line is pattern1, and the green line is pattern2.

<img src=https://raw.githubusercontent.com/Jack0Chan/pyuppaal/main/src/test_demos/figs/demo_patterns.png width=250 />


```python
for i, st in enumerate(umodel.find_all_patterns()):
    print(f'pattern{i+1}: ', st.untime_pattern)
```

## 4. Verify with Multi-threads


```python
import pyuppaal as pyu
import time
import multiprocessing.dummy as mp

print(pyu.__version__)
# set verifyta path
pyu.set_verifyta_path(r"C:\Users\10262\Documents\GitHub\cav2024\bin\uppaal64-4.1.26\bin-Windows\verifyta.exe")

model_path_list = ['demo.xml', 'demo_new.xml'] * 100
trace_path_list = ['demo_trace.xtr', 'demo_new_grace.xtr'] * 100
# for loop
t0 = time.time()
for model, trace in zip(model_path_list, trace_path_list):
    pyu.Verifyta().verify(model_path=model, trace_path=trace)
print(f'Verify with for loop, time usage {time.time() - t0}')

# multi-threads
t0 = time.time()
# pyu.Verifytaeasy_verify(model_path=model_path_list, trace_path=trace_path_list, num_threads=20)
p = mp.Pool()
p.starmap(pyu.Verifyta().verify, zip(model_path_list, trace_path_list))
print(f'Verify with multi-threads, time usage {time.time() - t0}')

```

## 5. Get Communication Graph

For models with multiple processes, you can use `umod.get_communication_graph()` method to visualize the sturcture of your UPPAAL model.

An example communication graph of a complex model in [Demo_PipeNet](https://pyuppaal.readthedocs.io/en/latest/Demo1-PipeNet.html#visualize-the-architecture) is shown below:

[![](https://mermaid.ink/img/pako:eNpVjs0KwjAQhF-l7Lk56DEHT714UUGPC7JttjaQpCHdiFL67kYo_pxmmG8GZoZuNAwaboniUF0aDCcb-cCCYR9iLnJsJ053TmuglH3LtSXnlNp92qtRih9WtoV8d39o84OgBs_JkzXlwYyhqhBkYM8IuljDPWUnCBiWUqUs4_kZOtCSMteQoyHhxlL57kH35CZeXq-ESg8?type=jpg)](https://mermaid.live/edit#pako:eNpVjs0KwjAQhF-l7Lk56DEHT714UUGPC7JttjaQpCHdiFL67kYo_pxmmG8GZoZuNAwaboniUF0aDCcb-cCCYR9iLnJsJ053TmuglH3LtSXnlNp92qtRih9WtoV8d39o84OgBs_JkzXlwYyhqhBkYM8IuljDPWUnCBiWUqUs4_kZOtCSMteQoyHhxlL57kH35CZeXq-ESg8)

## 6. Backup of old docs

Demos are provided to help users get familiar with `PyUPPAAL` (can not be rendered by github):
<div style="display: flex; flex-wrap: wrap; align-items: flex-start;">
    <div style="margin: 10px; width: 300px;">
        <img src="https://raw.githubusercontent.com/Jack0Chan/pyuppaal/main/src/test_demos/figs/pipeNetPatterns.png" style="width: 300px; height: 200px; object-fit: cover;">
        <h5 style="margin: 0 0 4px 0; font-size: 14px;"><a href="https://github.com/Jack0Chan/PyUPPAAL/blob/main/src/test_demos/Demo1-PipeNet.ipynb">Demo-PipeNet</a></h5>
        <p style="margin: 0; font-size: 14px;">This demo demonstrates how to</p>
        <ol style="margin: 0; padding-left: 20px; font-size: 14px;">
            <li>Load and verify a model.</li>
            <li>Model the input & observation sequence.</li>
            <li>Build communication graph.</li>
            <li>Find all patterns.</li>
        </ol>
    </div>
    <div style="margin: 10px; width: 300px;">
        <img src="https://raw.githubusercontent.com/Jack0Chan/pyuppaal/main/src/test_demos/figs/scripted_model_building_receiver.png" style="width: 300px; height: 200px; object-fit: cover;" alt="描述2">
        <h5 style="margin: 0 0 4px 0; font-size: 14px;"><a href="https://github.com/Jack0Chan/PyUPPAAL/blob/main/src/test_demos/Demo4-Scripted%20Model%20Construction.ipynb">Demo-Scripted Model Construction</a></h5>
        <p style="margin: 0; font-size: 14px;">This demo constructs a model solely with PyUPPAAL APIs, including:</p>
        <ol style="margin: 0; padding-left: 20px; font-size: 14px;">
            <li>Construct <code>Template</code> with <code>Edge</code>, <code>Location</code>.</li>
            <li>Set <code>Declarations</code>, <code>Systems</code>, <code>Queries</code>.</li>
            <li>Verify the constructed model.</li>
        </ol>
    </div>
    <div style="margin: 10px; width: 300px;">
        <img src="https://raw.githubusercontent.com/Jack0Chan/pyuppaal/main/src/test_demos/figs/pedestrian_overall.png" style="width: 300px; height: 200px; object-fit: cover;" alt="描述3">
        <h5 style="margin: 0 0 4px 0; font-size: 14px;"><a href="https://github.com/Jack0Chan/PyUPPAAL/blob/main/src/test_demos/Demo2-Pedestrian.ipynb">Demo-Pedestrain</a></h5>
        <p style="margin: 0; font-size: 14px;">This demo shows how to identify all event sequences that could result in a fault state, and see you can get ALL possible patterns only with PyUPPAAL <code>find_all_patterns()</code>.</p>
    </div>
    <div style="margin: 10px; width: 300px;">
        <img src="https://raw.githubusercontent.com/Jack0Chan/pyuppaal/main/src/test_demos/figs/npn_monitors.png" style="width: 300px; height: 200px; object-fit: cover;" alt="描述3">
        <h5 style="margin: 0 0 4px 0; font-size: 14px;"><a href="https://github.com/Jack0Chan/PyUPPAAL/blob/main/src/test_demos/Demo5-Trace%20Parser.ipynb">Demo-Trace Parser</a></h5>
        <p style="margin: 0; font-size: 14px; font-size: 14px;">In this demo, you will learn how to model the <code>input</code> and <code>observations</code> events of a descrete event system (DES), and how to extract information from parsed counter example.</p>
    </div>
    <div style="margin: 10px; width: 300px;">
        <img src="https://raw.githubusercontent.com/Jack0Chan/pyuppaal/main/src/test_demos/figs/diagnosis_identification.png" style="width: 300px; height: 200px; object-fit: cover;" alt="描述3">
        <h5 style="margin: 0 0 4px 0; font-size: 14px;"><a href="https://github.com/Jack0Chan/PyUPPAAL/blob/main/src/test_demos/Demo3-Fault%20Diagnosis.ipynb">Demo-Fault Identification and Diagnosability</a></h5>
        <p style="margin: 0; font-size: 14px;">In this demo, you will analyze the identification and diagnosability of certain fault, wich advanced methods of <code>pyuppaal</code>.</p>
    </div>
</div>
