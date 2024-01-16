import os
from pyuppaal.utap import utap_parser

""" Uppaal trace parser.
"""

def bring_to_root(file_name: str):
    root_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(root_dir, file_name)


def run(i):
    if_file = bring_to_root("test_utap.if")
    xtr_file = bring_to_root("test_utap.xtr")
    res = utap_parser(if_file, xtr_file, keep_if=True)
    return len(res)


def test_multiprocess():
    import multiprocessing as mp
    p = mp.Pool()
    res = p.map(run, range(10))
    assert len(res) == 10


def test_multithread():
    import multiprocessing.dummy as mp
    p = mp.Pool()
    res = p.map(run, range(10))
    assert len(res) == 10


if __name__ == '__main__':
    test_multiprocess()
    test_multithread()
