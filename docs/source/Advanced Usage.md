

# Advanced Usage

### Verification

You can save the verification to `.xtr` file:

```python
p2_model_path = 'verifyta_demo2.xml'
p2_trace_path = 'verifyta_demo2_trace.xtr'
res2 = pyu.simple_verify(model_path=p2_model_path, trace_path=p2_trace_path)
```

You can also try multi-threads verify model list:

```python
model_path_list = [p1_model_path, p2_model_path] * 2
trace_path_list = [p1_trace_path, p2_trace_path] * 2
res3 = pyu.simple_verify(model_path=model_path_list, trace_path=trace_path_list, parallel='threads')
```

Some extraordinary parallel modes are provided:

```python
model_path_list = [p1_model_path, p2_model_path] * 100
trace_path_list = [p1_trace_path, p2_trace_path] * 100
# for loop
t0 = time.time()
for model, trace in zip(model_path_list, trace_path_list):
    v.simple_verify(model_path=model, trace_path=trace)
print(f'Verify with for loop, time usage {time.time() - t0}')

# multi-threads
t0 = time.time()
v.simple_verify(model_path=model_path_list, trace_path=trace_path_list, parallel='threads')
print(f'Verify with multi-threads, time usage {time.time() - t0}')

# multi-process
t0 = time.time()
v.simple_verify(model_path=model_path_list, trace_path=trace_path_list, parallel='process')
print(f'Verify with multi-process, time usage {time.time() - t0}')

## OUTPUT:
## Verify with for loop, time usage 10.146977186203
## Verify with multi-threads, time usage 2.935403108596802
## Verify with multi-process, time usage 3.98100137710571
```

### Find pattern

You can assign a query to find a pattern:

```python
model_path = 'Pedestrian_3.xml'
query = f'A[] not (LV1Pedestrian2.Crossing and Cars.Crossing)'
pyu.find_a_pattern_with_query(model_path=model_path,query=query, focused_actions=None, hold=True)

## OUTPUT:
## ('A[] not (LV1Pedestrian2.Crossing and Cars.Crossing)',
## ['pCheckLight', 'pRed', 'cCheckLight', 'cGreen'])
```

All patterns with query is also available:

```python
model_path='Pedestrian_new.xml'
query = f'E<> (PPedestrian.Crossing and PCar.Crossing)' # property query
focused_actions = ["pCheckLight", "pGreen", "pRed", "pYellow", "pCrss", "cCrss"]
pyu.find_all_patterns_with_query(model_path=model_path, query=query, focused_actions=focused_actions, hold=True)

## OUTPUT:
## [('E<> (PPedestrian.Crossing and PCar.Crossing)',
##   ['pCheckLight', 'pRed', 'pCrss', 'cCrss']),
##  ('E<> (PPedestrian.Crossing and PCar.Crossing) && !Monitor1.pass',
##   ['cCrss', 'pCheckLight', 'pRed', 'pCrss']),
##  ('E<> (PPedestrian.Crossing and PCar.Crossing) && !Monitor1.pass && !Monitor2.pass',
##   ['pCheckLight', 'pGreen', 'pCrss', 'cCrss']),
##  ('E<> (PPedestrian.Crossing and PCar.Crossing) && !Monitor1.pass && !Monitor2.pass && !Monitor3.pass',
##   ['pCheckLight', 'pYellow', 'pCrss', 'cCrss'])]
```

## Add monitor

You can quickly build a monitor without operating fussy GUI of UPPAAL:

```python
model_path = r'C:\Users\22215\OneDrive\Coding\Lab\AVNRT_Complete_GroundTruth.xml'
umod = pyu.UModel(model_path=model_path)
## The prama is one-to-one correspondent
observations = pyu.TimedActions(actions=['actPathHisV','actPathHisH','actPathHisA','actPathHisV'], lb=[20,106,145,340], ub=[20,106,145,340])
umod.add_monitor('Monitor0', observations, observe_actions=['actPathHisV','actPathHisH','actPathHisA','actPathHisV'], strict = True)
```

