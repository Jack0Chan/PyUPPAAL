from __future__ import annotations
from .verifyta import Verifyta
# import os



def set_verifyta_path(verifyta_path: str):
    v = Verifyta()
    v.set_verifyta_path(verifyta_path)

# def simple_verify(model_path: str | List[str], 
#                   trace_path: str | List[str], 
#                   parallel: str=None):
#     v = Verifyta()
#     return v.simple_verify(model_path, trace_path, parallel)


    