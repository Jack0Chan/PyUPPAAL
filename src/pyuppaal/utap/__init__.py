"""Uppaal trace parser.

Raises:
    ValueError: Command error with: {cmd}

Returns:
    str: Parsed trace string that is readable by human, and will be parsed into `SimTrace`.
"""
import subprocess
import platform
import os
import sys

# use absolute path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
TRACEER_FILE_DICT = {
    'Windows': os.path.join(CURRENT_DIR, 'tracer.exe'),
    'Linux': os.path.join(CURRENT_DIR, 'tracer_linux'),
    'Darwin': os.path.join(CURRENT_DIR, 'tracer_darwin')
}
TRACEER_FILE = TRACEER_FILE_DICT[platform.system()]

# platform
PLATFORM = platform.system()
USE_SHELL = PLATFORM == 'Windows'

def utap_parser(if_file: str, xtr_file: str, keep_if: bool = False) -> str:
    """Parse `.if` and associated `.xtr` file to readable trace string, which will be parsed into `SimTrace`.

    Args:
        if_file (str): `.if` file path.
        xtr_file (str): `.xtr` file path.
        keep_if (bool): whether keep `.if` file.

    Returns:
        str: Parsed trace string that is readable by human, and will be parsed into `SimTrace`.
    """

    cmd = [TRACEER_FILE, "--trace=string", "-t", xtr_file, "-i", if_file]

    try:
        cmd_res = subprocess.run(cmd, capture_output=True, shell=USE_SHELL, text=True, check=False)
        if cmd_res.stderr:
            err_info = f"Command error with: {' '.join(cmd)}:\n {cmd_res.stderr}"
            raise ValueError(err_info)
        if not keep_if and os.path.exists(if_file):
            os.remove(if_file)
        return cmd_res.stdout

    except Exception as e:
        raise ValueError(f"Command error with: {' '.join(cmd)}") from e
