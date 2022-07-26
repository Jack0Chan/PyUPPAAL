# support typing str | List[str]
# https://github.com/microsoft/pylance-release/issues/513
from __future__ import annotations
import warnings
from typing import List
import os
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool
import functools
from multiprocessing import cpu_count
import platform

is_windows = platform.system() == 'Windows'

def check_is_verifyta_path_empty(func):
    """
    装饰器，用来在verifyta运行前检测路径是否被设置。
    """
    @functools.wraps(func)
    def checker_wrapper(*args, **kwargs):
        # 注意verifyta是singleton，因此可以直接用Verifyta()调用到唯一的实例
        if Verifyta()._verifyta_path:
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

        self._verifyta_path: str = ''

    @property
    def is_verifyta_empty(self):
        """
        check whether verifyta is set
        """
        if self._verifyta_path:
            return True
        else:
            return False

    @property
    def is_valid_verifyta_path(self):
        res = os.popen(f'{self._verifyta_path} -h').read()
        if 'Usage: verifyta [OPTION]... MODEL QUERY' in res:
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
        if '-h [ --help ]' in res:
            self._verifyta_path = verifyta_path
        else:
            example_info = "======== Example Paths ========" \
                           "\nWindows: absolute_path_to_uppaal\\bin-Windows\\verifyta.exe" \
                           "\nLinux  : absolute_path_to_uppaal/bin-Linux/verifyta" \
                           "\nmacOS  : absolute_path_to_uppaal/bin-Darwin/verifyta"
            raise ValueError(f"Invalid verifyta_path: {verifyta_path}.\n{example_info}")

    def get_verifyta_path(self):
        return self._verifyta_path

    @check_is_verifyta_path_empty
    def simple_verify(self, 
                      model_path: str | List[str], 
                      trace_path: str | List[str] = None, 
                      parallel: str=None, options = None):
        """
        Simple verification, return to the shortest diagnostic path. 
        Verify the model in model_path and save the verification results to trace_path
        
        model_path: str or str list, Model paths to be verified
        trace_path: str or str list, Trace paths to be saved
        parallel: str, select parallel method for accelerate verification, 
        None(default):run in sequence, 'process':use multiprocessing, 'threads': use multithreads.
        """
        # check trace_path is None
        if trace_path is None:
            if type(model_path) == str:
                trace_path = os.path.splitext(model_path)[0] + '.xtr'
            else:
                trace_path = [os.path.splitext(x)[0]+'.xtr' for x in model_path]

        # check model_path and trace_path type is same
        if type(model_path) != type(trace_path):
            error_info = f'type of model_path and trace_path are inconsistent\n'
            error_info += f'model_path: {type(model_path)}, trace_path:{type(trace_path)}.'
            raise TypeError(error_info)

        # check model_path is only one model, set parallel loop
        if type(model_path) != list:
            model_path, trace_path = [model_path], [trace_path]
            parallel = None
        
        # check model_path and trace_path len is same
        if len(model_path) != len(trace_path):
            error_info = f'length of model_path and trace_path are inconsistent'
            raise ValueError(error_info)
        
        # set uppaal environment variables
        cmd_env = 'set UPPAAL_COMPILE_ONLY=' if is_windows else "UPPAAL_COMPILE_ONLY="
        
        cmds = []
        for i in range(len(model_path)):
            model_i = model_path[i]
            trace_i = trace_path[i]
            # check model_path exist
            if not os.path.exists(model_i):
                error_info = f'model_path {model_i} not found.'
                raise FileNotFoundError(error_info)
            # check trace_path format
            if trace_i.endswith('.xml'):
                trace_i = trace_i.replace('.xml', '')
                if options is not None:
                    options_str = " ".join(options)
                    cmd = cmd_env+'&&'+f'{self._verifyta_path} -X {trace_i} {options_str} {model_i}'
                else:
                    cmd = cmd_env+'&&'+f'{self._verifyta_path} -t 1 -X {trace_i} {model_i}'
                cmds.append(cmd)
            elif trace_i.endswith('.xtr'):
                trace_i = trace_i.replace('.xtr', '')
                if options is not None:
                    options_str = " ".join(options)
                    cmd = cmd_env+'&&'+f'{self._verifyta_path} -f {trace_i} {options_str} {model_i}'
                else:
                    cmd = cmd_env+'&&'+f'{self._verifyta_path} -t 1 -f {trace_i} {model_i}'
                cmds.append(cmd)
            else:
                error_info = 'trace_path should end with ".xml" or ".xtr".'
                error_info += f' Currently trace_path = {trace_i}'
                raise ValueError(error_info)

        # select parallel method
        if parallel == None:
            return self.cmds_loop(cmds=cmds)
        if parallel == 'process':
            res = self.cmds_process(cmds=cmds)
        elif parallel == 'threads':
            res = self.cmds_threads(cmds=cmds)
        else:
            error_info = 'parallel should be "process" or "threads".'
            error_info += f' Currently parallel = {parallel}'
            raise ValueError(error_info)
        return res 

    # @check_is_verifyta_path_empty
    # def simple_verify_process(self, model_paths: List[str], trace_paths: List[str]):
    #     cmds = []
    #     for i in range(len(model_paths)):
    #         model_path = model_paths[i]
    #         trace_path = trace_paths[i]

    #         # check model_path exist
    #         if not os.path.exists(model_path):
    #             error_info = f'model_path {model_path} not found.'
    #             raise FileNotFoundError(error_info)

    #         # check trace_path format
    #         if trace_path.endswith('.xml'):
    #             trace_path = trace_path.replace('.xml', '')
    #             cmd = f'{self._verifyta_path} -t 1 -X {trace_path} {model_path}'
    #             cmds.append(cmd)
    #         elif trace_path.endswith('.xtr'):
    #             trace_path = trace_path.replace('.xtr', '')
    #             cmd = f'{self._verifyta_path} -t 1 -f {trace_path} {model_path}'
    #             cmds.append(cmd)
    #         else:
    #             error_info = 'trace_path should end with ".xml" or ".xtr".'
    #             error_info += f' Currently trace_path = {trace_path}'
    #             raise ValueError(error_info)

    #     return self.cmds_process(cmds, len(cmds))

    # @check_is_verifyta_path_empty
    # def simple_verify_threads(self, model_paths: List[str], trace_paths: List[str]):
    #     cmds = []
    #     for i in range(len(model_paths)):
    #         model_path = model_paths[i]
    #         trace_path = trace_paths[i]

    #         # check model_path exist
    #         if not os.path.exists(model_path):
    #             error_info = f'model_path {model_path} not found.'
    #             raise FileNotFoundError(error_info)

    #         # check trace_path format
    #         if trace_path.endswith('.xml'):
    #             trace_path = trace_path.replace('.xml', '')
    #             cmd = f'{self._verifyta_path} -t 1 -X {trace_path} {model_path}'
    #             cmds.append(cmd)
    #         elif trace_path.endswith('.xtr'):
    #             trace_path = trace_path.replace('.xtr', '')
    #             cmd = f'{self._verifyta_path} -t 1 -f {trace_path} {model_path}'
    #             cmds.append(cmd)
    #         else:
    #             error_info = 'trace_path should end with ".xml" or ".xtr".'
    #             error_info += f' Currently trace_path = {trace_path}'
    #             raise ValueError(error_info)

    #     return self.cmds_threads(cmds, len(cmds))


    @check_is_verifyta_path_empty
    def cmd(self, cmd: str):
        """
        run common command with cmd, you can easily ignore the verifyta path.
        return the running cmd and the command result
        """
        if self._verifyta_path not in cmd:
            cmd = f'{self._verifyta_path} {cmd}'
        return cmd, os.popen(cmd).read()

    @check_is_verifyta_path_empty
    def cmds_loop(self, cmds: List[str]):
        """
        run in sequence
        """
        return [self.cmd(tmp_cmd) for tmp_cmd in cmds]

    @check_is_verifyta_path_empty
    def cmds_process(self, cmds: List[str], num_process: int = None):
        """
        note that sometimes, multiprocess is not faster than single-process or multi-threads
        run a list of commands and return results
        if num_process is not given, it will run with num cpu cores
        if num_process is 1, it's better run with self.cmd
        return running cmds and associated result
        """
        if num_process == None:
            num_process = cpu_count()
        
        if num_process == 1:
            w = 'You are running with only 1 process, we recommend using Verifyta().cmd() method.'
            warnings.warn(w)
        p = Pool(min(num_process, cpu_count()))
        return p.map(self.cmd, cmds)

    @check_is_verifyta_path_empty
    def cmds_threads(self, cmds: List[str], num_threads: int = None):
        """
        run a list of commands and return results
        if num_threads is not given, it will run with num cpu cores * 2
        if num_threads is 1, it's better run with self.cmd
        return running cmds and associated result
        """
        if num_threads == None:
            num_threads = cpu_count()*2
        
        if num_threads == 1:
            w = 'You are running with only 1 thread, we recommend using Verifyta().cmd() method.'
            warnings.warn(w)
        p = ThreadPool(min(num_threads, cpu_count()*2))
        return p.map(self.cmd, cmds)

    @check_is_verifyta_path_empty
    def compile_to_if(self, model_path: str):
        """Compile model_path(model.xml) to generate a intermediate format file (model.if). 

        Args:
            model_path (str): str or str list, Model path to be verified

        Raises:
            FileNotFoundError: model_path not found.
            ValueError: model_path is not a xml format file.
        """
        if not os.path.exists(model_path):
            error_info = f'model_path {model_path} not found.'
            raise FileNotFoundError(error_info)
        file_path, file_ext = os.path.splitext(model_path)
        if_path = file_path + '.if'
        
        if file_ext != '.xml':
            error_info = f'model_path {model_path} should be xml format file.'
            raise ValueError(error_info)

        # set uppaal environment variables
        cmd_env = 'set UPPAAL_COMPILE_ONLY=1'
        cmd = cmd_env+"&&"+f'{self._verifyta_path} {model_path} > {if_path}'
        self.cmd(cmd=cmd)
        
        if not os.path.exists(if_path):
            error_info = f'if file {if_path} has not generated.'
            raise FileNotFoundError(error_info)
        return if_path

        