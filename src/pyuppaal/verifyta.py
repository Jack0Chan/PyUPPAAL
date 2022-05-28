import time
import warnings
from typing import List
import os
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool


class Verifyta:
    """
    uppaal commandline tools
    """
    # make singleton
    _instance = None
    _is_first_init = True

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self):
        # make singleton
        if not self._is_first_init:
            return
        self._is_first_init = False

        self.verifyta_path: str = ''

    def set_verifyta_path(self, verifyta_path: str):
        """
        设置verifyta_path
        verifyta_path: str, 用户指定的verifyta_path

        设置时会验证verifyta path的合法性，方法如下：
        通过命令行调用f'{verifyta_path} -h'，查看返回内容是否包含 'Usage: verifyta [OPTION]... MODEL QUERY'
        """
        res = os.popen(f'{verifyta_path} -h').read()
        if 'Usage: verifyta [OPTION]... MODEL QUERY' in res:
            self.verifyta_path = verifyta_path
        else:
            example_info = "======== Example Paths ========" \
                           "\nWindows: absolute_path_to_uppaal\\bin-Windows\\verifyta.exe" \
                           "\nLinux  : absolute_path_to_uppaal/bin-Linux/verifyta" \
                           "\nmacOS  : absolute_path_to_uppaal/bin-Darwin/verifyta"
            raise ValueError(f"Invalid verifyta_path: {verifyta_path}.\n{example_info}")

    def simple_verify(self, model_path: str, trace_path: str):
        """
        简单验证，返回最短诊断路径（shortest path）
        model_path: str, 待验证的模型路径
        trace_path: str, 需要保存的xml path文件路径
        验证模型，并将验证结果的xml文件保存到trace_path中
        """
        trace_path = trace_path.replace('.xml', '')
        cmd = f'{self.verifyta_path} -t 1 -X {trace_path} {model_path}'
        res = os.popen(cmd).read()
        return res

    def cmd(self, cmd: str):
        """
        run common command with cmd, you can easily ignore the verifyta path.
        return the running cmd and the command result
        """
        if self.verifyta_path not in cmd:
            cmd = f'{self.verifyta_path} {cmd}'
        return cmd, os.popen(cmd).read()

    def cmds_process(self, cmds: List[str], num_process: int = None):
        """
        note that sometimes, multiprocess is not faster than single-process or multi-threads
        run a list of commands and return results
        if num_process is not given, it will run with num cpu cores
        if num_process is 1, it's better run with self.cmd
        return running cmds and associated result
        """
        if num_process == 1:
            w = 'You are running with only 1 process, we recommend using self.cmd() method.'
            warnings.warn(w)
        p = Pool(num_process)
        return p.map(self.cmd, cmds)

    def cmds_threads(self, cmds: List[str], num_threads: int = None):
        """
        run a list of commands and return results
        if num_threads is not given, it will run with num cpu cores
        if num_threads is 1, it's better run with self.cmd
        return running cmds and associated result
        """
        if num_threads == 1:
            w = 'You are running with only 1 thread, we recommend using self.cmd() method.'
            warnings.warn(w)
        p = ThreadPool(num_threads)
        return p.map(self.cmd, cmds)


def test():
    v = Verifyta()
    v.set_verifyta_path('/Users/chenguangyao/Downloads/uppaal64-4.1.26/bin-Darwin/verifyta')
    print('set up verifyta_path: ', v.verifyta_path)
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
