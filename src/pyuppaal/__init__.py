"""A research tool that can simulate, verify or modify UPPAAL models with 
python. It can also help to analyze counter-examples in .xml format
"""

from .verifyta import Verifyta
from .umodel import UModel
from .tracer import ClockZone, Transition, SimTrace, GlobalVar
from .build_cg import Mermaid
from .pyuppaal import *

__version__ = '1.2.0'
