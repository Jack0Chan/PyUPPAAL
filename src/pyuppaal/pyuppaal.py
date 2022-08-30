from __future__ import annotations
from .verifyta import Verifyta
from .tracer import Tracer
from .umodel import UModel
from typing import List


def set_verifyta_path(verifyta_path: str):
    Verifyta().set_verifyta_path(verifyta_path)

def simple_verify(model_path: str | List[str], 
                  trace_path: str | List[str], 
                  parallel: str=None):
    return Verifyta().simple_verify(model_path, trace_path, parallel)

def cmd(cmd: str):
    return Verifyta().cmd(cmd)

def get_timed_trace(model_path: str, trace_path: str, hold: bool=False):
    return Tracer.get_timed_trace(model_path, trace_path,hold)

def cmds_loop(cmds: List[str]):
    return Verifyta().cmds_loop(cmds)

def cmds_process(cmds: List[str], num_process: int = None):
    return Verifyta().cmd_process(cmds,num_process)

def cmds_threads(cmds: List[str], num_threads: int = None):
    return Verifyta().cmds_threads(cmds,num_threads)

def get_communication_graph(model_path: str, save_path=None):
    u=UModel(model_path)
    return u.get_communication_graph(save_path)