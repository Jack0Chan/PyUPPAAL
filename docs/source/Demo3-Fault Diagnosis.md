# Demo3 - Fault Diagnosis and Identification

This demo shows two slightly different automata, `Model_A` and `Model_B`, with observable actions $\Sigma^o$ = `[a, b, c]`, and unobservable actions $\Sigma^{un}$ = `[f]`. The following four propositions presented are logically straightforward and easily reasoned, as they are based on a simple example:

1. Suffix `aaa` implies `f`. For suffix `aaa`, both `Model_A` and `Model_B` identify `f`, as it can only be observed post-occurrence of `f`.
2. Suffix `aba` does not confirm $f$ in `Model_A` The sequence $aba$ can occur during normal and fault conditions in `Model_A`. Therefore, `aba` does not conclusively suggest `f` has occurred.
3. Fault `f` in `Model_A` is not 3-Diagnosable. Given that the observation suffix `aba`, covering three events, occurs in both normal and fault modes of `Model_A`, it's impossible to unequivocally diagnose `f` within this span. Thus, `Model_A` is not 3-diagnosable.
4. Fault `f` in `Model_B` is 3-Diagnosable. In `Model_B`, the three-event suffixes `[abb, bbb]` are exclusive to the normal mode and absent in the fault mode. Conversely, `[aaa, aab, aba, bab, baa, bab]` are unique to the fault mode. The absence of common suffixes between modes in `Model_B` guarantees its 3-diagnosability, ensuring accurate fault identification from any three-event sequence.
5. You can download the models: [model_A.xml](https://github.com/Jack0Chan/PyUPPAAL/blob/main/src/test_demos/model_A.xml) and [model_B.xml](https://github.com/Jack0Chan/PyUPPAAL/blob/main/src/test_demos/model_B.xml).

<img src=https://raw.githubusercontent.com/Jack0Chan/pyuppaal/main/src/test_demos/figs/diagnosis_identification.png width=400 />


```python
import pyuppaal
from pyuppaal import UModel

print(pyuppaal.__version__)
pyuppaal.set_verifyta_path(r"C:\Users\10262\Documents\GitHub\cav2024\bin\uppaal64-4.1.26\bin-Windows\verifyta.exe")
```

    1.2.1
    

## 1. Fault Identification

Temorary files `tmp_identify_id.xml` will be saved. For more details, please read the docs of [UModel.fault_identification()](https://pyuppaal.readthedocs.io/en/latest/USER%20API.html#pyuppaal.umodel.UModel.fault_identification).

1. Suffix `aaa` implies `f`. For suffix `aaa`, both `Model_A` and `Model_B` identify `f`, as it can only be observed post-occurrence of `f`.
2. Suffix `aba` does not confirm $f$ in `Model_A` The sequence $aba$ can occur during normal and fault conditions in `Model_A`. Therefore, `aba` does not conclusively suggest `f` has occurred.


```python
m_a, m_b = UModel('model_A.xml'), UModel('model_B.xml')
sigma_o, sigma_un = ['a', 'b', 'c'], ['f']

# identification for fault 'f' with o1 = ['a', 'a', 'a'] and o2 = ['a', 'b', 'a']
o1, o2 = ['a', 'a', 'a'], ['a', 'b', 'a']
res1_a = m_a.fault_identification(o1, fault='f', sigma_o=sigma_o, sigma_un=sigma_un)
res1_b = m_b.fault_identification(o1, fault='f', sigma_o=sigma_o, sigma_un=sigma_un)
print(f"{o1} can identify 'f'. Model A: {res1_a[0]},  Model B: {res1_b[0]}.")
res2_a = m_a.fault_identification(o2, fault='f', sigma_o=sigma_o, sigma_un=sigma_un)
res2_b = m_b.fault_identification(o2, fault='f', sigma_o=sigma_o, sigma_un=sigma_un)
print(f"{o2} can identify 'f'. Model A: {res2_a[0]}, Model B: {res2_b[0]}.")
assert res1_a[0] == True
assert res1_b[0] == True
assert res2_a[0] == False
assert res2_b[0] == True
```

    ['a', 'a', 'a'] can identify 'f'. Model A: True,  Model B: True.
    ['a', 'b', 'a'] can identify 'f'. Model A: False, Model B: True.
    

## 2. Fault Diagnosability

Temorary files `tmp_diagnosable_suffix_id.xml` will be saved. For more details, please read the docs of [UModel.fault_diagnosability()](https://pyuppaal.readthedocs.io/en/latest/USER%20API.html#pyuppaal.umodel.UModel.fault_diagnosability).

1. Fault `f` in `Model_A` is not 3-Diagnosable. Given that the observation suffix `aba`, covering three events, occurs in both normal and fault modes of `Model_A`, it's impossible to unequivocally diagnose `f` within this span. Thus, `Model_A` is not 3-diagnosable.
2. Fault `f` in `Model_B` is 3-Diagnosable. In `Model_B`, the three-event suffixes `[abb, bbb]` are exclusive to the normal mode and absent in the fault mode. Conversely, `[aaa, aab, aba, bab, baa, bab]` are unique to the fault mode. The absence of common suffixes between modes in `Model_B` guarantees its 3-diagnosability, ensuring accurate fault identification from any three-event sequence.


```python
# n-diagnosability for fault 'f', for n=3
res3_a = m_a.fault_diagnosability(fault='f', n=3, sigma_o=sigma_o, sigma_un=sigma_un)
res3_b = m_b.fault_diagnosability(fault='f', n=3, sigma_o=sigma_o, sigma_un=sigma_un)
print(f"Model A is 3-diagnosable: {res3_a[0]}, reason: {res3_a[1].untime_pattern}.")
print(f"Model B is 3-diagnosable: {res3_b[0]}.")

assert res2_a[0] == False
assert res2_b[0] == True
```

    Model A is 3-diagnosable: False, reason: ['c', 'a', 'b', 'a'].
    Model B is 3-diagnosable: True.
    
