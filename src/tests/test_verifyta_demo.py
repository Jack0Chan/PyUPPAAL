from pyuppaal import Verifyta
import time


v = Verifyta()
# You MUST set the verifyta path firstly!
v.set_verifyta_path(r'D:\study\HCPSLAB\uppaal-controller\src\Win_Linux-uppaal64-4.1.26\bin-Darwin\verifyta.exe')

# verify P1 (verifyta_demo1.xml), save .xml file and print result
res = v.simple_verify(model_path='verifyta_demo1.xml', trace_path='verifyta_demo1_trace.xml')
print(res)
# result
"""
Options for the verification:
  Generating shortest trace
  Search order is breadth first
  Using conservative space optimisation
  Seed is 1656055072
  State space representation uses minimal constraint systems

Verifying formula 1 at /nta/queries/query[1]/formula
 -- Formula is NOT satisfied.
XMLTrace outputted to: verifyta_demo1_trace1.xml
"""
# verify P2 (verifyta_demo2.xml), save .xtr file and print result
res = v.simple_verify(model_path='verifyta_demo2.xml', trace_path='verifyta_demo2_trace.xtr')
print(res)
# result
"""
xxxxxxxxxxxx
"""

# verify P3 (verifyta_demo3.xml), save .xml file and print result
res = v.simple_verify(model_path='verifyta_demo3.xml', trace_path='verifyta_demo3_trace.xml')
print(res)
# result
"""
Options for the verification:
  Generating shortest trace
  Search order is breadth first
  Using conservative space optimisation
  Seed is 1656055250
  State space representation uses minimal constraint systems

Verifying formula 1 at /nta/queries/query[1]/formula
 -- Formula is satisfied.
"""

# verify P1, P2, P3 with multi-threads and multi-process for 20 repeats.
l_model_path = ['verifyta_demo1.xml', 'verifyta_demo2.xml', 'verifyta_demo3.xml'] * 20
l_trace_path = ['verifyta_demo1_trace.xml', 'verifyta_demo2_trace.xtr', 'verifyta_demo3_trace.xml'] * 20
# for loop
t0 = time.time()
for model, trace in zip(l_model_path, l_trace_path):
    v.simple_verify(model_path=model, trace_path=trace)
print(f'Verify with for loop, time usage {time.time() - t0}')

# multi-threads
t0 = time.time()
v.simple_verify_threads(model_paths=l_model_path, trace_paths=l_trace_path)
print(f'Verify with multi-threads, time usage {time.time() - t0}')

# multi-process
t0 = time.time()
v.simple_verify_process(model_paths=l_model_path, trace_paths=l_trace_path)
print(f'Verify with multi-process, time usage {time.time() - t0}')


# from pyuppaal import Verifyta
# import time
#
# if __name__ == '__main__':
#     v = Verifyta()
#     # You MUST set the verifyta path firstly!
#     v.set_verifyta_path('/Users/chenguangyao/Downloads/uppaal64-4.1.26/bin-Darwin/verifyta')
#
#     # verify P1 (verifyta_demo1.xml) and print result
#     res = v.simple_verify(model_path='verifyta_demo1.xml', trace_path='verifyta_demo1_trace.xml')
#     print(res)

