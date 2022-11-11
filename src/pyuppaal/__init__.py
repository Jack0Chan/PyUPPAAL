"""A research tool that can simulate, verify or modify UPPAAL models with 
python. It can also help to analyze counter-examples in .xml format
"""

from .verifyta import Verifyta
from .umodel import UModel
from .tracer import ClockZone, Transition, SimTrace, Tracer, GlobalVar
# from .config import *
from .pyuppaal import *
from .iTools import Mermaid
from .utap import utap_parser
from .datastruct import TimedActions

__version__='1.0.0'
