import os
# from symbol import simple_stmt
import pyuppaal
from pyuppaal import UModel
from verifyta_path import *
from pyuppaal import TimedActions

pyuppaal.set_verifyta_path(VERIFYTA_PATH)


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

def test_all_patterns():
    """_summary_
    """
    query = f'E<> (PPedestrian.Crossing and PCar.Crossing)' # property query
    focused_actions = ["pCheckLight", "pGreen", "pRed", "pYellow", "pCrss", "cCrss"]
    u = UModel(bring_to_root('pedestrian_new.xml'), auto_save=False)
    u.set_queries([query])
    res = u.find_all_patterns(focused_actions)
    assert len(res) == 4
    # print(len(res), list(map(lambda x: x.actions, res)))
