import os
# from symbol import simple_stmt
import pyuppaal
from pyuppaal import UModel
from verifyta_path import *
from pyuppaal import TimedActions


# pyuppaal.set_verifyta_path(VERIFYTA_PATH)

# u = UModel(bring_to_root('pedestrian.xml'))
# u.set_queries(['A[] not (LV1Pedestrian2.Crossing and Cars.Crossing)'])
# sim_trace = u.easy_verify()
# sim_trace.save_raw(bring_to_root('pedestrian_raw.txt'))
# print(sim_trace)
# print('====')
# print(u.templates)
# print(u.queries)
# print(u.broadcast_chan)

pyuppaal.set_verifyta_path(VERIFYTA_PATH)
u = UModel(bring_to_root('AVNRT_Fake_GroundTruth.xml'))
u.save_as(bring_to_root('AVNRT_Fake_GroundTruth_copy.xml'))
signals = TimedActions(["sigIn", "sigIn"], ["gclk >= 0", "gclk >= 320"], ["gclk <= 0", "gclk <= 320"])

u.add_input(signals)


def test_cg():
    """Test communication graph.
    """
    u = UModel(bring_to_root('pedestrian.xml'))
    # ==== before beautify ====
    tmp_file = bring_to_root('cg_pedestrain.md')
    m = u.get_communication_graph(save_path=tmp_file, is_beautify=False)
    assert os.path.exists(tmp_file) is True
    os.remove(tmp_file)
    print('==== before beautify ====\n', m)

    # ==== after beautify ====
    m.beautify()
    tmp_file = bring_to_root('cg_pedestrain_beauty.md')
    m.export(tmp_file)
    assert os.path.exists(tmp_file) is True
    os.remove(tmp_file)
    print('==== after beautify ====\n', m)

def test_verify():
    """_summary_
    """
    u = UModel(bring_to_root('pedestrian.xml'))
    u.set_queries(['A[] not (LV1Pedestrian2.Crossing and Cars.Crossing)'])


def test_add_input_template():
    u = UModel(bring_to_root('AVNRT_Fake_GroundTruth.xml'))
    u.save_as(bring_to_root('AVNRT_Fake_GroundTruth_copy.xml'))
    signals = TimedActions(["sigIn!", "sigIn!"], ["gclk >= 0", "gclk >= 320"], ["gclk <= 0", "gclk <= 320"])
    u.add_input(signals)