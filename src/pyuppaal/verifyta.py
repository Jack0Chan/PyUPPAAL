import warnings
from typing import List
import os
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool
import functools


def check_is_verifyta_path_empty(func):
    """
    装饰器，用来在verifyta运行前检测路径是否被设置。
    """
    @functools.wraps(func)
    def checker_wrapper(*args, **kwargs):
        # 注意verifyta是singleton，因此可以直接用Verifyta()调用到唯一的实例
        if Verifyta().verifyta_path:
            return func(*args, **kwargs)
        else:
            error_info = 'Verifyta path is not set.'
            error_info += ' Please use "Verifyta().set_verifyta_path(verifyta_path: str)" to set the path of verifyta.'
            raise ValueError(error_info)
    return checker_wrapper


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

    @property
    def is_verifyta_empty(self):
        """
        check whether verifyta is set
        """
        if self.verifyta_path:
            return True
        else:
            return False

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

    @check_is_verifyta_path_empty
    def simple_verify(self, model_path: str, trace_path: str):
        """
        简单验证，返回最短诊断路径（shortest path）
        model_path: str, 待验证的模型路径
        trace_path: str, 需要保存的xml or xtr path文件路径
        验证模型，并将验证结果的xml文件保存到trace_path中
        """
        # check trace_path format
        if trace_path.endswith('.xml'):
            trace_path = trace_path.replace('.xml', '')
            cmd = f'{self.verifyta_path} -t 1 -X {trace_path} {model_path}'
            res = os.popen(cmd).read()
        elif trace_path.endswith('.xtr'):
            # trace_path = trace_path.replace('.xml', '')
            # cmd = f'{self.verifyta_path} -t 1 -X {trace_path} {model_path}'
            # res = os.popen(cmd).read()
            raise NotImplementedError()
            res = ''
        else:
            error_info = 'trace_path should end with ".xml" or ".xtr".'
            error_info += f' Currently trace_path = {trace_path}'
            raise ValueError(error_info)
        return res

    @check_is_verifyta_path_empty
    def cmd(self, cmd: str):
        """
        run common command with cmd, you can easily ignore the verifyta path.
        return the running cmd and the command result
        """
        if self.verifyta_path not in cmd:
            cmd = f'{self.verifyta_path} {cmd}'
        return cmd, os.popen(cmd).read()

    @check_is_verifyta_path_empty
    def cmds_process(self, cmds: List[str], num_process: int = None):
        """
        note that sometimes, multiprocess is not faster than single-process or multi-threads
        run a list of commands and return results
        if num_process is not given, it will run with num cpu cores
        if num_process is 1, it's better run with self.cmd
        return running cmds and associated result
        """
        if num_process == 1:
            w = 'You are running with only 1 process, we recommend using Verifyta().cmd() method.'
            warnings.warn(w)
        p = Pool(num_process)
        return p.map(self.cmd, cmds)

    @check_is_verifyta_path_empty
    def cmds_threads(self, cmds: List[str], num_threads: int = None):
        """
        run a list of commands and return results
        if num_threads is not given, it will run with num cpu cores
        if num_threads is 1, it's better run with self.cmd
        return running cmds and associated result
        """
        if num_threads == 1:
            w = 'You are running with only 1 thread, we recommend using Verifyta().cmd() method.'
            warnings.warn(w)
        p = ThreadPool(num_threads)
        return p.map(self.cmd, cmds)
