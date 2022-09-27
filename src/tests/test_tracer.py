"""_summary_
"""
import os
from pyuppaal import Tracer
from pyuppaal import Verifyta
from verifyta_path import ROOT_DIR,VERIFYTA_PATH

Verifyta().set_verifyta_path(VERIFYTA_PATH)
model_path = os.path.join(ROOT_DIR, 'pedestrian.xml')
# model_path = os.path.join(ROOT_DIR, 'AVNRT_Fake_GroundTruth.xml')
trace_path = os.path.join(ROOT_DIR, 'pedestrian-1.xtr')
Verifyta().easy_verify(model_path)
print(Tracer.get_timed_trace(model_path, trace_path, hold=False))