""" Integration tests for UModel class. 
    Files required:
        - pedestrian.xml
        - pedestrian_new.xml
        - demo_new.xml
        - toy_model_diagnosable.xml
        - toy_model_not_diagnosable.xml
        - EPS.xml
        - EPS_ScanFirst.xml
        - test1.xml
        - demo1.xml
        - demo2.xml
"""

import os
# from symbol import simple_stmt
import pyuppaal
from pyuppaal import UModel, Verifyta
from typing import List
# import time

pyuppaal.DeveloperTools.set_verifyta_path_dev()


def bring_to_root(file_name: str):
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(ROOT_DIR, file_name)


keep_tmp_file = False


def test_cg():
    """Test communication graph."""
    u = UModel(bring_to_root('pedestrian.xml'))

    # ==== before beautify ====
    tmp_file = bring_to_root('cg_pedestrain.md')
    u.save_path = tmp_file  # Set the save path
    u.is_beautify = False   # Set beautify to False
    m = u.get_communication_graph()  # Access the property
    m.export(tmp_file)      # Export the graph
    assert os.path.exists(tmp_file) is True
    os.remove(tmp_file)
    print('==== before beautify ====\n', m)

    # ==== after beautify ====
    u.is_beautify = True    # Set beautify to True
    m.beautify()
    tmp_file = bring_to_root('cg_pedestrain_beauty.md')
    m.export(tmp_file)      # Export the graph
    assert os.path.exists(tmp_file) is True
    os.remove(tmp_file)
    print('==== after beautify ====\n', m)


def test_all_patterns():
    """_summary_
    """
    query = f'E<> (PPedestrian.Crossing and PCar.Crossing)'  # property query
    focused_actions = ["pCheckLight", "pGreen",
                       "pRed", "pYellow", "pCrss", "cCrss"]
    u = UModel(bring_to_root('pedestrian_new.xml'))
    u.queries = [query]
    res = u.find_all_patterns(focused_actions, max_patterns=4, keep_tmp_file=keep_tmp_file)
    assert len(res) == 4
    # os.remove(bring_to_root("pedestrian_new_pattern_a_pattern-1.xtr"))
    # os.remove(bring_to_root("pedestrian_new_pattern_a_pattern.xml"))


def test_all_patterns_iter():
    """Test for finding all patterns using iterator."""
    query = f'E<> (PPedestrian.Crossing and PCar.Crossing)'  # property query
    focused_actions = ["pCheckLight", "pGreen",
                       "pRed", "pYellow", "pCrss", "cCrss"]
    u = UModel(bring_to_root('pedestrian_new.xml'))
    u.queries = [query]

    # Using the iterator method
    pattern_iterator = u.find_all_patterns_iter(
        focused_actions, max_patterns=4, keep_tmp_file=keep_tmp_file)

    # Retrieve patterns from the iterator
    res = list(pattern_iterator)
    assert len(res) == 4


def test_all_patterns_iter_consistance():
    """ Compare the results of find_all_patterns and find_all_patterns_iter"""
    query = 'E<> (PPedestrian.Crossing and PCar.Crossing)'  # property query
    focused_actions = ["pCheckLight", "pGreen",
                       "pRed", "pYellow", "pCrss", "cCrss"]
    max_patterns = 4  # Set search max patterns

    # Setup UModel instance
    u = UModel(bring_to_root('pedestrian_new.xml'))
    u.queries = [query]

    # Using traditional find_all_patterns
    traditional_results = u.find_all_patterns(
        focused_actions, max_patterns=max_patterns, keep_tmp_file=keep_tmp_file)

    # Using find_all_patterns_iter
    pattern_iterator = u.find_all_patterns_iter(
        focused_actions, max_patterns=max_patterns, keep_tmp_file=keep_tmp_file)
    iter_results = list(pattern_iterator)

    # Comparing the results
    assert len(traditional_results) == len(iter_results)
    for trad, iter in zip(traditional_results, iter_results):
        assert trad == iter

    # Cleanup
    # os.remove(bring_to_root("pedestrian_new_pattern-1.xtr"))
    # os.remove(bring_to_root("pedestrian_new_pattern.xml"))


def test_easy_verify():
    """_summary_
    """
    u = UModel(bring_to_root('demo_new.xml'))
    # u.queries = 'E<> P1.pass' # this will write to model. Since we already have, we d not need to write again.
    res = u.easy_verify(verify_options='-t 1 -o 0')
    print(res)

# test_easy_verify()


def test_diagnosibility():  # This test is based on the toy model.
    u_diagnosable = UModel(bring_to_root('toy_model_diagnosable.xml'))
    u_not_diagnosable = UModel(bring_to_root('toy_model_not_diagnosable.xml'))
    sigma_o = ['a', 'b', 'c', 'action']
    sigma_un = ['f']
    sigma_f = ['f']

    n = 3

    # for f in sigma_f:
    #     t0 = time.time()
    # u.fault_diagnosability_increasing(fault=f,max_n=n,sigma_o=sigma_o,sigma_un=sigma_un)
    # print(f"Time for fault_diagnosability_increasing: {round(time.time()-t0)} seconds")

    # t0 = time.time()
    res_diagosable = u_diagnosable.fault_diagnosability(
        fault=sigma_f[0], n=n, sigma_o=sigma_o, sigma_un=sigma_un, visual=True, keep_tmp_file=keep_tmp_file)
    res_not_diagnosable = u_not_diagnosable.fault_diagnosability(
        fault=sigma_f[0], n=n, sigma_o=sigma_o, sigma_un=sigma_un, visual=False, keep_tmp_file=keep_tmp_file)
    # print(f"   Time usage without optimization {round(time.time() - t0, 2)}.")
    assert res_diagosable[0] == True and res_not_diagnosable[0] == False


def test_identification():  # This test is based on the EPS model.
    sigma_f: List[str] = ['fault_relay1_stuck_on', 'fault_relay1_stuck_off',
                          'fault_relay2_stuck_on', 'fault_relay2_stuck_off',
                          'fault_relay3_stuck_on', 'fault_relay3_stuck_off',
                          'fault_battery1_burn', 'fault_battery2_burn',]
    # unobservable interacting events, including faults
    sigma_un: List[str] = ['battery1_low', 'battery1_high', 'battery2_low', 'battery2_high',
                           'relay1_low', 'relay1_high', 'relay2_low', 'relay2_high', 'relay3_low', 'relay3_high',
                           'wire1_low', 'wire1_high', 'wire2_low', 'wire2_high',
                           'wire3_low', 'wire3_high', 'wire4_low', 'wire4_high'] + sigma_f
    # control events
    sigma_c: List[str] = ['relay1_on', 'relay1_off',
                          'relay2_on', 'relay2_off', 'relay3_on', 'relay3_off']
    # sensor events
    sigma_s: List[str] = ['v1_low', 'v2_low',
                          'v1_high', 'v2_high', 'notwork', 'work']
    # observable events, including controls
    sigma_o: List[str] = sigma_s + sigma_c

    u = UModel(bring_to_root('EPS.xml'))

    # identified_faults = []
    # for f in sigma_f:
    #     identify_res = self.fault_identification(
    #         suffix_sequence=suffix_sequence, fault=f, sigma_o=sigma_o, sigma_un=sigma_un, keep_tmp_file=keep_tmp_file)
    #     if identify_res[0]:
    #         identified_faults.append(f)
    # return identified_faults

    # res.append f if f is identified

    res = []
    obs = ['relay1_on', 'relay2_off', 'relay3_on',
           'v1_low', 'v2_high', 'notwork']
    for f in sigma_f:
        if u.fault_identification(suffix_sequence=obs, fault=f,
                                  sigma_o=sigma_o, sigma_un=sigma_un, keep_tmp_file=keep_tmp_file)[0]:
            res.append(f)
    assert res == ['fault_battery1_burn']

    res = []
    obs = ['relay1_off', 'relay2_on', 'relay3_on',
           'v1_low', 'v2_low', 'notwork']
    for f in sigma_f:
        if u.fault_identification(suffix_sequence=obs, fault=f,
                                  sigma_o=sigma_o, sigma_un=sigma_un, keep_tmp_file=keep_tmp_file)[0]:
            res.append(f)
    assert res == ['fault_battery1_burn', 'fault_battery2_burn']

    res = []
    obs = ['v1_high', 'v2_high', 'relay1_on',
           'relay2_off', 'relay3_on',  'notwork']
    for f in sigma_f:
        if u.fault_identification(suffix_sequence=obs, fault=f,
                                  sigma_o=sigma_o, sigma_un=sigma_un, keep_tmp_file=keep_tmp_file)[0]:
            res.append(f)
    assert res == []


def test_fault_tolerance():
    CONTROL_LENGTH = 2
    u = UModel(bring_to_root('EPS_ScanFirst.xml'))
    # system_prefix = u.system[u.system.rfind('system')]
    # u.system = system_prefix +'\n' + 'system battery1, battery2, wire1, wire2, wire3, wire4, relay1, relay2, relay3, load, v1, v2, controller_scan_first, scanner;'

    safety_enents = ['relay1_off', 'relay2_off', 'relay3_off']  # safety operation
    sigma_f: List[str] = ['fault_relay1_stuck_on', 'fault_relay1_stuck_off',
                          'fault_relay2_stuck_on', 'fault_relay2_stuck_off',
                          'fault_relay3_stuck_on', 'fault_relay3_stuck_off',
                          'fault_battery1_burn', 'fault_battery2_burn',]
    sigma_c: List[str] = ['relay1_on', 'relay1_off',
                          'relay2_on', 'relay2_off', 'relay3_on', 'relay3_off']

    # test for fault_tolerance
    res = u.fault_tolerance(target_state='load.working', identified_faults=['fault_battery1_burn'], safety_events=safety_enents,
                            sigma_f=sigma_f, sigma_c=sigma_c,
                            control_length=CONTROL_LENGTH, keep_tmp_file=keep_tmp_file)
    # print(str(res) )
    assert ("Fault can be tolerated" in res)

    res = u.fault_tolerance(target_state='load.working', identified_faults=['fault_battery1_burn', 'fault_battery2_burn'],
                            safety_events=safety_enents,
                            sigma_f=sigma_f, sigma_c=sigma_c,
                            control_length=CONTROL_LENGTH, keep_tmp_file=keep_tmp_file)
    # print(str(res))
    assert ("Fault can NOT be tolerated" in res)

    res = u.fault_tolerance(target_state='load.working', identified_faults=['fault_battery1_burn', 'fault_relay1_stuck_off'],
                            safety_events=safety_enents,
                            sigma_f=sigma_f, sigma_c=sigma_c,
                            control_length=CONTROL_LENGTH, keep_tmp_file=keep_tmp_file)
    # print(str(res))
    assert ("Fault can be tolerated" in res)

# test_fault_tolerance()

# xtr tracer test.


def __run_test_tracer(model_path: str, trace_path: str):
    """_summary_
    """

    if Verifyta().get_uppaal_version() == 5:
        trace_path = trace_path.replace("-1.xtr", "_xtr-1")

    u = UModel(bring_to_root(model_path))
    trace_path = bring_to_root(trace_path)
    # u.queries -> use default in model.
    u.verify(verify_options='-t 1 -o 0')
    sim_trace = u.load_xtr_trace(trace_path)
    assert os.path.exists(trace_path) is True
    os.remove(trace_path)
    return sim_trace


def test_tracer_basic():
    """_summary_
    """
    sim_trace = __run_test_tracer("pedestrian.xml", "pedestrian-1.xtr")
    # ==== save raw SimTrace ====
    raw_sim_trace_path = bring_to_root('pedestrian-raw.txt')
    sim_trace.save_raw(raw_sim_trace_path)
    assert os.path.exists(raw_sim_trace_path) is True
    os.remove(raw_sim_trace_path)

    # ==== save SimTrace ====
    sim_trace_path = bring_to_root('pedestrian.txt')
    sim_trace.save(sim_trace_path)
    assert os.path.exists(sim_trace_path) is True
    os.remove(sim_trace_path)


def test_tracer_trim():
    __run_test_tracer("test1.xml", "test1-1.xtr")


def test_multithreaded_tracer():
    import multiprocessing.dummy as mp
    """Run multiple tracer tests in parallel using multi-threading."""
    test_cases = [
        ("demo1.xml", "demo1-1.xtr"),
        ("demo2.xml", "demo2-1.xtr")
    ]
    # Create a pool of threads
    pool = mp.Pool(4)
    # Run the tracer tests in parallel
    pool.starmap(__run_test_tracer, test_cases)
    pool.close()
    pool.join()


if __name__ == "__main__":
    test_tracer_basic()
    # test_multithreaded_tracer()
    # test_diagnosibility()
    pass
