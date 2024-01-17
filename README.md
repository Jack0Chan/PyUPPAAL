# Introduction

[![Documentation Status](https://readthedocs.org/projects/pyuppaal/badge/?version=latest)](https://pyuppaal.readthedocs.io/en/latest/?badge=latest)    [![Licence](https://img.shields.io/github/license/jack0chan/pyuppaal)](https://opensource.org/licenses/mit-license.php)    [![](https://img.shields.io/badge/github-Jack0Chan-blue)](https://github.com/Jack0Chan)    [![](https://img.shields.io/badge/group-HCPS-blue)](https://www.yuque.com/hcps)

`pyuppaal` is a research tool that helps you do most things that you can do with UPPAAL GUI. Basic coding flow is:

1. load a .xml model, just like you open a model in UPPAAL GUI;
2. set the query, just like you edit the queries in UPPAAL GUI;
3. verify a model with the query and options (e.g., shortest path), just like you click the "Verify" button in UPPAAL GUI.
4. universal (support Windows, Linux, MacOS).

In addition to the above functions, you can also

- load a `.xtr` trace, and get the formatted trace data as [SimTrace](https://pyuppaal.readthedocs.io/en/latest/USER%20API.html#pyuppaal.tracer.SimTrace);
- modify NTA of UPPAAL xml model, including templates, systems, and queries, etc. ([Example]());
- add built-in templates such as Input, Observer, and other monitors in class [Template](https://pyuppaal.readthedocs.io/en/latest/USER%20API.html#pyuppaal.nta.Template);
- find all patterns of the model with certain query with [find_all_patterns]() method;
- common problem solutions, such as , [fault_identification](), [fault_diagnosability](), and [fault_tolerance]();
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

Lets take the following model P1 with query `A[] not deadlock` as the example. You can download this file via [this_link](https://github.com/Jack0Chan/pyuppaal/blob/main/src/test_integration/demo.xml).

<img src=https://raw.githubusercontent.com/Jack0Chan/pyuppaal/main/src/test_integration/figs/demo.png width=250 />

```python
import pyuppaal as pyu

VERIFYTA_PATH = "uppaal\\uppaal64-4.1.26\\bin-Windows\\verifyta.exe"
# set verifyta path
pyu.set_verifyta_path(VERIFYTA_PATH)

demo_path = 'demo.xml'

# verify and return the terminal result
terminal_res = pyu.Verifyta().verify(demo_path)
print(terminal_res)

# another method
umod = pyu.UModel(demo_path)
umod_res = umod.verify()

assert terminal_res == umod_res
```

```plaintext
['Options for the verification:
  Generating no trace\n  Search order is breadth first
  Using conservative space optimisation
  Seed is 1668171327
  State space representation uses minimal constraint systems
  Verifying formula 1 at /nta/queries/query[1]/formula
  -- Formula is NOT satisfied.']
```

You can also edit the model and get all possible patterns that satisfy the query.

The red line is pattern1, and the green line is pattern2.

<img src=https://raw.githubusercontent.com/Jack0Chan/pyuppaal/main/src/test_integration/figs/demo_patterns.png width=250 />

```python
# save as a new file because find_all_patterns will modify the file
umod = umod.save_as('demo_new.xml')
# set the queries of the xml model.
umod.queries ='E<> P1.pass'

print("broadcast channels: ", umod.broadcast_chan)
print("queries: ", umod.queries)
# get one trace
print('\n', umod.easy_verify())
# find all patterns
all_patterns = umod.find_all_patterns()
for i, pattern in enumerate(all_patterns):
    print(f'pattern{i+1}: ', pattern.untime_pattern)
```

```plaintext
broadcast channels:  ['a', 'd', 'b', 'c']
queries:  ['E<> P1.pass']    State [0]: ['P1.start']
global_variables [0]: None

Clock_constraints [0]: [t(0) - P1.t ≤ 0; P1.t - t(0) ≤ 10; ]transitions [0]: a: P1 -> []; P1.start -> P1._id2;State [1]: ['P1._id2']global_variables [1]: NoneClock_constraints [1]: [t(0) - P1.t ≤ -10; ]transitions [1]: b: P1 -> []; P1._id2 -> P1.pass;-----------------------------------State [2]: ['P1.pass']global_variables [2]: NoneClock_constraints [2]: [t(0) - P1.t ≤ -10; ]  

pattern1:  ['a', 'b']
pattern2:  ['c', 'd']
```

## 4. Verify with Multi-threads

```python
import pyuppaal as pyu
import time
import multiprocessing.dummy as mp

VERIFYTA_PATH = "uppaal\\uppaal64-4.1.26\\bin-Windows\\verifyta.exe"
# set verifyta path
pyu.set_verifyta_path(VERIFYTA_PATH)

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

```plaintext
Verify with for loop, time usage 8.65420126914978
Verify with multi-threads, time usage 1.9333720207214355
```

## 5. Get Communication Graph

For models with multiple processes, you can use  `umod.get_communication_graph()` method to visualize the sturcture of the model.

An example communication graph of a complex model in [MiniProject_PipeNet](https://pyuppaal.readthedocs.io/en/latest/README.html#mini-project-pipenet) is shown below:

[![](https://mermaid.ink/img/pako:eNpVjs0KwjAQhF-l7Lk56DEHT714UUGPC7JttjaQpCHdiFL67kYo_pxmmG8GZoZuNAwaboniUF0aDCcb-cCCYR9iLnJsJ053TmuglH3LtSXnlNp92qtRih9WtoV8d39o84OgBs_JkzXlwYyhqhBkYM8IuljDPWUnCBiWUqUs4_kZOtCSMteQoyHhxlL57kH35CZeXq-ESg8?type=png)](https://mermaid.live/edit#pako:eNpVjs0KwjAQhF-l7Lk56DEHT714UUGPC7JttjaQpCHdiFL67kYo_pxmmG8GZoZuNAwaboniUF0aDCcb-cCCYR9iLnJsJ053TmuglH3LtSXnlNp92qtRih9WtoV8d39o84OgBs_JkzXlwYyhqhBkYM8IuljDPWUnCBiWUqUs4_kZOtCSMteQoyHhxlL57kH35CZeXq-ESg8)

## 6. Other Demos

More functions can be found in the demos below.

1. [Demo - PipeNet (find_all_patterns)](https://pyuppaal.readthedocs.io/en/latest/README.html#demo-pipenet)
2. [Demo - Pedestrian (find_all_patterns)](https://github.com/Jack0Chan/pyuppaal/blob/v1.2)
3. [Demo - Fault Diagnosis (fault_diagnosability, fault_identification)](https://github.com/Jack0Chan/pyuppaal/blob/v1.2)
4. [Demo - Scripted Model Construction (pyuppaal.nta)](https://github.com/Jack0Chan/pyuppaal/blob/v1.2)
5. [Demo - Trace Parser (pyuppaal.SimTrace)](https://github.com/Jack0Chan/pyuppaal/blob/v1.2)
