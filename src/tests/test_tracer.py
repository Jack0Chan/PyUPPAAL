"""_summary_
"""
import os
from pyuppaal import Tracer, UModel, Verifyta
import verifyta_path


def test_tracer_basic():
    """_summary_
    """
    Verifyta().set_verifyta_path(verifyta_path.VERIFYTA_PATH)
    model_path = verifyta_path.bring_to_root('pedestrian.xml')
    trace_path = verifyta_path.bring_to_root('pedestrian-1.xtr')

    Verifyta().easy_verify(model_path)
    sim_trace = Tracer.get_timed_trace(model_path, trace_path)
    assert os.path.exists(trace_path) is True
    os.remove(trace_path)
    # ==== save raw SimTrace ====
    raw_sim_trace_path = verifyta_path.bring_to_root('pedestrian-raw.txt')
    sim_trace.save_raw(raw_sim_trace_path)
    assert os.path.exists(raw_sim_trace_path) is True
    os.remove(raw_sim_trace_path)

    # ==== save SimTrace ====
    sim_trace_path = verifyta_path.bring_to_root('pedestrian.txt')
    sim_trace.save(sim_trace_path)
    assert os.path.exists(sim_trace_path) is True
    os.remove(sim_trace_path)

def test_tracer_trim_transitions():
    """_summary_
    """
    Verifyta().set_verifyta_path(verifyta_path.VERIFYTA_PATH)
    model_path = verifyta_path.bring_to_root('M0_AVNRT_5_4.xml')
    umod = UModel(model_path)
    assert umod.easy_verify() is not None
    os.remove(verifyta_path.bring_to_root('M0_AVNRT_5_4-1.xtr'))
