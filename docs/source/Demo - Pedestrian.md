# Demo2 - Pedestrian

```python
import os

import pyuppaal as pyu
from pyuppaal import UModel, Verifyta
from pyuppaal.monitors import Monitors

print(pyu.__version__)

def bring_to_root(file_name: str):
    # ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    ROOT_DIR = os.path.dirname("C://Users//Taco//Documents//GitHub//cav2024//Demo-Pedestrian//")
    return os.path.join(ROOT_DIR, file_name)

pyu.DeveloperTools.set_verifyta_path_dev()
```

    1.2.1

```python
# Load the `xml` model
pipeNet = UModel(bring_to_root("pedestrian.xml"))
# save as a new file in order not to overwrite current file
pipeNet = pipeNet.save_as(bring_to_root("demo_pedestrian.xml"))
```

#### Verifyta

```python
# we enumerate all the options for verifyta.
verify_options = [' -t 0 -o 0',
                  ' -t 0 -o 1',
                  ' -t 0 -o 2',
                  ' -t 1 -o 0',
                  ' -t 1 -o 1',
                  ' -t 1 -o 2',
                  ' -t 1 -o 3',
                  ' -t 1 -o 4',
                  ' -t 2 -o 0', 
                  ' -t 2 -o 1',
                  ' -t 2 -o 2',
                  ' -t 2 -o 3',
                  ' -t 2 -o 4'
                  ] 

# diagnostic_options = [f' -t {i}']

res = []

focused_actions = ["pCheckLight", "pGreen",
                       "pRed", "pYellow", "pCrss", "cCrss"]
for i, verify_option in enumerate(verify_options):
    res.append(pipeNet.easy_verify(verify_options=verify_option,keep_tmp_file=False).filter_by_actions(focused_actions).untime_pattern)


print(set([ "-".join(r) for r in res]))

  
```

    {'cCrss-pCheckLight-pRed-pCrss', 'pCheckLight-pRed-pCrss-cCrss'}

```python
# Load the model
M = UModel("pedestrian.xml")
M.queries = "E<> (PPedestrian.Crossing and PCar.Crossing)"
traces = pipeNet.find_all_patterns(focused_actions=["pCheckLight", "pGreen", "pRed", "pYellow", "pCrss", "cCrss"],keep_tmp_file=False)

for trace in traces:
    print(trace.untime_pattern)
```

    ['pCheckLight', 'pRed', 'pCrss', 'cCrss']
    ['cCrss', 'pCheckLight', 'pRed', 'pCrss']
    ['pCheckLight', 'pGreen', 'pCrss', 'cCrss']
    ['pCheckLight', 'pYellow', 'pCrss', 'cCrss']

```python
M.get_communication_graph()
```

    ``mermaid     graph TD     PCar--cCheckLight-->PTrafficLights     PTrafficLights--cGreen,cRed,cYellow-->PCar     PTrafficLights--pGreen,pRed,pYellow-->PPedestrian     PPedestrian--pCheckLight-->PTrafficLights     ``
