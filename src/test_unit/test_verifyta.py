"""命令行输入pytest -s可以查看print
"""
import os
import pytest
from pyuppaal import Verifyta
import pyuppaal


def bring_to_root(file_name: str):
    if Verifyta().get_uppaal_version() == 5:
        file_name = file_name.replace('-1.xtr', '_xtr-1')
    root_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(root_dir, file_name)


VERIFYTA_PATH = pyuppaal.DeveloperTools.get_verifyta_path_dev()

Verifyta().set_verifyta_path(VERIFYTA_PATH)


def test_set_verifyta_path():
    """_summary_
    """
    # correct verifyta path
    Verifyta().set_verifyta_path(VERIFYTA_PATH)
    # wrong verifyta path
    with pytest.raises(ValueError) as excinfo:
        Verifyta().set_verifyta_path('invalid path')


def test_verify(i=0):
    """input i for multi-thread testing
    """
    Verifyta().set_verifyta_path(VERIFYTA_PATH)
    model_paths = [bring_to_root('demo1.xml'),
                   bring_to_root('demo2.xml'),
                   bring_to_root('demo3.xml')]
    for model_path in model_paths:
        verify_res = Verifyta().verify(model_path,None, verify_options='-t 1 -o 0')
        assert 'satisfied' in verify_res


def test_multithread():
    import multiprocessing.dummy as mp
    p = mp.Pool()
    res = p.map(test_verify, range(10))
    assert len(res) == 10


def test_easy_verify1():
    """_summary_
    """
    Verifyta().set_verifyta_path(VERIFYTA_PATH)
    model_paths = [bring_to_root('demo1.xml'),
                   bring_to_root('demo2.xml'),
                   bring_to_root('demo3.xml')]
    # ======== without trace_paths ========
    # the third model do not have counter-example
    # should automatically create .xtr counter-example
    options = ['-t 1 -o 0', '-t 2 -o 0', '-t 2 -o 1']
    # Verifyta().verify(model_paths, verify_options=options)
    # verify one by one
    for model_path, option in zip(model_paths, options):
        Verifyta().verify(model_path, verify_options=option)
        
    target_trace_paths = [bring_to_root('demo1-1.xtr'),
                          bring_to_root('demo2-1.xtr')]
    for trace_path in target_trace_paths:
        assert os.path.exists(trace_path) is True
        os.remove(trace_path)


def test_easy_verify2():
    """_summary_
    """
    Verifyta().set_verifyta_path(VERIFYTA_PATH)
    model_paths = [bring_to_root('demo1.xml'),
                   bring_to_root('demo2.xml'),
                   bring_to_root('demo3.xml')]
    # ======== with trace_paths ========
    trace_paths = [bring_to_root('t1.xtr'),
                   bring_to_root('t2.xtr'),
                   bring_to_root('t3.xtr')]
    # res = Verifyta().verify(model_paths, trace_path=trace_paths,
    #                              verify_options='-t 1 -o 0')
    #verify one by one
    for model_path, trace_path in zip(model_paths, trace_paths):
        res = Verifyta().verify(model_path, trace_path=trace_path, verify_options='-t 1 -o 0')
        
    print(res)
    # the third model do not have counter-example
    target_trace_paths = [bring_to_root('t1-1.xtr'), bring_to_root('t2-1.xtr')]
    for trace_path in target_trace_paths:
        assert os.path.exists(trace_path) is True
        os.remove(trace_path)


if __name__ == '__main__':
    test_set_verifyta_path()
    test_verify()
    test_easy_verify1()
    test_easy_verify2()

