<font color='red'>NOTICE:</font>
We are implementing **basic editor** that can help to edit xml with `Declarations`, `Systems`, `Templates(Locations, Edges, Nails, BranchPoints)`, `Queries`, etc., which will come soon in later 2023 with support of UPPAAL 5.0.0. Currently these functions are developed and under test. Note that we are working hard on making an easy, concept-clear uppaal tool with python, the code below is not the final api.
<details><summary>Click Me to Preview the Code</summary>
<p>

```python
def test_construct_model():
    model_path = bring_to_root('constructed_model.xml')
    os.remove(model_path)
    umodel = pyuppaal.UModel.new(model_path)

    umodel.declaration = """// Place global declarations here.
broadcast chan a, b, c;
int count = 0;
int sender_count = 0;
const int rec_end = 10;\n"""
    
# region: 构建tempaltes，一共两个
    # region: 构建第1个template
    template0 = Template(name = "Receiver",
                locations=[], 
                init_ref=0,
                edges=[],
                params="broadcast chan &param1, broadcast chan &param2, int inv_start, int guard_start",
                declaration="""// Place local declarations here.\nclock t;""")
    # 构造locations
    # l0 是initial location
    l0 = Location(location_id=0,location_pos=(-391,-102),
                name = "Start", name_pos=(-401,-136),
                invariant="t<=inv_start", invariant_pos=(-401,-85),
                test_code_on_enter="count ++;", test_code_on_exit="count = 10;", 
                is_initial=True)
    l1 = Location(location_id=1, location_pos=(-178,-102),
                invariant="t<=200", invariant_pos=(-188,-85),
                rate_of_exponential=0.8, rate_of_exp_pos=(-187,-93))
    l2 = Location(location_id=2, location_pos=(-42,-93),is_urgent=True)
    l3 = Location(location_id=3, location_pos=(-76,-212),is_committed=True)
    l4 = Location(location_id=4, location_pos=(25,-212),
                 name = "End1", name_pos=(15,-246))
    l5 = Location(location_id=5, location_pos=(34,-93),
                name = "End2", name_pos=(24,-127),
                comments="备注End2", comments_pos=(25,-34))
    
    # 构造branch points
    bp0 = Location(location_id= 6, location_pos=(-119, -144), is_branchpoint=True)
    
    template0.locations = [l0, l1, l2, l3, l4, l5, bp0]
    
    # 构造edges
    e0 = Edge(source_location_id=2,source_location_pos=(-42,-93),
             target_location_id=5,target_location_pos=(34,-93),
             sync="param2?",sync_pos=(-24,-110),
             update="t=888",update_pos=(-24,-93))
    e1 = Edge(source_location_id=3,source_location_pos=(-76,-212),
             target_location_id=4,target_location_pos=(25,-212),
             sync="param1?",sync_pos=(-58,-229),
             update="t=999",update_pos=(-51,-212))
    e2 = Edge(source_location_id=6,source_location_pos=(-119,-144),
             target_location_id=3,target_location_pos=(-76,-212),
             probability_weight=0.2,prob_weight_pos=(-93,-178))
    e3 = Edge(source_location_id=6,source_location_pos=(-119,-144),
             target_location_id=2,target_location_pos=(-42,-93),
             probability_weight=0.8,prob_weight_pos=(-93,-119))
    e4 = Edge(source_location_id=1,source_location_pos=(-178,-102),
             target_location_id=6,target_location_pos=(-119,-144))
    e5 = Edge(source_location_id=0,source_location_pos=(-391,-102),
             target_location_id=1,target_location_pos=(-178,-102),
             guard="t>= guard_start",guard_pos=(-331,-102),
             update="count ++",update_pos=(-306,-85),
             test_code="count == -1;")
    template0.edges = [e0, e1, e2, e3, e4, e5]
    # template0.branch_points = [bp0]
    # endregion
    
    # region: 构建第2个template
    template1 = Template(name="Sender",
                        locations=[],
                        init_ref=7,
                        edges=[],
                        params="broadcast chan &param1, broadcast chan &param2",
                        declaration=None)
    
    # 构造locations
    l7 = Location(location_id=7, location_pos=(-459,-34),
            name = "Start", name_pos=(-493,-68),
            test_code_on_enter="sender_count = 10;",
            test_code_on_exit="sender_count = -1;",
            comments="""Start:\nTestCode""", comments_pos=(-469,25),
            is_initial=True)
    l8 = Location(location_id=8,location_pos=(-187,-102))
    l9 = Location(location_id=9,location_pos=(-178,17))
    # l10 = Location(location_id=10,location_pos=(-323,-34))
    
    # 构造branch points
    bp1 = Location(location_id=10, location_pos=(-323, -34), is_branchpoint=True)
    
    template1.locations = [l7, l8, l9, bp1]
    
    # 构造edges
    e6 = Edge(source_location_id=10,source_location_pos=(-323,-34),
            target_location_id=9,target_location_pos=(-178,17),
            sync="param2!", sync_pos=(-305,-34))
    e7 = Edge(source_location_id=10,source_location_pos=(-323,-34),
            target_location_id=8,target_location_pos=(-187,-102),
            sync="param1!", sync_pos=(-305,-80),
            probability_weight=0.8, prob_weight_pos=(-305,-51))
    e8 = Edge(source_location_id=7,source_location_pos=(-459,-34),
            target_location_id=10,target_location_pos=(-323,-34),
            nails=[(-382,-136)])
    template1.edges = [e6, e7, e8]
    # print(template1.edges)

    # template1.branch_points = [bp1]
    # endregion        
# endregion 构造templates
                     
    umodel.templates = [template0, template1]
    umodel.system = """// Place template instantiations here.
rec = Receiver(a, b, 10, rec_end);
sender = Sender(a, b);
// List one or more processes to be composed into a system.
system rec, sender;\n"""
    umodel.queries = ["E<> sender_count == 10",
                      "E<> count == 1",
                      "E<> rec.End1",
                      "E<> rec.t >= 10",
                      "A[] not deadlock"]
    
    assert "E<> sender_count == 10" == umodel.queries[0]
    
    # assert umodel.xml == pyuppaal.UModel(bring_to_root("test_umodel_build.xml")).xml
    target_model = pyuppaal.UModel(bring_to_root("test_umodel_build.xml"))
    assert umodel.queries == target_model.queries
    assert umodel.system == target_model.system
    assert umodel.declaration == target_model.declaration
    assert umodel.templates[0].xml == target_model.templates[0].xml
    assert umodel.templates[1].xml == target_model.templates[1].xml
    assert umodel.xml == target_model.xml
    assert "Verifying formula" in umodel.verify()
```

</p>
</details>

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

<img src=https://raw.githubusercontent.com/Jack0Chan/pyuppaal/main/src/test_integration/figs/demo.png width=250 />


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

<img src=https://raw.githubusercontent.com/Jack0Chan/pyuppaal/main/src/test_integration/figs/demo_patterns.png width=250 />


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

<img src=https://raw.githubusercontent.com/Jack0Chan/pyuppaal/main/src/test_integration/figs/pipeNetModel.png width=400 />

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
VERIFYTA_PATH = "C:\\Users\\T1\\Documents\\GitHub\\mcvsfd\\Win_Linux-uppaal64-4.1.26\\bin-Windows\\verifyta.exe"
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

# Focused Actions is xxxxxxxxx(if this comment is not completed, please report the issue :>, thanks)
fc = ['exit1', 'exit2', 'exit3']
# Add observation template.
pipeNet.add_observer_template(observations, focused_actions=fc)

# Query whether the model can simulate the inputs & observations
pipeNet.queries = 'E<> Observer.pass'
# Get one possible trace.
trace = pipeNet.easy_verify()
print("pattern:", trace.untime_pattern)
print("trace:", trace)
```

    pattern: ['input_ball', 'hidden_path1', 'hidden_path3', 'exit1', 'input_ball', 'hidden_path1', 'hidden_path4', 'exit2']
    trace: State [0]: ['PipeNet.Idle', 'Input._id8', 'Observer._id11']
    global_variables [0]: None
    Clock_constraints [0]: [t(0) - gclk ≤ 0; t(0) - PipeNet.t ≤ 0; t(0) - Input.input_clk ≤ 0; t(0) - Observer.input_clk ≤ 0; gclk - PipeNet.t ≤ 0; PipeNet.t - Input.input_clk ≤ 0; Input.input_clk - Observer.input_clk ≤ 0; Observer.input_clk - t(0) ≤ 0; ]
    transitions [0]: input_ball: Input -> ['PipeNet']; Input._id8 -> Input._id9; PipeNet.Idle -> PipeNet.Cross1; 
    -----------------------------------
    State [1]: ['PipeNet.Cross1', 'Input._id9', 'Observer._id11']
    global_variables [1]: None
    Clock_constraints [1]: [t(0) - gclk ≤ 0; t(0) - PipeNet.t ≤ 0; t(0) - Input.input_clk ≤ 0; t(0) - Observer.input_clk ≤ 0; gclk - t(0) ≤ 500; gclk - PipeNet.t ≤ 0; PipeNet.t - Input.input_clk ≤ 0; Input.input_clk - Observer.input_clk ≤ 0; Observer.input_clk - gclk ≤ 0; ]
    transitions [1]: hidden_path1: PipeNet -> []; PipeNet.Cross1 -> PipeNet.Cross2; 
    -----------------------------------
    State [2]: ['PipeNet.Cross2', 'Input._id9', 'Observer._id11']
    global_variables [2]: None
    Clock_constraints [2]: [t(0) - gclk ≤ 0; t(0) - PipeNet.t ≤ 0; t(0) - Input.input_clk ≤ 0; t(0) - Observer.input_clk ≤ 0; gclk - t(0) ≤ 500; gclk - PipeNet.t ≤ 300; gclk - Input.input_clk ≤ 0; PipeNet.t - gclk ≤ -200; Input.input_clk - Observer.input_clk ≤ 0; Observer.input_clk - gclk ≤ 0; ]
    transitions [2]: hidden_path3: PipeNet -> []; PipeNet.Cross2 -> PipeNet.Exit1; 
    -----------------------------------
    State [3]: ['PipeNet.Exit1', 'Input._id9', 'Observer._id11']
    global_variables [3]: None
    Clock_constraints [3]: [t(0) - gclk ≤ 0; t(0) - PipeNet.t ≤ -200; t(0) - Input.input_clk ≤ 0; t(0) - Observer.input_clk ≤ 0; gclk - t(0) ≤ 500; gclk - Input.input_clk ≤ 0; PipeNet.t - gclk ≤ -200; Input.input_clk - Observer.input_clk ≤ 0; Observer.input_clk - gclk ≤ 0; ]
    transitions [3]: exit1: PipeNet -> ['Observer']; PipeNet.Exit1 -> PipeNet.Reset; Observer._id11 -> Observer._id12; 
    -----------------------------------
    State [4]: ['PipeNet.Reset', 'Input._id9', 'Observer._id12']
    global_variables [4]: None
    Clock_constraints [4]: [t(0) - gclk ≤ -500; t(0) - PipeNet.t ≤ -200; t(0) - Input.input_clk ≤ 0; t(0) - Observer.input_clk ≤ 0; gclk - Input.input_clk ≤ 0; PipeNet.t - t(0) ≤ 300; Input.input_clk - Observer.input_clk ≤ 0; Observer.input_clk - t(0) ≤ 500; ]
    transitions [4]: None: PipeNet.Reset -> PipeNet.Idle
    -----------------------------------
    State [5]: ['PipeNet.Idle', 'Input._id9', 'Observer._id12']
    global_variables [5]: None
    Clock_constraints [5]: [t(0) - gclk ≤ -500; t(0) - PipeNet.t ≤ 0; t(0) - Input.input_clk ≤ 0; t(0) - Observer.input_clk ≤ 0; gclk - t(0) ≤ 1000; gclk - PipeNet.t ≤ 300; gclk - Input.input_clk ≤ 0; PipeNet.t - gclk ≤ -200; Input.input_clk - Observer.input_clk ≤ 0; Observer.input_clk - gclk ≤ 0; ]
    transitions [5]: input_ball: Input -> ['PipeNet']; Input._id9 -> Input.pass; PipeNet.Idle -> PipeNet.Cross1; 
    -----------------------------------
    State [6]: ['PipeNet.Cross1', 'Input.pass', 'Observer._id12']
    global_variables [6]: None
    Clock_constraints [6]: [t(0) - gclk ≤ -1000; t(0) - PipeNet.t ≤ 0; t(0) - Input.input_clk ≤ 0; t(0) - Observer.input_clk ≤ 0; gclk - t(0) ≤ 1550; gclk - PipeNet.t ≤ 1000; PipeNet.t - Input.input_clk ≤ -1000; Input.input_clk - Observer.input_clk ≤ 0; Observer.input_clk - gclk ≤ 0; ]
    transitions [6]: hidden_path1: PipeNet -> []; PipeNet.Cross1 -> PipeNet.Cross2; 
    -----------------------------------
    State [7]: ['PipeNet.Cross2', 'Input.pass', 'Observer._id12']
    global_variables [7]: None
    Clock_constraints [7]: [t(0) - gclk ≤ 0; t(0) - PipeNet.t ≤ 0; t(0) - Input.input_clk ≤ 0; t(0) - Observer.input_clk ≤ 0; gclk - t(0) ≤ 1550; gclk - PipeNet.t ≤ 1300; gclk - Input.input_clk ≤ 0; PipeNet.t - gclk ≤ -1200; Input.input_clk - Observer.input_clk ≤ 0; Observer.input_clk - gclk ≤ 0; ]
    transitions [7]: hidden_path4: PipeNet -> []; PipeNet.Cross2 -> PipeNet.Exit2; 
    -----------------------------------
    State [8]: ['PipeNet.Exit2', 'Input.pass', 'Observer._id12']
    global_variables [8]: None
    Clock_constraints [8]: [t(0) - gclk ≤ 0; t(0) - PipeNet.t ≤ -200; t(0) - Input.input_clk ≤ 0; t(0) - Observer.input_clk ≤ 0; gclk - t(0) ≤ 1550; gclk - PipeNet.t ≤ 1300; gclk - Input.input_clk ≤ 0; PipeNet.t - t(0) ≤ 300; PipeNet.t - gclk ≤ -1200; Input.input_clk - Observer.input_clk ≤ 0; Observer.input_clk - gclk ≤ 0; ]
    transitions [8]: exit2: PipeNet -> ['Observer']; PipeNet.Exit2 -> PipeNet.Reset; Observer._id12 -> Observer.pass; 
    -----------------------------------
    State [9]: ['PipeNet.Reset', 'Input.pass', 'Observer.pass']
    global_variables [9]: None
    Clock_constraints [9]: [t(0) - gclk ≤ -1550; t(0) - PipeNet.t ≤ -250; t(0) - Input.input_clk ≤ 0; t(0) - Observer.input_clk ≤ 0; gclk - Input.input_clk ≤ 0; PipeNet.t - t(0) ≤ 300; Input.input_clk - Observer.input_clk ≤ 0; Observer.input_clk - t(0) ≤ 1550; ]

The `Input` and `Observation` template created by `pyuppaal`. The cache file `*_pattern.xml` can be found in the same directory of the input model.
<br><br>
<img src=https://raw.githubusercontent.com/Jack0Chan/pyuppaal/main/src/test_integration/figs/pipeNetInput.png width=300 />
<img src=https://raw.githubusercontent.com/Jack0Chan/pyuppaal/main/src/test_integration/figs/pipeNetObserver.png width=350 />
<img src=https://raw.githubusercontent.com/Jack0Chan/pyuppaal/main/src/test_integration/figs/pipeNetModel.png width=350 />
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
   

<img src=https://raw.githubusercontent.com/Jack0Chan/pyuppaal/main/src/test_integration/figs/pipeNetPatterns.png width=300 />


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

<img src=https://raw.githubusercontent.com/Jack0Chan/pyuppaal/main/src/test_integration/figs/pipeNetMonitor1.png width=100% />

## Full Code


```python
import pyuppaal as pyu
# set verifyta path
# 原来的 PATH
# VERIFYTA_PATH = "uppaal\\Win_Linux-uppaal64-4.1.26\\bin-Windows\\verifyta.exe"
VERIFYTA_PATH = "C:\\Users\\T1\\Documents\\GitHub\\mcvsfd\\Win_Linux-uppaal64-4.1.26\\bin-Windows\\verifyta.exe"

pyu.set_verifyta_path(VERIFYTA_PATH)

# Load the `xml` model
pipeNet = pyu.UModel("demo_PipeNet.xml")
# save as a new file in order not to overwrite current file
pipeNet = pipeNet.save_as("demo_PipeNet_new.xml")

# Define the input.
inputs = pyu.TimedActions(actions=['input_ball', 'input_ball'], lb=[0, 1000], ub=[0, 1000])
# Define the observation.
# observations = pyu.TimedActions(actions=['exit1', 'exit2'], lb=[500, 1550], ub=[500, 1550])
observations = pyu.TimedActions(actions=['exit1', 'exit2'], lb=[500, 1550], ub=[500, 1550])
# Add input template.
pipeNet.add_input_template(inputs)
# Add observation template.
# raise ValueError("这里别忘了添加focused actions")
pipeNet.add_observer_template(observations, focused_actions=['exit1', 'exit2', 'exit3'])

# Query whether the model can simulate the inputs & observations
pipeNet.queries = 'E<> Observer.pass'
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

