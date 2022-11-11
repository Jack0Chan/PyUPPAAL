"""_summary_
"""
import os
from pyuppaal import Tracer, UModel, Verifyta
import verifyta_path

def _run_test_tracer(model_path, trace_path):
    """_summary_
    """
    model_path = verifyta_path.bring_to_root(model_path)
    trace_path = verifyta_path.bring_to_root(trace_path)

    Verifyta().easy_verify(model_path)
    sim_trace = Tracer.get_timed_trace(model_path, trace_path)
    assert os.path.exists(trace_path) is True
    os.remove(trace_path)
    return sim_trace

def test_tracer_basic():
    """_summary_
    """
    Verifyta().set_verifyta_path(verifyta_path.VERIFYTA_PATH)
    sim_trace = _run_test_tracer("pedestrian.xml", "pedestrian-1.xtr")
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

def test_tracer_trim():
    _run_test_tracer("test1.xml", "test1-1.xtr")
