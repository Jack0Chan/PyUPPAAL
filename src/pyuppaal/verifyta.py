"""verifyta
"""
# support typing str | List[str]
# https://github.com/microsoft/pylance-release/issues/513
from __future__ import annotations

from typing import List
from multiprocessing.dummy import Pool as ThreadPool
import functools
import platform
import os


def check_is_verifyta_path_empty(func):
    """====该函数后续会删除，希望不要每次都检测====
    装饰器, 用来在verifyta运行前检测路径是否被设置。
    """
    @functools.wraps(func)
    def checker_wrapper(*args, **kwargs):
        # 注意verifyta是singleton，因此可以直接用Verifyta()调用到唯一的实例
        if Verifyta().verifyta_path:
            return func(*args, **kwargs)
        else:
            error_info = 'Verifyta path is not set.'
            error_info += ' Please use "pyuppaal.set_verifyta_path(verifyta_path: str)" to set the path of verifyta.'
            raise ValueError(error_info)
    return checker_wrapper


class Verifyta:
    """This is a singleton class that help to use `verifyta` command.
    """
    # make singleton
    __instance = None
    __is_first_init = True

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self):
        # make singleton
        if not self.__is_first_init:
            return
        self.__is_first_init = False

        self.__verifyta_path: str = None
        self.__is_windows: bool = platform.system() == 'Windows'

    @property
    def verifyta_path(self) -> str:
        """Get current verifyta path.

        Returns:
            str: current verifyta path.
        """
        return self.__verifyta_path

    def __is_valid_verifyta_path(self, verifyta_path: str) -> bool:
        """Check whether the verifyta path is valid.
        Checking steps:
        1. run cmd with `verifyta_path -h`;
        2. check whether `'-h [ --help ]' in res`.

        Args:
            verifyta_path (str): _description_

        Returns:
            bool: _description_
        """
        cmd = f'{verifyta_path} -h'
        res = os.popen(cmd).read()
        return '-h [ --help ]' in res

    def set_verifyta_path(self, verifyta_path: str) -> bool:
        """Set the verifyta path before using pyuppaal.
        This function will check the validation of the `verifyta_path` automatically by the following steps:

        1. run cmd with `verifyta_path -h`;
        2. check whether `'-h [ --help ]' in res`.
        
        Example paths:

        1. Windows: path_to_uppaal\\bin-Windows\\verifyta.exe
        2. Linux  : path_to_uppaal/bin-Linux/verifyta
        3. macOS  : path_to_uppaal/bin-Darwin/verifyta

        Args:
            verifyta_path (str): (absolute) path to `verifyta`

        Raises:
            ValueError: if verifyta_path is invalid, it will raise an error and tips to help.

        Returns:
            bool: return `True` if verifyta_path is successfully set.
        """

        if self.__is_valid_verifyta_path(verifyta_path):
            self.__verifyta_path = verifyta_path
            return True
        else:
            example_info = "======== Example Paths ========" \
                           "\nWindows: absolute_path_to_uppaal\\bin-Windows\\verifyta.exe" \
                           "\nLinux  : absolute_path_to_uppaal/bin-Linux/verifyta" \
                           "\nmacOS  : absolute_path_to_uppaal/bin-Darwin/verifyta"
            raise ValueError(
                f"Invalid verifyta_path: {verifyta_path}.\n{example_info}")

    @check_is_verifyta_path_empty
    def cmd(self, cmd: str) -> str:
        """Run common command with cmd, you can easily ignore the verifyta path.

        Args:
            cmd (str): command to run.

        Returns:
            str: the output of the input command.
        """
        if self.__verifyta_path not in cmd:
            cmd = f'{self.__verifyta_path} {cmd}'
        return os.popen(cmd).read()

    # @check_is_verifyta_path_empty 调用了self.cmd，所以不需要加
    def cmds(self, cmds: List[str], num_threads: int = 1) -> List[str]:
        """Run commands with terminal.

        Args:
            cmds (List[str]): commands to run
            num_threads (int, optional): use multi-threads if is greater than 1. Defaults to 1.

        Raises:
            ValueError: Number of threads should ≥ 1.

        Returns:
            List[str]: return values of each command.
        """
        # 检测报错
        num_threads = int(num_threads)
        if num_threads < 1:
            raise ValueError("Number of threads should ≥ 1.")
        elif num_threads == 1:
            return [self.cmd(tmp_cmd) for tmp_cmd in cmds]
        else:
            p = ThreadPool(num_threads)
            return p.map(self.cmd, cmds)

    @check_is_verifyta_path_empty
    def _compile_to_if(self, model_path: str) -> str:
        """Compile the `.xml` model_path to a `.if` file and return the path to `.if` file.

        Args:
            model_path (str): `.xml` model file.

        Raises:
            FileNotFoundError: `model_path` not found.
            ValueError: `model_path` is not a `.xml`.
            FileNotFoundError: _description_

        Returns:
            str: path to `.if` file.
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
        # 设置命令行环境保证uppaal能够产生正确的.if文件，后半部分保证文件以UTF-8编码，进而保证lf结尾。
        cmd_env = "set UPPAAL_COMPILE_ONLY=1 && set PSDefaultParameterValues['Out-File:Encoding']='Default'"
        # cmd = cmd_env+"&&"+f'{self.__verifyta_path} {model_path} > {if_path}'
        cmd = f'{cmd_env} && {self.__verifyta_path} {model_path} > {if_path}'
        self.cmd(cmd=cmd)
        if not os.path.exists(if_path):
            error_info = f'if file {if_path} has not generated.'
            raise FileNotFoundError(error_info)
        return if_path

    @check_is_verifyta_path_empty
    def compile_to_if(self, model_path: str) -> str:
        """Compile the `.xml` model_path to a `.if` file and return the content of the `.if` file.

        Args:
            model_path (str): `.xml` model file.

        Raises:
            FileNotFoundError: `model_path` not found.
            ValueError: `model_path` is not a `.xml`.
            FileNotFoundError: _description_

        Returns:
            str: path to `.if` file.
        """
        if not os.path.exists(model_path):
            error_info = f'model_path {model_path} not found.'
            raise FileNotFoundError(error_info)
        file_path, file_ext = os.path.splitext(model_path)

        if file_ext != '.xml':
            error_info = f'model_path {model_path} should be xml format file.'
            raise ValueError(error_info)

        # set uppaal environment variables
        # 设置命令行环境保证uppaal能够产生正确的.if文件，后半部分保证文件以UTF-8编码，进而保证lf结尾。
        cmd_env = "set UPPAAL_COMPILE_ONLY=1 && set PSDefaultParameterValues['Out-File:Encoding']='Default'"
        cmd = f'{cmd_env} && {self.__verifyta_path} {model_path}'
        if_str = self.cmd(cmd=cmd)
        return if_str

    # @check_is_verifyta_path_empty 调用了self.cmd，所以不需要加
    def verify(self,
               model_path: str | List[str],
               verify_options: str | List[str] = None,
               num_threads: int = 1) -> List[str]:
        """Verify models and return the verify results as list.
        This is designed for advanced UPPAAL user.
        If you want to save a `.xtr` or `.xml`(DBM) path, you may want to check `Verifyta().easy_verify()`.
        WARNING: Note that `-f xx.xtr` or `-X xx.xml` should be used together with `-t` options, otherwise you may fail to save the path files.
        
        Examples:       
            >>> Verifyta().verify('test1.xml')
            >>> Verifyta().verify(['test1.xml', 'test2.xml'], verify_options = '-t 1 -o 0')
            >>> Verifyta().verify(['test1.xml', 'test1.xml'], 
            >>>     verify_options = ['-t 1 -o 0', '-t 2 -o 0'])
            >>> # if you surely want to generate a trace file with Verifyta().verify()
            >>> # you should not add `.xtr` at the end of `xtr_trace`,
            >>> # or `.xml` at the end of `xtr_trace`
            >>> Verifyta().verify(['test1.xml', 'test1.xml'], 
            >>>     verify_options = ['-f xtr_trace -t 1 -o 0', '-X xml_trace -t 2 -o 0'], 
            >>>     num_threads=2)
            >>>
            >>> # return example
            >>> # Options for the verification: 
            >>> #    Generating shortest trace
            >>> #    Search order is breadth first
            >>> #    Using conservative space optimisation
            >>> #    Seed is 1665658616
            >>> #    State space representation uses minimal constraint systems
            >>> #    Verifying formula 1 at /nta/queries/query[1]/formula
            >>> #   -- Formula is satisfied.
            >>> # Options for the verification: 
            >>> #   Generating shortest trace  
            >>> #   Search order is breadth first
            >>> #   Using conservative space optimisation
            >>> #   Seed is 1665658616  
            >>> #   State space representation uses minimal constraint systems
            >>> #   Verifying formula 1 at /nta/queries/query[1]/formula
            >>> #   -- Formula is NOT satisfied.

        Args:
            model_path (str | List[str]): model paths to be verified.
            verify_options (str | List[str], optional): verify options that are proveded by `verifyta`, and you can get details by run `verifyta -h` in your terminal.
                If `verify_options` is provided as a single `string`, all the models will be verified with the same options. Defaults to None.
            num_threads (int, optional): use multi-threads if is greater than 1. Defaults to 1.

        Raises:
            ValueError: _description_
            TypeError: _description_
            ValueError: _description_
            FileNotFoundError: _description_
            ValueError: _description_

        Returns:
            List[str]: terminal verify results for each `.xml` model. 
        """
        num_threads = int(num_threads)
        if num_threads < 1:
            raise ValueError(
                f"Number of threads should ≥ 1. Current value: {num_threads}.")

        # check model_path is only one model
        if isinstance(model_path, str):
            model_path = [model_path]
        len_model_path = len(model_path)

        # check verify_options is only one
        if verify_options is None:
            verify_options = ['' for _ in range(len_model_path)]
        elif isinstance(verify_options, str):
            verify_options = [verify_options for _ in range(len_model_path)]
        else:
            pass
        len_verify_options = len(verify_options)

        # check consistency
        if len_model_path != len_verify_options:
            error_info = f'Length of model_path and verify_options are inconsistent. Current values:\n' \
                         f'model_path: {model_path}, \nverify_options: {verify_options}.'
            raise ValueError(error_info)

        # set uppaal environment variables
        # 因为生成.if的时候UPPAAL_COMPILE_ONLY=1, 这里要改回来。但是改成啥都不对，所以就啥都不加，然后就对了。。。
        # 啥都不加是@yhc试出来的
        cmd_env = 'set UPPAAL_COMPILE_ONLY=' if self.__is_windows else "UPPAAL_COMPILE_ONLY="

        cmds = []
        for i in range(len_model_path):
            model_i = model_path[i]
            verify_options_i = verify_options[i]
            # check model_path exist
            if not os.path.exists(model_i):
                error_info = f'model_path {model_i} not found.'
                raise FileNotFoundError(error_info)
            # 构造命令
            cmd = cmd_env+'&&' + \
                f'{self.__verifyta_path} {model_i} {verify_options_i}'
            cmds.append(cmd)
        # print(cmds)
        res = self.cmds(cmds=cmds, num_threads=num_threads)
        # print(res)
        return res

    # @check_is_verifyta_path_empty 调用了self.cmd，所以不需要加
    def easy_verify(self,
                    model_path: str | List[str],
                    trace_path: str | List[str] = None,
                    verify_options: str | List[str] = "-t 1",
                    num_threads: int = 1) -> List[str]:
        """Verify models and return the verify results as list.
        For `trace_path` param, both `.xtr` and `.xml`(DBM) files are supported.
        WARNING: `-t` option must be set for `verify_options`, which is set by default `verify_options = '-t 1'`(shortest), otherwise counter-example file may not be created.

        Examples:       
            >>> Verifyta().set_verifyta_path(VERIFYTA_PATH)
            >>> model_paths = [os.path.join(ROOT_DIR, 'demo1.xml'),
            >>>         os.path.join(ROOT_DIR, 'demo2.xml'),
            >>>         os.path.join(ROOT_DIR, 'demo3.xml')]
            >>> trace_paths = [os.path.join(ROOT_DIR, 't1.xtr'),
            >>>         os.path.join(ROOT_DIR, 't2-.xml'),
            >>>         os.path.join(ROOT_DIR, 't3-.xml')]
            >>> Verifyta().easy_verify(model_paths, 
            >>>         verify_options=['-t 1 -o 0', '-t 2 -o 0', '-t 2 -o 1'], 
            >>>         num_threads=3)
            >>> Verifyta().easy_verify(model_paths, trace_path=trace_paths, 
            >>>         verify_options='-t 1 -o 0', num_threads=3)        

        Args:
            model_path (str | List[str]): model paths to be verified.
            trace_path (str | List[str], optional): target trace paths, both `.xtr` and `.xml`(DBM) are supported. 
                Defaults to None, which will create `.xtr` path.
            verify_options (str | List[str], optional): verify options that are proveded by `verifyta`, and you can get details by run `verifyta -h` in your terminal.
                If `verify_options` is provides as a single string, all the models will be verified with the same options. Defaults to '-t 1', returning the shortest trace.
            num_threads (int, optional): use multi-threads if is greater than 1. Defaults to 1.

        Returns:
            List[str]: terminal verify results for each `.xml` model.
        """
        # num_threads will be checked in self.verify()

        # check whether trace_path is None
        if trace_path is None:
            if isinstance(model_path, str):
                trace_path = os.path.splitext(model_path)[0] + '.xtr'
            else:
                trace_path = [os.path.splitext(
                    x)[0]+'.xtr' for x in model_path]

        # check model_path is only one model, set parallel loop
        if isinstance(model_path, str):
            model_path = [model_path]
        if isinstance(trace_path, str):
            trace_path = [trace_path]

        len_model_path = len(model_path)
        len_trace_path = len(trace_path)
        # check model_path and trace_path len is same
        if len_model_path != len_trace_path:
            error_info = f'Length of model_path and trace_path are inconsistent\n' \
                         f'model_path: {len_model_path}, trace_path: {len_trace_path}'
            raise ValueError(error_info)

        if verify_options is None:
            verify_options = "-t 1"
        if isinstance(verify_options, str):
            verify_options = [verify_options for _ in range(len_model_path)]

        options = []
        # 构造options然后让self.verify()处理任务
        for i in range(len_model_path):
            trace_i = trace_path[i]
            verify_options_i = verify_options[i]
            if '-t ' not in verify_options_i:
                verify_options[i] += ' -t 1'
            # model_path existence will be checked in self.verity()
            # check trace_path format
            if trace_i.endswith('.xml'):
                option = f"-X {trace_i.replace('.xml', '')} {verify_options_i}"
                options.append(option)
            elif trace_i.endswith('.xtr'):
                option = f"-f {trace_i.replace('.xtr', '')} {verify_options_i}"
                options.append(option)
            else:
                error_info = f'trace_path should end with ".xml" or ".xtr", ' \
                             f'current trace_path = {trace_i}.'
                raise ValueError(error_info)
        return self.verify(model_path=model_path, verify_options=options, num_threads=num_threads)
