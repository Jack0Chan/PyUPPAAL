"""This module contains the unit tests for the Mermaid class.
    It generates mermaid, svg, png, jpg files from a mermaid string.
    The mermaid string is generated from `pedestrian.xml`.
"""
import os
from pyuppaal import Mermaid

def bring_to_root(file_name: str):
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(ROOT_DIR, file_name)


def test_basic():
    """_summary_
    """
    s = '''```mermaid
TrafficLights--cGreen-->Cars
TrafficLights--cYellow-->Cars
LV1Pedestrian1--pCrss-->Cars
LV1Pedestrian2--pCrss-->Cars```'''

    m = Mermaid(s)
    assert m.mermaid_str == s
    # ==== remove ====
    res = '''```mermaid
graph TD
TrafficLights--cGreen-->Cars
TrafficLights--cYellow-->Cars
LV1Pedestrian2--pCrss-->Cars
```'''
    assert m.remove('LV1Pedestrian1') == res
    res = [['TrafficLights', 'cGreen', 'Cars'],
           ['TrafficLights', 'cYellow', 'Cars'],
           ['LV1Pedestrian2', 'pCrss', 'Cars']]
    assert m.mermaid_list == res
    # ==== beautify ====
    res = '''```mermaid
graph TD
TrafficLights--cGreen,cYellow-->Cars
LV1Pedestrian2--pCrss-->Cars
```'''
    assert m.beautify() == res
    # ==== remove ====
    res = '''```mermaid
graph TD
TrafficLights--cGreen-->Cars
TrafficLights--cYellow-->Cars
```'''
    assert m.remove('LV1Pedestrian2') == res
    # ==== beautify ====
    res = '''```mermaid
graph TD
TrafficLights--cGreen,cYellow-->Cars
```'''
    assert m.beautify() == res


def test_save():
    """_summary_
    """
    s = '''```mermaid
TrafficLights--cGreen-->Cars
TrafficLights--cYellow-->Cars
LV1Pedestrian1--pCrss-->Cars
LV1Pedestrian2--pCrss-->Cars```'''
    m = Mermaid(s)
    export_files = ['mermaid_test.md', 'mermaid_test.svg', 'mermaid_test.jpg', 'mermaid_test.png']
    for export_file in export_files:
        bring_to_root(export_file)
        m.export(export_file)
        assert os.path.exists(export_file) is True
        # delete file
        os.remove(export_file)


test_save()