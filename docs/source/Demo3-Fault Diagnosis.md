# Demo3 - Fault Diagnosis

**Note: we are woking on CAV-2024 tool paper. The documentation will be updated to a structure similar to Demo1-PipeNet before 2024.4.1.**

<img src=https://raw.githubusercontent.com/Jack0Chan/pyuppaal/main/src/test_demos/models.jpg width=300 />


```python
# setup pyuppaal
import pyuppaal
from pyuppaal import UModel

print(pyuppaal.__version__)
pyuppaal.set_verifyta_path(r"C:\Users\Taco\Documents\GitHub\cav2024\bin\uppaal64-4.1.26\bin-Windows\verifyta.exe")
```

    1.2.0
    


```python
m_a, m_b = UModel('model_A.xml'), UModel('model_B.xml')
sigma_o, sigma_un = ['a', 'b', 'c'], ['f']

# identification for fault 'f' with o1 = ['a', 'a', 'a'] and o2 = ['a', 'b', 'a']
o1, o2 = ['a', 'a', 'a'], ['a', 'b', 'a']
res1_a = m_a.fault_identification(o1, fault='f', sigma_o=sigma_o, sigma_un=sigma_un)
res1_b = m_b.fault_identification(o1, fault='f', sigma_o=sigma_o, sigma_un=sigma_un)
print(f"{o1} can detect 'f'. Model A: {res1_a[0]},  Model B: {res1_b[0]}.")
res2_a = m_a.fault_identification(o2, fault='f', sigma_o=sigma_o, sigma_un=sigma_un)
res2_b = m_b.fault_identification(o2, fault='f', sigma_o=sigma_o, sigma_un=sigma_un)
print(f"{o2} can detect 'f'. Model A: {res2_a[0]}, Model B: {res2_b[0]}.")
# n-diagnosability for fault 'f', for n=3
res_a = m_a.fault_diagnosability(fault='f', n=3, sigma_o=sigma_o, sigma_un=sigma_un)
res_b = m_b.fault_diagnosability(fault='f', n=3, sigma_o=sigma_o, sigma_un=sigma_un)
print(f"Model A is 3-diagnosable: {res_a[0]}, reason: {res_a[1].untime_pattern}.")
print(f"Model B is 3-diagnosable: {res_b[0]}.")
```

    ['a', 'a', 'a'] can detect 'f'. Model A: True,  Model B: True.
    ['a', 'b', 'a'] can detect 'f'. Model A: False, Model B: True.
    Model A is 3-diagnosable: False, reason: ['c', 'a', 'b', 'a'].
    Model B is 3-diagnosable: True.
    
