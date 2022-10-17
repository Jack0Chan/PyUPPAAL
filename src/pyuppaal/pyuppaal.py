from __future__ import annotations
from .verifyta import Verifyta
from .tracer import Tracer
from .umodel import UModel
from .datastruct import TimedActions
from typing import List


def set_verifyta_path(verifyta_path: str):
    """
    Set verifyta path, and you will get tips if `verifyta_path` is invalid.
    This function will check whether `verifyta_path` is valid by following steps:
    1. run '{verifyta_path} -h' with cmd
    2. check whether '-h [ --help ]' is in the result

    :param str verifyta_path: absolute path to `verifyta`
    """
    Verifyta().set_verifyta_path(verifyta_path)


def easy_verify(model_path: str | List[str], trace_path: str | List[str], verify_options: str="-t 1", num_threads=1):
    """
    Easy verification with default options, return to the shortest diagnostic path. 
    Verify the model in model_path and save the verification results to trace_path.

    :param str or List[str] model_path: model paths to be verified.
    :param str or List[str] trace_path: trace paths to be saved. Both `.xtr` and `.xml` formats are supported.
    :param str parallel: <'process'|'threads'>, select parallel method for accelerate verification, 
        None(default): run in sequence, 'process':use multiprocessing, 'threads': use multithreads.
    """
    return Verifyta().easy_verify(model_path, trace_path, verify_options, num_threads)


def get_timed_trace(model_path: str, trace_path: str, hold: bool = False):
    """
    Get `trace` and its `dclk` interval of each transition state.
    To emphasize, due to the limitation of verification return of `UPPAAL`, the trace is no longer a specific time, but a constraints of `gclk`, which makes it easier to generate a verification monitor, but is poor at dividing parameters.

    :param str model_path: the path of model file
    :param str trace_path: target trace file
    :param bool hold: determine whether retain intermediate file, e.g., `.if` and `.txt` file
    :return: a `SimTrace`
    """
    return Tracer.get_timed_trace(model_path, trace_path, hold)


def cmd(cmd: str):
    """
    Run common command with cmd, you can easily ignore the verifyta path.

    :return: the running cmd and the command result
    """
    return Verifyta().cmd(cmd)


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
    return Verifyta().cmds(cmds, num_threads)


# def get_communication_graph(model_path: str, save_path=None):
#     """
#     Get the communication graph of the uppaal model and save it to a `<.md | .svg | .png | .pdf>` file.

#     :param str model_path: path to the model file
#     :param str save_path: `<.md |d .svg | .png | .pdf>` the path to save graph file
#     :return: None
#     """
#     u = UModel(model_path)
#     return u.get_communication_graph(save_path)


# def find_a_pattern(model_path: str, inputs: TimedActions, observes: TimedActions,
#                    observe_actions: List[str] = None, focused_actions: List[str] = None, hold=False, options: str = None):
#     """
#     :param str model_path: path to the model file
#     :param TimedActions inputs: TimedActions of input signal model
#     :param TimedActions observes: TimedActions of observe signal model
#     :param List[str] input_actions: list of input signal
#     :param List[str] observe_actions: list of observe signal
#     :param bool hold: whether save history files
#     :param str options: verifyta options
#     :return: query, pattern_seq.actions @yhc SimTrace？
#     """
#     u = UModel(model_path)
#     return u.find_a_pattern(inputs, observes, observe_actions, focused_actions, hold, options)


# def find_all_patterns(model_path: str, inputs: TimedActions, observes: TimedActions, observe_actions: List[str] = None, focused_actions: List[str] = None, hold: bool = False, max_patterns: int = None):
#     u = UModel(model_path)
#     return u.find_all_patterns(inputs, observes, observe_actions, focused_actions, hold, max_patterns)


# def find_a_pattern_with_query(model_path: str, query: str = None, focused_actions: List[str] = None, hold=False, options=None):
#     u = UModel(model_path)
#     return u.find_a_pattern_with_query(query, focused_actions, hold, options)


# def find_all_patterns_with_query(model_path, query, focused_actions: List[str] = None, hold: bool = False, max_patterns: int = None):
#     u = UModel(model_path)
#     return u.find_all_patterns_with_query(query, focused_actions, hold, max_patterns)
