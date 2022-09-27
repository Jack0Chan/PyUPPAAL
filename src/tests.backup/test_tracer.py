from pyuppaal import tracer
from pyuppaal import Verifyta

if __name__ == '__main__':
    v = Verifyta()
    # You MUST set the verifyta path firstly!
    # v.set_verifyta_path(r'D:/Softwares/uppaal64-4.1.25-5/bin-Windows/verifyta.exe')
    v.set_verifyta_path(r'C:/Users/22215/OneDrive/Software/UPPAAL/bin-Windows/verifyta.exe')

    p1_model_path = 'verifyta_demo2.xml'
    p1_trace_path = 'verifyta_demo2_trace-1.xtr'
    simtracer = tracer.SimulationTrace()
    simtracer.load_trace(p1_model_path, p1_trace_path, v)

# s

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