from pyuppaal import Verifyta
import time


def test():
    Verifyta()._verifyta_path = '666'
    print('Verifyta().verifyta_path:', Verifyta()._verifyta_path)

    v = Verifyta()
    print('         v.verifyta_path:', v._verifyta_path)

    v.set_verifyta_path('/Users/chenguangyao/Downloads/uppaal64-4.1.26/bin-Darwin/verifyta')
    print('set up verifyta_path: ', v._verifyta_path)
    l_cmd = ['-h' for _ in range(1)]

    t = time.time()
    v.cmds_process(l_cmd)
    print('time with multi-process: ', time.time() - t)

    t = time.time()
    v.cmds_process(l_cmd, num_process=1)
    print('time with 1-process: ', time.time() - t)

    t = time.time()
    v.cmds_threads(l_cmd)
    print('time with multi-threads: ', time.time() - t)

    t = time.time()
    v.cmds_threads(l_cmd, num_threads=1)
    print('time with 1-thread: ', time.time() - t)

    t = time.time()
    for cmd in l_cmd:
        v.cmd(cmd)
    print('time without multi-process: ', time.time() - t)


if __name__ == '__main__':
    test()
