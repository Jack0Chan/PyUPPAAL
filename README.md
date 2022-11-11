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

A [MiniProject_PipeNet](https://github.com/Jack0Chan/pyuppaal/blob/main/src/tests/Doc_MiniProject_PipeNet.ipynb) is provided to help understand how `pauppaal` can contribute to scientific research.

# Quickstart

## Installation
To install `pyuppaal`, simply run this simple command:

`pip install pyuppaal`

## Before Coding

Remember to set the `verifyta_path` in your first line of code.

```python

pyuppaal.set_verifyta_path("your/path/to/verifyta.exe")

```


## Verify a Model, and Get the Verifycation Result

Lets take the following model P1 with query `A[] not deadlock` as the example. You can download this file via [this_link].

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


## Verify Models with Multi-threads


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


## Get Communication Graph

For models with multiple processes, you can use `pyuppaal.get_communication_graph(model_path)` or `umod.get_communication_graph()` method to visualize the sturcture of the model.

An example communication graph of a complex model in [MiniProject_PipeNet](https://github.com/Jack0Chan/pyuppaal/blob/main/src/tests/Doc_MiniProject_PipeNet.ipynb) is shown below:

[![](https://mermaid.ink/img/pako:eNpVjs0KwjAQhF-l7Lk56DEHT714UUGPC7JttjaQpCHdiFL67kYo_pxmmG8GZoZuNAwaboniUF0aDCcb-cCCYR9iLnJsJ053TmuglH3LtSXnlNp92qtRih9WtoV8d39o84OgBs_JkzXlwYyhqhBkYM8IuljDPWUnCBiWUqUs4_kZOtCSMteQoyHhxlL57kH35CZeXq-ESg8?type=png)](https://mermaid.live/edit#pako:eNpVjs0KwjAQhF-l7Lk56DEHT714UUGPC7JttjaQpCHdiFL67kYo_pxmmG8GZoZuNAwaboniUF0aDCcb-cCCYR9iLnJsJ053TmuglH3LtSXnlNp92qtRih9WtoV8d39o84OgBs_JkzXlwYyhqhBkYM8IuljDPWUnCBiWUqUs4_kZOtCSMteQoyHhxlL57kH35CZeXq-ESg8)


