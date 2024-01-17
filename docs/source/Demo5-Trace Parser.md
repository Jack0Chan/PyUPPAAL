# Demo5 - Trace Parser

**Note: we are woking on CAV-2024 tool paper. The documentation will be updated to a structure similar to Demo1-PipeNet before 2024.4.1.**

This demo indicates the usage of pyuppaal.SimTrace.

## 1. Problem Description

Coming soon..

<img src=trace_parser.png width=1200 />

## 2. Code


```python
import pyuppaal
from pyuppaal import UModel

pyuppaal.set_verifyta_path(r"C:\Users\Taco\Documents\GitHub\cav2024\bin\uppaal64-4.1.26\bin-Windows\verifyta.exe")

umodel = UModel('ToyInformation.xml')
trace = umodel.easy_verify()
print(trace)
```

    State [0]: ['input._id7', 'nodeInput._id2', 'path._id0', 'nodeOut._id5', 'Monitor0._id11']
    global_variables [0]: None
    Clock_constraints [0]: [t(0) - gclk ≤ 0; t(0) - nodeInput.t ≤ 0; t(0) - path.t ≤ 0; gclk - nodeInput.t ≤ 0; nodeInput.t - path.t ≤ 0; path.t - t(0) ≤ 0; ]
    transitions [0]: sigIn: input -> nodeInput; input._id7 -> input._id8; nodeInput._id2 -> nodeInput._id4;
    -----------------------------------
    State [1]: ['input._id8', 'nodeInput._id4', 'path._id0', 'nodeOut._id5', 'Monitor0._id11']
    global_variables [1]: None
    Clock_constraints [1]: [t(0) - gclk ≤ 0; t(0) - nodeInput.t ≤ 0; t(0) - path.t ≤ 0; gclk - nodeInput.t ≤ 0; nodeInput.t - path.t ≤ 0; path.t - t(0) ≤ 0; ]
    transitions [1]: actPath: nodeInput -> path; nodeInput._id4 -> nodeInput.Refratory; path._id0 -> path.Conducting;
    -----------------------------------
    State [2]: ['input._id8', 'nodeInput.Refratory', 'path.Conducting', 'nodeOut._id5', 'Monitor0._id11']
    global_variables [2]: None
    Clock_constraints [2]: [t(0) - gclk ≤ 0; t(0) - nodeInput.t ≤ 0; t(0) - path.t ≤ 0; gclk - t(0) ≤ 30; gclk - nodeInput.t ≤ 0; nodeInput.t - path.t ≤ 0; path.t - gclk ≤ 0; ]
    transitions [2]: actNode: path -> nodeOut; path.Conducting -> path._id0; nodeOut._id5 -> nodeOut._id6;
    -----------------------------------
    State [3]: ['input._id8', 'nodeInput.Refratory', 'path._id0', 'nodeOut._id6', 'Monitor0._id11']
    global_variables [3]: None
    Clock_constraints [3]: [t(0) - gclk ≤ 0; t(0) - nodeInput.t ≤ 0; t(0) - path.t ≤ 0; gclk - t(0) ≤ 30; gclk - nodeInput.t ≤ 0; nodeInput.t - path.t ≤ 0; path.t - gclk ≤ 0; ]
    transitions [3]: sigOut: nodeOut -> Monitor0; nodeOut._id6 -> nodeOut._id5; Monitor0._id11 -> Monitor0._id12;
    -----------------------------------
    State [4]: ['input._id8', 'nodeInput.Refratory', 'path._id0', 'nodeOut._id5', 'Monitor0._id12']
    global_variables [4]: None
    Clock_constraints [4]: [t(0) - gclk ≤ -30; t(0) - nodeInput.t ≤ 0; t(0) - path.t ≤ 0; gclk - t(0) ≤ 50; gclk - nodeInput.t ≤ 0; nodeInput.t - path.t ≤ 0; path.t - gclk ≤ 0; ]
    transitions [4]: sigIn: input -> ; input._id8 -> input._id9;
    -----------------------------------
    State [5]: ['input._id9', 'nodeInput.Refratory', 'path._id0', 'nodeOut._id5', 'Monitor0._id12']
    global_variables [5]: None
    Clock_constraints [5]: [t(0) - gclk ≤ -50; t(0) - nodeInput.t ≤ 0; t(0) - path.t ≤ 0; gclk - t(0) ≤ 100; gclk - nodeInput.t ≤ 0; nodeInput.t - path.t ≤ 0; path.t - gclk ≤ 0; ]
    transitions [5]: None: nodeInput -> nodeInput; nodeInput.Refratory -> nodeInput._id2;
    -----------------------------------
    State [6]: ['input._id9', 'nodeInput._id2', 'path._id0', 'nodeOut._id5', 'Monitor0._id12']
    global_variables [6]: None
    Clock_constraints [6]: [t(0) - gclk ≤ -50; t(0) - nodeInput.t ≤ 0; t(0) - path.t ≤ 0; gclk - t(0) ≤ 100; gclk - nodeInput.t ≤ 0; nodeInput.t - path.t ≤ 0; path.t - gclk ≤ 0; ]
    transitions [6]: sigIn: input -> nodeInput; input._id9 -> input.Finish; nodeInput._id2 -> nodeInput._id4;
    -----------------------------------
    State [7]: ['input.Finish', 'nodeInput._id4', 'path._id0', 'nodeOut._id5', 'Monitor0._id12']
    global_variables [7]: None
    Clock_constraints [7]: [t(0) - gclk ≤ -100; t(0) - nodeInput.t ≤ 0; t(0) - path.t ≤ 0; gclk - nodeInput.t ≤ 100; nodeInput.t - path.t ≤ -100; path.t - t(0) ≤ 100; ]
    transitions [7]: actPath: nodeInput -> path; nodeInput._id4 -> nodeInput.Refratory; path._id0 -> path.Conducting;
    -----------------------------------
    State [8]: ['input.Finish', 'nodeInput.Refratory', 'path.Conducting', 'nodeOut._id5', 'Monitor0._id12']
    global_variables [8]: None
    Clock_constraints [8]: [t(0) - gclk ≤ -100; t(0) - nodeInput.t ≤ 0; t(0) - path.t ≤ 0; gclk - t(0) ≤ 130; gclk - nodeInput.t ≤ 100; nodeInput.t - path.t ≤ 0; path.t - gclk ≤ -100; ]
    transitions [8]: actNode: path -> nodeOut; path.Conducting -> path._id0; nodeOut._id5 -> nodeOut._id6;
    -----------------------------------
    State [9]: ['input.Finish', 'nodeInput.Refratory', 'path._id0', 'nodeOut._id6', 'Monitor0._id12']
    global_variables [9]: None
    Clock_constraints [9]: [t(0) - gclk ≤ -100; t(0) - nodeInput.t ≤ 0; t(0) - path.t ≤ 0; gclk - t(0) ≤ 130; gclk - nodeInput.t ≤ 100; nodeInput.t - path.t ≤ 0; path.t - gclk ≤ -100; ]
    transitions [9]: sigOut: nodeOut -> Monitor0; nodeOut._id6 -> nodeOut._id5; Monitor0._id12 -> Monitor0.pass;
    -----------------------------------
    State [10]: ['input.Finish', 'nodeInput.Refratory', 'path._id0', 'nodeOut._id5', 'Monitor0.pass']
    global_variables [10]: None
    Clock_constraints [10]: [t(0) - gclk ≤ -130; t(0) - nodeInput.t ≤ 0; t(0) - path.t ≤ 0; gclk - t(0) ≤ 200; gclk - nodeInput.t ≤ 100; nodeInput.t - path.t ≤ 0; path.t - gclk ≤ -100; ]
    
    

## 1. Path Conduction Info

From the printed trace information above, we can extract path conduction info:

State [2]: ['input._id8', 'nodeInput.Refratory', 'path.Conducting', 'nodeOut._id5', 'Monitor0._id11']

global_variables [2]: None

Clock_constraints [2]: [t(0) - gclk ≤ 0; t(0) - nodeInput.t ≤ 0; <font color="red">t(0) - path.t ≤ 0; gclk - t(0) ≤ 30;</font>  gclk - nodeInput.t ≤ 0; nodeInput.t - path.t ≤ 0; <font color="red">path.t - gclk ≤ 0; </font>]  

transitions [2]: actNode: path -> ['nodeOut']; path.Conducting -> path._id0; nodeOut._id5 -> nodeOut._id6;

<!-- <font color="red">233 </font> -->

We can infer `0 <= path.t <=30` from the red component.

<img src=conduction_1.png width=300 />
<img src=conduction_2.png width=300 />

## 2.Node Refractory Info

State [5]: ['input._id9', 'nodeInput.Refratory', 'path._id0', 'nodeOut._id5', 'Monitor0._id12']
global_variables [5]: None
Clock_constraints [5]: [t(0) - gclk ≤ -50; t(0) - nodeInput.t ≤ 0; t(0) - path.t ≤ 0; gclk - t(0) ≤ 100; gclk - nodeInput.t ≤ 0; nodeInput.t - path.t ≤ 30; path.t - gclk ≤ -30; ]
transitions [5]: None: nodeInput.Refratory -> nodeInput._id2

<img src=refractory_1.png width=300 />
<img src=refractory_2.png width=300 />
