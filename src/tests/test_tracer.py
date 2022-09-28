"""_summary_
"""
import verifyta_path
from pyuppaal import Tracer
from pyuppaal import Verifyta

Verifyta().set_verifyta_path(verifyta_path.VERIFYTA_PATH)
model_path = verifyta_path.bring_to_root('AVNRT_Fake_GroundTruth.xml')
trace_path = verifyta_path.bring_to_root('AVNRT_Fake_GroundTruth-1.xtr')
Verifyta().easy_verify(model_path)

sim_trace = Tracer.get_timed_trace(model_path, trace_path)
print(sim_trace)


# Verifyta().set_verifyta_path(VERIFYTA_PATH)
# model_path = bring_to_root('pedestrian.xml')
# trace_path = bring_to_root('pedestrian-1.xtr')
# Verifyta().easy_verify(model_path)
# print(Tracer.get_timed_trace(model_path, trace_path, hold=False))