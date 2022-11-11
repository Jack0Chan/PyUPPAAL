"""_summary_
"""
from __future__ import annotations
from typing import List
from .verifyta import Verifyta
from .umodel import UModel
from .iTools import Mermaid


def set_verifyta_path(verifyta_path: str):
    """Set verifyta path, and you will get tips if `verifyta_path` is invalid.
    This function will check whether `verifyta_path` is valid by following steps:
    1. run '{verifyta_path} -h' with cmd
    2. check whether '-h [ --help ]' is in the result

    Args:
        verifyta_path (str): absolute path to `verifyta`
    """
    Verifyta().set_verifyta_path(verifyta_path)


def easy_verify(model_path: str | List[str],
                trace_path: str | List[str],
                verify_options: str = "-t 1",
                num_threads=1) -> List[str]:
    """Easy verification with default options, return to the shortest diagnostic path.
    Verify the model in model_path and save the verification results to trace_path.

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
    return Verifyta().easy_verify(model_path, trace_path, verify_options, num_threads)

def get_communication_graph(model_path: str, save_path=None, is_beautify=True) -> Mermaid:
    """Get the communication graph of the UPPAAL model, and return a `Mermaid` instance.

    Args:
        model_path (str): path to the model.
        save_path (_type_, optional): `<.md | .svg | .pdf | .png>`, the path to save the file. Defaults to None.
        is_beautify (bool, optional): whether beautify the mermaid file by merging edges. Defaults to True.

    Returns:
        Mermaid: _description_
    """
    umod = UModel(model_path)
    return umod.get_communication_graph(save_path, is_beautify)


def verify(model_path: str | List[str],
           verify_options: str | List[str] = None,
           num_threads: int = 1) -> List[str]:
    """Verify models and return the verify results as list. This is designed for advanced UPPAAL user. 
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
    return Verifyta().verify(model_path, verify_options, num_threads)


def cmd(cmd: str) -> str:
    """Run common command with cmd, you can easily ignore the verifyta path.

    Args:
        cmd (str): command to be run by verifyta.

    Returns:
        str: the running cmd and the command result
    """
    return Verifyta().cmd(cmd)


def cmds(cmds: List[str], num_threads: int = 1) -> List[str]:
    """Run commands with terminal.

    Args:
        cmds (List[str]): commands to run
        num_threads (int, optional): use multi-threads if is greater than 1. Defaults to 1.

    Raises:
        ValueError: Number of threads should ≥ 1.

    Returns:
        List[str]: return values of each command.
    """
    return Verifyta().cmds(cmds, num_threads)
