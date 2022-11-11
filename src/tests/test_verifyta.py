"""命令行输入pytest -s可以查看print
"""
import os
import time
import pytest
import verifyta_path
from pyuppaal import Verifyta

Verifyta().set_verifyta_path(verifyta_path.VERIFYTA_PATH)


def test_set_verifyta_path():
    """_summary_
    """
    Verifyta().set_verifyta_path(verifyta_path.VERIFYTA_PATH)
    with pytest.raises(ValueError) as excinfo:
        Verifyta().set_verifyta_path('invalid path')
    assert Verifyta().set_verifyta_path(verifyta_path.VERIFYTA_PATH) is True


def test_verify():
    """_summary_
    """
    Verifyta().set_verifyta_path(verifyta_path.VERIFYTA_PATH)
    model_paths = [verifyta_path.bring_to_root('demo1.xml'),
                   verifyta_path.bring_to_root('demo2.xml'),
                   verifyta_path.bring_to_root('demo3.xml')]
    # single thread loop
    t0 = time.time()
    verify_ress = Verifyta().verify(model_paths, verify_options='-t 1 -o 0')
    for verify_res in verify_ress:
        assert 'satisfied' in verify_res
    t1 = time.time()
    # multi-thread
    verify_ress = Verifyta().verify(model_paths, verify_options=[
        '-t 1 -o 0', '-t 2 -o 0', '-t 2 -o 1'], num_threads=3)
    for verify_res in verify_ress:
        assert 'satisfied' in verify_res
    t2 = time.time()
    # time usage
    single_thread_time = round(t1-t0, 2)
    multi_thread_time = round(t2-t1, 2)
    assert single_thread_time > multi_thread_time
    info = f'3个复杂度相似单不完全相同任务, 单线程: {single_thread_time}s,'
    info += f'单线程平均: {round(single_thread_time/3, 2)}s, 3线程: {multi_thread_time}s.'
    print(info)


def test_easy_verify1():
    """_summary_
    """
    Verifyta().set_verifyta_path(verifyta_path.VERIFYTA_PATH)
    model_paths = [verifyta_path.bring_to_root('demo1.xml'),
                   verifyta_path.bring_to_root('demo2.xml'),
                   verifyta_path.bring_to_root('demo3.xml')]
    # ======== without trace_paths ========
    # the third model do not have counter-example
    # should automatically create .xtr counter-example
    res = Verifyta().easy_verify(model_paths, verify_options=[
        '-t 1 -o 0', '-t 2 -o 0', '-t 2 -o 1'], num_threads=3)
    target_trace_paths = [verifyta_path.bring_to_root('demo1-1.xtr'),
                          verifyta_path.bring_to_root('demo2-1.xtr')]
    for trace_path in target_trace_paths:
        assert os.path.exists(trace_path) is True
        os.remove(trace_path)


def test_easy_verify2():
    """_summary_
    """
    Verifyta().set_verifyta_path(verifyta_path.VERIFYTA_PATH)
    model_paths = [verifyta_path.bring_to_root('demo1.xml'),
                   verifyta_path.bring_to_root('demo2.xml'),
                   verifyta_path.bring_to_root('demo3.xml')]
    # ======== with trace_paths ========
    trace_paths = [verifyta_path.bring_to_root('t1.xtr'),
                   verifyta_path.bring_to_root('t2-.xml'),
                   verifyta_path.bring_to_root('t3-.xml')]
    res = Verifyta().easy_verify(model_paths, trace_path=trace_paths,
                                 verify_options='-t 1 -o 0', num_threads=3)
    print(res)
    # the third model do not have counter-example
    target_trace_paths = [verifyta_path.bring_to_root('t1-1.xtr'),
                          verifyta_path.bring_to_root('t2-1.xml')]
    for trace_path in target_trace_paths:
        assert os.path.exists(trace_path) is True
        os.remove(trace_path)
