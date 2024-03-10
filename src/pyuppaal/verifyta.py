"""verifyta
"""
# support typing str | List[str]
# https://github.com/microsoft/pylance-release/issues/513
from __future__ import annotations

import platform
import os
import subprocess
from typing import List


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

        self.__verifyta_version: int = None

        self.__operating_system: str = self.get_env()

    @property
    def verifyta_path(self) -> str:
        """Get current verifyta path.

        Returns:
            str: current verifyta path.
        """
        return self.__verifyta_path

    @staticmethod
    def get_env() -> str:  # operation system

        operating_system = platform.system()

        if operating_system == 'Windows':
            return 'Windows'
        elif operating_system == 'Linux':
            return 'Linux'
        elif operating_system == 'Darwin':
            return 'Darwin'
        else:
            raise ValueError(f'Unknown operating system: {operating_system}')

    def get_uppaal_version(self) -> int:

        res = self.cmd(f'{self.__verifyta_path} -v')
        index = res.split(' ').index('UPPAAL')  # Version is the word after UPPAAL
        return int(res.split(' ')[index + 1].split('.')[0])

    def set_verifyta_path(self, verifyta_path: str) -> None:
        """Set the verifyta path before using pyuppaal.
        This function will check the validation of the `verifyta_path` automatically by the following steps:

        1. run cmd with `verifyta_path -v`;
        2. check whether `'UPPAAL' in res`.

        Example paths:

        1. Windows: path_to_uppaal\\bin-Windows\\verifyta.exe
        2. Linux  : path_to_uppaal/bin-Linux/verifyta
        3. macOS  : path_to_uppaal/bin-Darwin/verifyta

        Args:
            verifyta_path (str): (absolute) path to `verifyta`

        Raises:
            ValueError: if verifyta_path is invalid.

        Returns:
            None
        """
        # check validation of verifyta
        cmd = f'{verifyta_path} -v'

        cmd_res = subprocess.run(cmd, shell=True, capture_output=True)
        # if cmd_res.returncode == 0:
        #     pass
        # else:
        #     # 如果报错里面有 \xcf\xB5\xCD\xB3，是中文gbk系统的问题，大概率解码后是"路径不存在"。
        #     # if "\\xcf\\xb5\\xcd\\xb3" in str(cmd_res):
        #     #     print("Encounter Encode Error. Probable means 'File Not Found' in your language.")
        #     raise ValueError(f"Verifyta Not Found!. \nCommand: {cmd}\nErr: {str(cmd_res.stderr)}")

        # UPPAAL5 will get noneType in stderr.
        if cmd_res.stderr is not None:
            cmd_res = str(cmd_res.stdout + cmd_res.stderr)
        else:
            cmd_res = str(cmd_res.stdout)

        if 'UPPAAL' in cmd_res:
            self.__verifyta_path = verifyta_path
            self.__verifyta_version = self.get_uppaal_version()
        else:
            example_info = "======== Example Paths ========" \
                           "\nWindows: absolute_path_to_uppaal\\bin-Windows\\verifyta.exe" \
                           "\nLinux  : absolute_path_to_uppaal/bin-Linux/verifyta" \
                           "\nmacOS  : absolute_path_to_uppaal/bin-Darwin/verifyta"
            raise ValueError(
                f"Invalid verifyta_path: {verifyta_path}.\n{example_info} \nVerifyta Not Found!.")

    def cmd(self, cmd: str) -> str:
        """Run common command with cmd, you can easily ignore the verifyta path.

        Args:
            cmd (str): command to run.

        Raises:
            ValueError: if verifyta_path is not set.
            ValueError: if cmd got stderr and not as expected.

        Returns:
            str: the output of the input command.
        """
        # check for validation of verifyta path
        if not Verifyta().verifyta_path:
            error_info = 'Verifyta path is not set.'
            error_info += ' Please use "pyuppaal.set_verifyta_path(verifyta_path: str)" to set the path of verifyta.'
            raise ValueError(error_info)

        # Run the command and check for errors. Use shell because we set env var and && is used.
        # macos and windows use shell, linux not use
        cmd_res = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=False)

        if cmd_res.stderr is not None and cmd_res.stderr != '':
            if "Writing example trace to" in cmd_res.stderr:
                pass
            elif "Writing counter example" in cmd_res.stderr:
                pass
            elif cmd_res.stdout is not None and "Showing" in cmd_res.stdout:
                # cmd:
                #   set UPPAAL_COMPILE_ONLY=&&c:\users\taco\documents\github\pyuppaal_hcps\src\pyuppaal\../../bin/uppaal64-4.1.26\bin-Windows/verifyta.exe C:\Users\Taco\Documents\GitHub\pyuppaal_hcps\src\test_unit\demo1.xml -t 1 -o 0
                # stdout:
                #   Options for the verification:
                #   Generating shortest trace
                #   Search order is breadth first
                #   Using conservative space optimisation
                #   Seed is 1700202518
                #   State space representation uses minimal constraint systems
                #
                # Verifying formula 1 at /nta/queries/query[1]/formula
                #  -- Formula is NOT satisfied.
                # Showing counter example.

                # stderr:
                # State:
                # ( P1.A )
                # P1.t=0 #depth=0

                # Transitions:
                #   P1.A->P1.C { 1, tau, t := 0 }

                # State:
                # ( P1.C )
                # P1.t=0 #depth=1
                pass
            elif "[warning] Strict invariant." in cmd_res.stderr:
                # TODO: Maybe change the input/observation clk name to avoid this.
                pass
            else:
                if "license key is not set" in cmd_res.stderr:
                    raise ValueError(
                        f"UPPAAL License Not set. Register on `https://uppaal.veriaal.dk/academic.html` and set the key via `verifyta --lease 168 --key YOUR_LICENSE_KEY`.\n Note: You may need to modify `verifyta` to the real verifyta path. \n cmd: {''.join(cmd)}\nErr: {cmd_res.stderr}")
                if "Failed to retrieve" in cmd_res.stderr:
                    raise ValueError(f"UPPAAL License Error. Check Internect connection and try again may help. \n cmd: {''.join(cmd)}\nErr: {cmd_res.stderr}")
                raise ValueError(f"Command: {''.join(cmd)}\nErr: {cmd_res.stderr}")
        res = cmd_res.stderr

        if cmd_res.stdout is not None:
            res = res + cmd_res.stdout

        return res

    def compile_to_if(self, model_path: str) -> str:
        """Compile the `.xml` model_path to a `.if` file and return the content of the `.if` file.

        Args:
            model_path (str): `.xml` model file.

        Raises:
            FileNotFoundError: `model_path` not found.
            ValueError: `model_path` is not a `.xml`.

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

        if_path = file_path + '.if'
        # set uppaal environment variables
        # 设置命令行环境保证uppaal能够产生正确的.if文件，后半部分保证文件以UTF-8编码，进而保证lf结尾。
        if self.__operating_system == "Windows":
            cmd_env = "set UPPAAL_COMPILE_ONLY=1 && set PSDefaultParameterValues['Out-File:Encoding']='Default'"
            cmd = f'{cmd_env} && {self.__verifyta_path} {model_path} > {if_path}'
        else:
            cmd_env = "UPPAAL_COMPILE_ONLY=1"
            cmd = f'{cmd_env} {self.__verifyta_path} {model_path} > {if_path}'
        self.cmd(cmd=cmd)

        return if_path

    def verify(self, model_path: str, trace_path: str = None, verify_options: str = "-t 1", keep_tmp_file=True) -> str:
        """
        Verify model and return the verify result as list.
        This is designed for advanced UPPAAL user.

        Verify models and return the verify results as list.
        For `trace_path` param, both `.xtr` and `.xml`(DBM) files are supported.
        WARNING: Note that `-f xx.xtr` or `-X xx.xml` should be used together with `-t` options, otherwise you may fail to save the path files.
        WARNING: `-t` option must be set for `verify_options`, which is set by default `verify_options = '-t 1'`(shortest), otherwise counter-example file may not be created.

        Examples:
            >>> Verifyta().set_verifyta_path(VERIFYTA_PATH)
            >>> model_path = os.path.join(ROOT_DIR, 'demo1.xml')
            >>> trace_path = os.path.join(ROOT_DIR, 't1.xtr')
            >>> Verifyta().verify(model_path, trace_path=trace_path, verify_options='-t 1 -o 0')

        Args:
            model_path (str): model path to be verified.
            trace_path (str, optional): target trace path, both `.xtr` and `.xml`(DBM) are supported. 
                Defaults to None, which will create `.xtr` path.
            verify_options (str, optional): verify options that are proveded by `verifyta`, and you can get details by run `verifyta -h` in your terminal.
                Defaults to '-t 1', returning the shortest trace.

        Raises:
            ValueError: if tracer file is not `xml` or `xtr`.

        Returns:
            str: terminal verify results for `.xml` model.
        """

        if not isinstance(model_path, str):
            raise ValueError(f'List input is not supported anymore, please use for loop. mdel_path: {model_path}, verify_options: {verify_options}')

        if verify_options is None:
            verify_options = "-t 1"

        # 构造options然后让self.verify()处理任务
        if '-t ' not in verify_options:
            verify_options += ' -t 1'
        # model_path existence will be checked in self.verity()
        # check trace_path format
        option = ''

        # check whether trace_path is None
        if Verifyta().__verifyta_version == 4:
            if trace_path is None:
                trace_path = os.path.splitext(model_path)[0] + '.xtr'

            if trace_path.endswith('.xml'):
                option = f"-X {trace_path.replace('.xml', '')} {verify_options}"
            elif trace_path.endswith('.xtr'):
                option = f"-f {trace_path.replace('.xtr', '')} {verify_options}"
            else:
                error_info = f'trace_path should end with ".xml" or ".xtr", current trace_path = {trace_path}.'
                raise ValueError(error_info)
        else:
            if trace_path is None:
                trace_path = os.path.splitext(model_path)[0] + '_xtr'
                option = f"-f {trace_path} {verify_options}"
            elif trace_path.endswith('.xml'):
                option = f"-X {trace_path.replace('.xml', '_xtr')} {verify_options}"
            elif trace_path.endswith('.xtr'):
                option = f"-f {trace_path.replace('.xtr', '_xtr')} {verify_options}"
            elif trace_path.endswith("_xtr"):
                option = f"-f {trace_path} {verify_options}"
            else:
                error_info = f'trace_path should end with ".xml" or ".xtr", current trace_path = {trace_path}.'
                raise ValueError(error_info)

        # check model_path exist
        if not os.path.exists(model_path):
            error_info = f'model_path {model_path} not found.'
            raise FileNotFoundError(error_info)

        # set uppaal environment variables
        cmd_env = 'set UPPAAL_COMPILE_ONLY=' if (self.__operating_system == "Windows") else "UPPAAL_COMPILE_ONLY="

        # 构造命令
        cmd = f'{cmd_env}&&{self.__verifyta_path} {model_path} {option}'
        res = self.cmd(cmd)

        # remove tmp file
        if not keep_tmp_file:
            trace_path = trace_path.replace('.xtr', '-1.xtr').replace('_xtr', '_xtr-1')
            if os.path.exists(trace_path):
                os.remove(trace_path)

        return res
