# Introduction

[![](https://img.shields.io/badge/docs-passing-brightgreen)](https://pyuppaal.readthedocs.io/en/latest/index.html)	[![Licence](https://img.shields.io/github/license/jack0chan/pyuppaal)](https://opensource.org/licenses/mit-license.php)	[![](https://img.shields.io/badge/github-Jack0Chan-blue)](https://github.com/Jack0Chan/pyuppaal)	[![](https://img.shields.io/badge/group-HCPS-blue)](https://www.yuque.com/hcps) 

`pyuppaal` is a research tool that can simulate, verify and modify UPPAAL models with python. With this package, you can do

1. run any UPPAAL commands with multi-process that is valid with verifyta, and return the proof trace (or counter-example).
2. modify a `.xml`  model, including templates, declarations, system declarations, and queries. It has a powerful method `find_all_patterns`  that can get all different untimed traces that can explain current property.
4. (todo) analyze the *SMC* simulation results.

# Quickstart

## Something to prepare

### Installation

To install `pyuppaal`, simply run this simple command:

```
python -m pip install pyuppaal
```

### Get started

Begin by importing the `pyuppaal` module:

```python
import pyuppaal as pyu
# verifyta path is required before any other operations
pyu.set_verifyta_path(r'C:/Users/22215/OneDrive/Software/UPPAAL/bin-Windows/verifyta.exe')
```

## Try some simple verification!

Choose the model file you want to verify, as well as the path you want to save the result, you can complete a simple verifivation:

```python
# Two paths you choose
p1_model_path = 'verifyta_demo1.xml'
p1_trace_path = 'verifyta_demo1_trace.xml'
# The result will be written in the target file, and the procedure information is saved in res1
res1 = pyu.simple_verify(model_path=p1_model_path, trace_path=p1_trace_path)
print(res1)

## OUTPUT:
## [('set UPPAAL_COMPILE_ONLY=&&C:/Users/22215/OneDrive/Software/UPPAAL/bin-Windows/verifyta.exe -t 1 -X verifyta_demo1_trace verifyta_demo1.xml', 'Options for the verification:\n  Generating shortest trace\n  Search order is breadth first\n  Using conservative space optimisation\n  Seed is 1662285315\n  State space representation uses minimal constraint systems\n\x1b[2K\nVerifying formula 1 at /nta/queries/query[1]/formula\n\x1b[2K -- Formula is NOT satisfied.\nXMLTrace outputted to: verifyta_demo1_trace1.xml\n')]
```

## Get timed trace easily

You can also  get a timed trace with the same params:

```python
simtracer = pyu.get_timed_trace(p1_model_path, p1_trace_path,hold=True)
print(simtracer)

## OUTPUT:
## State [0]: ['P2.A']
## global_variables [0]: []
## Clock_constraints [0]: [t(0) - P2.t ≤ 0; P2.t - t(0) ≤ 10; ]
## transitions [0]: None: P2.A -> P2.B
## -----------------------------------
## State [1]: ['P2.B']
## global_variables [1]: []
## Clock_constraints [1]: [t(0) - P2.t ≤ -10; P2.t - t(0) ≤ 10; ]
## transitions [1]: None: P2.B -> P2.C
## -----------------------------------
## State [2]: ['P2.C']
## global_variables [2]: []
## Clock_constraints [2]: [t(0) - P2.t ≤ -10; P2.t - t(0) ≤ 20; ]
```

## Find a pattern

You can quickly find a pattern with plentiful params, e.g., inputs, observations, actions:

```python
model_path = 'pyuppaal_demo_PipeNet.xml'
# input at 0 and 1000
inputs = pyu.TimedActions(actions=['input_ball', 'input_ball'], lb=[0, 1000], ub=[0,1000])
# observe at 500 and 1550
observations = pyu.TimedActions(actions=['exit1', 'exit2'], lb=[500, 1550], ub=[500, 1550])
# concerned actions
hidden_actions = ['hidden_path1', 'hidden_path2', 'hidden_path3', 'hidden_path4', 'hidden_path5', 'hidden_path6']
input_actions = ['input_ball']
observe_actions = ['exit1','exit2','exit3']
focused_actions = list(set(hidden_actions+input_actions+observe_actions))
# find a pattern
pyu.find_a_pattern(inputs, observations, observe_actions=observe_actions, focused_actions=None, hold=False)

## OUTPUT:
## ('E<> Monitor0.pass',
##  ['input_ball',
##   'input_ball',
##   'hidden_path1',
##   'hidden_path3',
##   'exit1',
##   'input_ball',
##   'input_ball',
##   'hidden_path1',
##   'hidden_path4',
##   'exit2'])
```

## Find all patterns

You can also find all patterns:

```python
pyu.find_all_patterns(inputs, observations, observe_actions=observe_actions, hold=False, max_patterns = 2)

## OUTPUT
## [('E<> Monitor0.pass',
##   ['input_ball',
##    'input_ball',
##    'hidden_path1',
##    'hidden_path3',
##    'exit1',
##    'input_ball',
##    'input_ball',
##    'hidden_path1',
##    'hidden_path4',
##    'exit2']),
##  ('E<> Monitor0.pass && !Monitor1.pass',
##   ['input_ball',
##    'input_ball',
##    'hidden_path1',
##    'hidden_path3',
##    'exit1',
##    'input_ball',
##    'input_ball',
##    'hidden_path2',
##    'hidden_path5',
##    'exit2'])]
```

## Generate communication graph

You can easily generate your communication graph to plentiful type, e.g., `.md`, `.png`, `.svg` and `.pdf`:

```python
model_path = r'C:\Users\22215\OneDrive\Coding\Github\pyuppaal\src\tests\Pedestrian.xml'
# just take .png as an example
save_path = r'C:\Users\22215\OneDrive\Coding\Github\pyuppaal\src\tests\Pedestrian.png'
pyu.get_communication_graph(model_path,save_path)
```



