# Introduction

[![Documentation Status](https://readthedocs.org/projects/pyuppaal/badge/?version=latest)](https://pyuppaal.readthedocs.io/en/latest/?badge=latest)    [![Licence](https://img.shields.io/github/license/jack0chan/pyuppaal)](https://opensource.org/licenses/mit-license.php)    [![](https://img.shields.io/badge/github-Jack0Chan-blue)](https://github.com/Jack0Chan)    [![](https://img.shields.io/badge/group-HCPS-blue)](https://www.yuque.com/hcps) 

`pyuppaal` is a research tool that helps you do most things that you can do with UPPAAL GUI. Basic coding flow is:

1. load a .xml model, just like you open a model in UPPAAL GUI;
2. set the query, just like you edit the queries in UPPAAL GUI;
3. verify a model with the query and options (e.g., shortest path), just like you click the "Verify" button in UPPAAL GUI.

In addition to the above functions, you can also

- load a .xtr trace, and get the formatted trace data;
- modify templates, declaration and systems;
- add built-in templates such as Input, Observer, and Monitors; 
- find all patterns of the model with certain query.
- [todo] analyze the *SMC* simulation results. 

A [MiniProject_PipeNet](https://pyuppaal.readthedocs.io/en/latest/README.html#mini-project-pipenet) is provided to help understand how `pyppaal` can contribute to scientific research.

# Quickstart

## 1. Installation

`pip install pyuppaal`

## 2. Before Coding

Remember to set the `verifyta_path` in your first line of code.

```python

pyuppaal.set_verifyta_path("your/path/to/verifyta.exe")

```


## 3. Verify a Model

Lets take the following model P1 with query `A[] not deadlock` as the example. You can download this file via [this_link](https://github.com/Jack0Chan/pyuppaal/blob/main/src/tests/demo.xml).

<img src=https://raw.githubusercontent.com/Jack0Chan/pyuppaal/main/src/tests/figs/demo.png width=250 />


```python
import pyuppaal as pyu

VERIFYTA_PATH = "uppaal\\Win_Linux-uppaal64-4.1.26\\bin-Windows\\verifyta.exe"
# set verifyta path
pyu.set_verifyta_path(VERIFYTA_PATH)

demo_path = 'demo.xml'

# verify and return the terminal result
terminal_res = pyu.verify(demo_path)
print(terminal_res)

# another method
umod = pyu.UModel(demo_path)
assert terminal_res[0] == umod.verify()
```

    ['Options for the verification:\n  Generating no trace\n  Search order is breadth first\n  Using conservative space optimisation\n  Seed is 1668171327\n  State space representation uses minimal constraint systems\n\x1b[2K\nVerifying formula 1 at /nta/queries/query[1]/formula\n\x1b[2K -- Formula is NOT satisfied.\n']


You can also edit the model and get all possible patterns that satisfy the query.

The red line is pattern1, and the green line is pattern2.

<img src=https://raw.githubusercontent.com/Jack0Chan/pyuppaal/main/src/tests/figs/demo_patterns.png width=250 />


```python
# save as a new file because find_all_patterns will modify the file
umod = umod.save_as('demo_new.xml')
# set the queries of the xml model.
umod.set_queries('E<> P1.pass')

print("broadcast channels: ", umod.broadcast_chan)
print("queries: ", umod.queries)
# get one trace
print('\n', umod.easy_verify())
# find all patterns
all_patterns = umod.find_all_patterns()
for i, pattern in enumerate(all_patterns):
    print(f'pattern{i+1}: ', pattern.untime_pattern)
```

    broadcast channels:  ['a', 'd', 'b', 'c']
    queries:  ['E<> P1.pass']
    
     State [0]: ['P1.start']
    global_variables [0]: None
    Clock_constraints [0]: [t(0) - P1.t ≤ 0; P1.t - t(0) ≤ 10; ]
    transitions [0]: a: P1 -> []; P1.start -> P1._id2; 
    -----------------------------------
    State [1]: ['P1._id2']
    global_variables [1]: None
    Clock_constraints [1]: [t(0) - P1.t ≤ -10; ]
    transitions [1]: b: P1 -> []; P1._id2 -> P1.pass; 
    -----------------------------------
    State [2]: ['P1.pass']
    global_variables [2]: None
    Clock_constraints [2]: [t(0) - P1.t ≤ -10; ]
    
    pattern1:  ['a', 'b']
    pattern2:  ['c', 'd']


## 4. Verify with Multi-threads


```python
import pyuppaal as pyu
import time

# set verifyta path
pyu.set_verifyta_path(VERIFYTA_PATH)

model_path_list = ['demo.xml', 'demo_new.xml'] * 100
trace_path_list = ['demo_trace.xtr', 'demo_new_grace.xtr'] * 100
# for loop
t0 = time.time()
for model, trace in zip(model_path_list, trace_path_list):
    pyu.easy_verify(model_path=model, trace_path=trace)
print(f'Verify with for loop, time usage {time.time() - t0}')

# multi-threads
t0 = time.time()
pyu.easy_verify(model_path=model_path_list, trace_path=trace_path_list, num_threads=20)
print(f'Verify with multi-threads, time usage {time.time() - t0}')
```

    Verify with for loop, time usage 8.65420126914978
    Verify with multi-threads, time usage 1.9333720207214355


## 5. Get Communication Graph

For models with multiple processes, you can use `pyuppaal.get_communication_graph(model_path)` or `umod.get_communication_graph()` method to visualize the sturcture of the model.

An example communication graph of a complex model in [MiniProject_PipeNet](https://pyuppaal.readthedocs.io/en/latest/README.html#mini-project-pipenet) is shown below:

[![](https://mermaid.ink/img/pako:eNpVjs0KwjAQhF-l7Lk56DEHT714UUGPC7JttjaQpCHdiFL67kYo_pxmmG8GZoZuNAwaboniUF0aDCcb-cCCYR9iLnJsJ053TmuglH3LtSXnlNp92qtRih9WtoV8d39o84OgBs_JkzXlwYyhqhBkYM8IuljDPWUnCBiWUqUs4_kZOtCSMteQoyHhxlL57kH35CZeXq-ESg8?type=png)](https://mermaid.live/edit#pako:eNpVjs0KwjAQhF-l7Lk56DEHT714UUGPC7JttjaQpCHdiFL67kYo_pxmmG8GZoZuNAwaboniUF0aDCcb-cCCYR9iLnJsJ053TmuglH3LtSXnlNp92qtRih9WtoV8d39o84OgBs_JkzXlwYyhqhBkYM8IuljDPWUnCBiWUqUs4_kZOtCSMteQoyHhxlL57kH35CZeXq-ESg8)


# Mini Project - PipeNet

We will use [demo_PipeNet.xml](https://github.com/Jack0Chan/pyuppaal/blob/main/src/tests/demo_PipeNet.xml) as an example to help understand how `pauppaal` can contribute to scientific research **partially observable** system.

### 1. Problem Description

There is a pipe-net that has invisible paths between the `Entry` and three different `Exits`. One day, two balls are put into the `Entry` at the global time (gclk) 0 and 1000, and are observed from `Exit1` and `Exit2` at the global time 500 and 1550. 

You want to know what happends to the balls -- all possible paths that can lead to such a input-observation.

### 2. Modeling the PipeNet

We have modeled the PipeNet with UPPAAL, you can download via [this link](https://github.com/Jack0Chan/pyuppaal/blob/main/src/tests/demo_PipeNet.xml).

As shown in the figure below, the guard on the edge is the falling time for each path, e.g., if a ball goes through `hidden_path1`, it will take `200` to `300` seconds.

<img src=https://raw.githubusercontent.com/Jack0Chan/pyuppaal/main/src/tests/figs/pipeNetModel.png width=400 />

### 3. Load the Model and Set Inputs & Observations

Now we will 
1. add an `Input` template that puts the balls into the `Entry` at `gclk==0` and `gclk==1000`.
2. add an `Observer` template that indicates the observations from `Exit1` at `gclk==500`, and `Exit2` at `gclk==1550`.
3. Get one possible pattern that simulates the inputs & observations.

In pyuppaal, inputs & observations are described by `TimedActions`, which is a class with three lists:
1. `actions: List[str]`, 
2. `lower bounds: List[int]`, suggesting the guard and 
3. `upper bounds: List[int]`, suggesting the invariant.


```python
import pyuppaal as pyu
# set verifyta path
VERIFYTA_PATH = "uppaal\\Win_Linux-uppaal64-4.1.26\\bin-Windows\\verifyta.exe"
pyu.set_verifyta_path(VERIFYTA_PATH)

# Load the `xml` model
pipeNet = pyu.UModel("demo_PipeNet.xml")
# save as a new file in order not to overwrite current file
pipeNet = pipeNet.save_as("demo_PipeNet_new.xml")

# Define the input.
inputs = pyu.TimedActions(actions=['input_ball', 'input_ball'], lb=[0, 1000], ub=[0, 1000])
# Define the observation.
observations = pyu.TimedActions(actions=['exit1', 'exit2'], lb=[500, 1550], ub=[500, 1550])
# Add input template.
pipeNet.add_input_template(inputs)
# Add observation template.
pipeNet.add_observer_template(observations)

# Query whether the model can simulate the inputs & observations
pipeNet.set_queries('E<> Observer.pass')
# Get one possible trace.
trace = pipeNet.easy_verify()
print("pattern:", trace.untime_pattern)
# Too long to show. Run it by yourself :)
# print("trace:", trace)
```

    pattern: ['input_ball', 'hidden_path1', 'hidden_path3', 'exit1', 'input_ball', 'hidden_path1', 'hidden_path4', 'exit2']

The `Input` and `Observation` template created by `pyuppaal`. The cache file `*_pattern.xml` can be found in the same directory of the input model.
<br><br>
<img src=https://raw.githubusercontent.com/Jack0Chan/pyuppaal/main/src/tests/figs/pipeNetInput.png width=300 />
<img src=https://raw.githubusercontent.com/Jack0Chan/pyuppaal/main/src/tests/figs/pipeNetObserver.png width=350 />
<img src=https://raw.githubusercontent.com/Jack0Chan/pyuppaal/main/src/tests/figs/pipeNetModel.png width=350 />
<br><br>
In this example, we know the exact time of the inputs & observations, and thus `lower_bounds == upper_bounds`. If you are not sure about the exact time, or you just want to add uncertainty, e.g., the first ball goes from `Exit1` at gclk $\in$ [490, 510], you can just set the lower bound to 490, and the upper bound to 510.

### 4. Visualize the Architecture

You can visualize the architecture by getting the communication graph in [mermaid](https://mermaid.live/) format. 

[![](https://mermaid.ink/img/pako:eNpVjs0KwjAQhF-l7Lk56DEHT714UUGPC7JttjaQpCHdiFL67kYo_pxmmG8GZoZuNAwaboniUF0aDCcb-cCCYR9iLnJsJ053TmuglH3LtSXnlNp92qtRih9WtoV8d39o84OgBs_JkzXlwYyhqhBkYM8IuljDPWUnCBiWUqUs4_kZOtCSMteQoyHhxlL57kH35CZeXq-ESg8?type=png)](https://mermaid.live/edit#pako:eNpVjs0KwjAQhF-l7Lk56DEHT714UUGPC7JttjaQpCHdiFL67kYo_pxmmG8GZoZuNAwaboniUF0aDCcb-cCCYR9iLnJsJ053TmuglH3LtSXnlNp92qtRih9WtoV8d39o84OgBs_JkzXlwYyhqhBkYM8IuljDPWUnCBiWUqUs4_kZOtCSMteQoyHhxlL57kH35CZeXq-ESg8)


```python
# visualize via https://mermaid.live/
cg = pipeNet.get_communication_graph(is_beautify=False)
print(cg)
```

    ```mermaid
    graph TD
    PipeNet
    Input
    Observer
    Input--input_ball-->PipeNet
    PipeNet--exit2-->Observer
    PipeNet--exit1-->Observer```




### 5. Find all patterns

You can get all possible patterns by the following code, and all possible patterns are shown in the figure below. 

1. The first observation at `Exit1` is suggested by the red line. 
2. The second observation at `Exit2` is suggested by 2 the green and yellow line, meaning there are two possible patterns for this observation.
   

<img src=https://raw.githubusercontent.com/Jack0Chan/pyuppaal/main/src/tests/figs/pipeNetPatterns.png width=300 />


```python
# Find all possible traces.
traces = pipeNet.find_all_patterns()
# print patterns.
for i, trace in enumerate(traces):
    print(f'pattern{i+1}', trace.untime_pattern)
```

    pattern1 ['input_ball', 'hidden_path1', 'hidden_path3', 'exit1', 'input_ball', 'hidden_path1', 'hidden_path4', 'exit2']
    pattern2 ['input_ball', 'hidden_path1', 'hidden_path3', 'exit1', 'input_ball', 'hidden_path2', 'hidden_path5', 'exit2']


While extracting all patterns, pyuppaal constructs Monitors based on historical patterns. The figure below shows one of the monitors constructed by pyuppaal. You can get more details from the cache file `*_pattern.xml` that is in the same directory of the input model.

<img src=https://raw.githubusercontent.com/Jack0Chan/pyuppaal/main/src/tests/figs/pipeNetMonitor1.png width=100% />

## Full Code


```python
import pyuppaal as pyu
# set verifyta path
VERIFYTA_PATH = "uppaal\\Win_Linux-uppaal64-4.1.26\\bin-Windows\\verifyta.exe"
pyu.set_verifyta_path(VERIFYTA_PATH)

# Load the `xml` model
pipeNet = pyu.UModel("demo_PipeNet.xml")
# save as a new file in order not to overwrite current file
pipeNet = pipeNet.save_as("demo_PipeNet_new.xml")

# Define the input.
inputs = pyu.TimedActions(actions=['input_ball', 'input_ball'], lb=[0, 1000], ub=[0, 1000])
# Define the observation.
observations = pyu.TimedActions(actions=['exit1', 'exit2'], lb=[500, 1550], ub=[500, 1550])
# Add input template.
pipeNet.add_input_template(inputs)
# Add observation template.
pipeNet.add_observer_template(observations)

# Query whether the model can simulate the inputs & observations
pipeNet.set_queries('E<> Observer.pass')
# Get one possible trace.
trace = pipeNet.easy_verify()
print("pattern:", trace.untime_pattern)
# Too long to show. Run it by yourself :)
# print("trace:", trace)

# visualize via https://mermaid.live/
cg = pipeNet.get_communication_graph(is_beautify=False)
print(cg)

# Find all possible traces.
traces = pipeNet.find_all_patterns()
# print patterns.
for i, trace in enumerate(traces):
    print(f'pattern{i+1}', trace.untime_pattern)
```

    pattern: ['input_ball', 'hidden_path1', 'hidden_path3', 'exit1', 'input_ball', 'hidden_path1', 'hidden_path4', 'exit2']
    ```mermaid
    graph TD
    PipeNet
    Input
    Observer
    Input--input_ball-->PipeNet
    PipeNet--exit2-->Observer
    PipeNet--exit1-->Observer```
    pattern1 ['input_ball', 'hidden_path1', 'hidden_path3', 'exit1', 'input_ball', 'hidden_path1', 'hidden_path4', 'exit2']
    pattern2 ['input_ball', 'hidden_path1', 'hidden_path3', 'exit1', 'input_ball', 'hidden_path2', 'hidden_path5', 'exit2']```

