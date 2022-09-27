"""_summary_
"""
from pyuppaal import Tracer
from pyuppaal import Verifyta
from verifyta_path import VERIFYTA_PATH

Verifyta().set_verifyta_path(VERIFYTA_PATH)
model_path = '/Users/chenguangyao/Documents/GitHub/pyuppaal/src/tests/pedestrian.xml'
trace_path = '/Users/chenguangyao/Documents/GitHub/pyuppaal/src/tests/pedestrian-1.xtr'
Verifyta().easy_verify(model_path)
Tracer.get_timed_trace(model_path, trace_path)