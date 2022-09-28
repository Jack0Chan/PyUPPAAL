"""tracer example:
State: Cars.Idle TrafficLights.cRed_pGreen LV1Pedestrian2.Idle Cars.tCCrssMax=4 Cars.tCCrssMin=1 LV1Pedestrian2.tPCrssMin=0 LV1Pedestrian2.tPCrssMax=10 t(0)-tTL<=0 t(0)-Cars.tc<=0 t(0)-TrafficLights.tTL<=0 t(0)-LV1Pedestrian2.tp<=0 t(0)-LV1Pedestrian2.tTL<=0 tTL-t(0)<=55 tTL-Cars.tc<=0 Cars.tc-TrafficLights.tTL<=0 TrafficLights.tTL-LV1Pedestrian2.tp<=0 LV1Pedestrian2.tp-LV1Pedestrian2.tTL<=0 LV1Pedestrian2.tTL-tTL<=0
Transition: LV1Pedestrian2.Idle -> LV1Pedestrian2.CheckTL {1; pWantCrss!; 1;} TrafficLights.cRed_pGreen -> TrafficLights._id8 {1; pWantCrss?; 1;}
State: Cars.Idle TrafficLights._id8 LV1Pedestrian2.CheckTL Cars.tCCrssMax=4 Cars.tCCrssMin=1 LV1Pedestrian2.tPCrssMin=0 LV1Pedestrian2.tPCrssMax=10 t(0)-tTL<=0 t(0)-Cars.tc<=0 t(0)-TrafficLights.tTL<=0 t(0)-LV1Pedestrian2.tp<=0 t(0)-LV1Pedestrian2.tTL<=0 tTL-t(0)<=55 tTL-Cars.tc<=0 Cars.tc-TrafficLights.tTL<=0 TrafficLights.tTL-LV1Pedestrian2.tp<=0 LV1Pedestrian2.tp-LV1Pedestrian2.tTL<=0 LV1Pedestrian2.tTL-tTL<=0
Transition: TrafficLights._id8 -> TrafficLights.cRed_pGreen {1; pGreen!; 1;} LV1Pedestrian2.CheckTL -> LV1Pedestrian2._id27 {1; pGreen?; 1;}
State: Cars.Idle TrafficLights.cRed_pGreen LV1Pedestrian2._id27 Cars.tCCrssMax=4 Cars.tCCrssMin=1 LV1Pedestrian2.tPCrssMin=0 LV1Pedestrian2.tPCrssMax=10 t(0)-tTL<=0 t(0)-Cars.tc<=0 t(0)-TrafficLights.tTL<=0 t(0)-LV1Pedestrian2.tp<=0 t(0)-LV1Pedestrian2.tTL<=0 tTL-t(0)<=55 tTL-Cars.tc<=0 Cars.tc-TrafficLights.tTL<=0 TrafficLights.tTL-LV1Pedestrian2.tp<=0 LV1Pedestrian2.tp-LV1Pedestrian2.tTL<=0 LV1Pedestrian2.tTL-tTL<=0
Transition: LV1Pedestrian2._id27 -> LV1Pedestrian2.Crossing {1; pCrss!; tp = 0;} Cars.Idle -> Cars.Idle {1; pCrss?; 1;}
State: Cars.Idle TrafficLights.cRed_pGreen LV1Pedestrian2.Crossing Cars.tCCrssMax=4 Cars.tCCrssMin=1 LV1Pedestrian2.tPCrssMin=0 LV1Pedestrian2.tPCrssMax=10 t(0)-tTL<=0 t(0)-Cars.tc<=0 t(0)-TrafficLights.tTL<=0 t(0)-LV1Pedestrian2.tp<=0 t(0)-LV1Pedestrian2.tTL<=0 tTL-t(0)<=55 tTL-Cars.tc<=0 Cars.tc-TrafficLights.tTL<=0 TrafficLights.tTL-LV1Pedestrian2.tTL<=0 LV1Pedestrian2.tp-t(0)<=10 LV1Pedestrian2.tp-tTL<=0 LV1Pedestrian2.tTL-tTL<=0
Transition: TrafficLights.cRed_pGreen -> TrafficLights.cRed_pYellow {tTL >= 55; 0; tTL = 0;}
State: Cars.Idle TrafficLights.cRed_pYellow LV1Pedestrian2.Crossing Cars.tCCrssMax=4 Cars.tCCrssMin=1 LV1Pedestrian2.tPCrssMin=0 LV1Pedestrian2.tPCrssMax=10 t(0)-tTL<=-55 t(0)-Cars.tc<=0 t(0)-TrafficLights.tTL<=0 t(0)-LV1Pedestrian2.tp<=0 t(0)-LV1Pedestrian2.tTL<=0 tTL-t(0)<=60 tTL-Cars.tc<=0 tTL-LV1Pedestrian2.tp<=55 Cars.tc-TrafficLights.tTL<=55 TrafficLights.tTL-LV1Pedestrian2.tTL<=-55 LV1Pedestrian2.tp-t(0)<=10 LV1Pedestrian2.tTL-tTL<=0
Transition: TrafficLights.cRed_pYellow -> TrafficLights.cGreen_pRed {tTL >= 5; 0; tTL = 0;}
State: Cars.Idle TrafficLights.cGreen_pRed LV1Pedestrian2.Crossing Cars.tCCrssMax=4 Cars.tCCrssMin=1 LV1Pedestrian2.tPCrssMin=0 LV1Pedestrian2.tPCrssMax=10 t(0)-tTL<=-60 t(0)-Cars.tc<=0 t(0)-TrafficLights.tTL<=0 t(0)-LV1Pedestrian2.tp<=0 t(0)-LV1Pedestrian2.tTL<=0 tTL-Cars.tc<=0 tTL-LV1Pedestrian2.tp<=55 Cars.tc-TrafficLights.tTL<=60 TrafficLights.tTL-LV1Pedestrian2.tTL<=-60 LV1Pedestrian2.tp-t(0)<=10 LV1Pedestrian2.tTL-tTL<=0
Transition: Cars.Idle -> Cars.CheckTL {tc >= 1; cWantCrss!; 1;} TrafficLights.cGreen_pRed -> TrafficLights._id5 {1; cWantCrss?; 1;}
State: Cars.CheckTL TrafficLights._id5 LV1Pedestrian2.Crossing Cars.tCCrssMax=4 Cars.tCCrssMin=1 LV1Pedestrian2.tPCrssMin=0 LV1Pedestrian2.tPCrssMax=10 t(0)-tTL<=-60 t(0)-Cars.tc<=0 t(0)-TrafficLights.tTL<=0 t(0)-LV1Pedestrian2.tp<=0 t(0)-LV1Pedestrian2.tTL<=0 tTL-Cars.tc<=0 tTL-LV1Pedestrian2.tp<=55 Cars.tc-TrafficLights.tTL<=60 TrafficLights.tTL-LV1Pedestrian2.tTL<=-60 LV1Pedestrian2.tp-t(0)<=10 LV1Pedestrian2.tTL-tTL<=0
Transition: TrafficLights._id5 -> TrafficLights.cGreen_pRed {1; cGreen!; 1;} Cars.CheckTL -> Cars.Crossing {1; cGreen?; tc = 0;}
State: Cars.Crossing TrafficLights.cGreen_pRed LV1Pedestrian2.Crossing Cars.tCCrssMax=4 Cars.tCCrssMin=1 LV1Pedestrian2.tPCrssMin=0 LV1Pedestrian2.tPCrssMax=10 t(0)-tTL<=0 t(0)-Cars.tc<=0 t(0)-TrafficLights.tTL<=0 t(0)-LV1Pedestrian2.tp<=0 t(0)-LV1Pedestrian2.tTL<=0 tTL-TrafficLights.tTL<=60 tTL-LV1Pedestrian2.tp<=55 Cars.tc-t(0)<=1 Cars.tc-tTL<=-60 TrafficLights.tTL-LV1Pedestrian2.tTL<=-60 LV1Pedestrian2.tp-t(0)<=10 LV1Pedestrian2.tTL-tTL<=0 

使用方法 ./trace_custom.exe xxx.if xxx.xtr your_output.txt
注意输入要是LF行尾, 不能是CRLF, 否则会报错unknown section
"""
# 这一行的import能够指定class的method返回自身类
# 参考链接：https://www.nuomiphp.com/eplan/11188.html
from __future__ import annotations
import os
from typing import List
from .verifyta import Verifyta
from .config import TRACER_CUSTOM_PATH


class OneClockZone:
    """_summary_
    """
    def __init__(self, clock1: str, clock2: str, is_equal: bool, bound_value: int):
        """clock1 - clock2 < or ≤ bound_value

        Args:
            clock1 (str): _description_
            clock2 (str): _description_
            is_equal (bool): _description_
            bound_value (int): _description_
        """
        self.__clock1: str = clock1
        self.__clock2: str = clock2
        self.__is_equal: bool = is_equal
        self.__bound_value: int = bound_value

    def __str__(self):
        sign = '≤' if self.is_equal else '<'
        res = f'{self.clock1} - {self.clock2} {sign} {self.bound_value}'
        return res

    def __repr__(self):
        return self.__str__()

    @property
    def clock1(self) -> str:
        """clock1 - clock2 < or ≤ bound_value

        Returns:
            str: _description_
        """
        return self.__clock1

    @property
    def clock2(self) -> str:
        """clock1 - clock2 < or ≤ bound_value

        Returns:
            str: _description_
        """
        return self.__clock2

    @property
    def is_equal(self) -> bool:
        """clock1 - clock2 < or ≤ bound_value

        Returns:
            str: _description_
        """
        return self.__is_equal

    @property
    def bound_value(self) -> int:
        """clock1 - clock2 < or ≤ bound_value

        Returns:
            str: _description_
        """
        return self.__bound_value


class ClockZone:
    """Composed by `List` of `OneClockZone`.
    """
    def __init__(self, clockzones: List[OneClockZone]):
        """Composed by `List` of `OneClockZone`.

        For the `.xtr` trace, each state contains several clock zones.

        Args:
            clockzones (List[OneClockZone]): _description_
        """
        self.__clockzones: List[OneClockZone] = clockzones

    def __str__(self):
        if self.clockzones:
            res = '['
            for clock_zone in self.clockzones:
                res += f'{clock_zone.__str__()}; '
            res += ']'
            return res

    def __repr__(self):
        return self.__str__()

    @property
    def clockzones(self) -> List[OneClockZone]:
        """`List` of `OneClockZone`.

        Returns:
            List[OneClockZone]: _description_
        """
        return self.__clockzones


class Edges:
    """`Edges` are components of `Transition`. One Transition contains at least one Edge. 
    If more than 1 Edges are contained, it means that there is sync occurred. On this condition, Edges[0] is the sender(!) and others are reveivers(?).

    An Edge looks like this: 
    process.start_location -> process.end_location: {guard, sync, update}.
    A Transition looks like this:
    Transition: LV1Pedestrian2.Idle -> LV1Pedestrian2.CheckTL {1; pWantCrss!; 1;} TrafficLights.cRed_pGreen -> TrafficLights._id8 {1; pWantCrss?; 1;}
    """
    def __init__(self, start_location: str, end_location: str, guard: str, sync: str, update: str):
        """process.start_location -> process.end_location: {guard, sync, update}

        Args:
            start_location (str): _description_
            end_location (str): _description_
            guard (str): _description_
            sync (str): _description_
            update (str): _description_
        """
        self.__start_location: str = start_location
        self.__end_location: str = end_location
        self.__guard: str = guard
        self.__sync: str = sync
        self.__update: str = update
        # one edge has only one process
        self.__process: str = self.start_location.split('.')[0]

    def __str__(self):
        res = f'{self.process}.{self.start_location} -> {self.process}.{self.end_location}:'
        res = res + f'{{{self.guard};{self.sync};{self.update}}}'
        return res

    def __repr__(self):
        return self.__str__()

    @property
    def start_location(self) -> str:
        """_summary_

        Returns:
            str: _description_
        """
        return self.__start_location

    @property
    def end_location(self) -> str:
        """_summary_

        Returns:
            str: _description_
        """
        return self.__end_location

    @property
    def guard(self) -> str:
        """If `guard == '1'`, it means the edge does not have a guard.

        Returns:
            str: _description_
        """
        return self.__guard

    @property
    def has_guard(self) -> bool:
        """Whether the edge has a gurad.
        
        If `guard == '1'`, it means the edge does not have a guard.

        Returns:
            bool: _description_
        """
        return self.guard == '1'

    @property
    def sync(self) -> str:
        """_summary_

        Returns:
            str: _description_
        """
        return self.__sync

    @property
    def update(self) -> str:
        """_summary_

        Returns:
            str: _description_
        """
        return self.__update

    @property
    def process(self) -> str:
        """One edge has only one process.

        Returns:
            str: _description_
        """
        return self.__process

    @property
    def is_sync(self) -> bool:
        """_summary_

        Returns:
            bool: _description_
        """
        return self.sync[-1] == '!' or self.sync[-1] == '?'

    @property
    def sync_type(self) -> str:
        """_summary_

        Returns:
            str: _description_
        """
        if self.is_sync:
            return 'send' if self.sync[-1] == '!' else 'receive'
        else:
            return None

    @property
    def sync_symbol(self) -> str:
        """_summary_

        Returns:
            str: _description_
        """
        if self.is_sync:
            return self.sync[:-1]
        else:
            return None


class Transition:
    """One `Transition` contains at least one `Edge`. 
    If more than 1 Edges are contained, it means that there is sync occurred. On this condition, Edges[0] is the sender(!) and others are reveivers(?).

    An Edge looks like this: 
    process.start_location -> process.end_location: {guard, sync, update}.
    A Transition looks like this:
    Transition: LV1Pedestrian2.Idle -> LV1Pedestrian2.CheckTL {1; pWantCrss!; 1;} TrafficLights.cRed_pGreen -> TrafficLights._id8 {1; pWantCrss?; 1;}
    """
    def __init__(self, sync: str, start_process: str, end_process: List[str], edges: List[Edges] = None):
        """_summary_

        Args:
            sync (str): _description_
            start_process (str): _description_
            end_process (List[str]): _description_
            edges (List[Edges], optional): _description_. Defaults to None.
        """
        self.__sync: str = sync
        self.__start_process: str = start_process
        self.__end_process: List[str] = end_process
        # 这个edges暂时没用，但是我们也先存下来了。
        self.__edges: List[Edges] = edges

    def __str__(self):
        if self.sync is None:
            res = f'{self.sync}: {self.edges[0].start_location} -> {self.edges[0].end_location}'
        else:
            res = f'{self.sync}: {self.start_process} -> {self.end_process}'
        return res

    def __repr__(self):
        return self.__str__()

    @property
    def sync(self) -> str:
        return self.__sync

    @property
    def start_process(self) -> str:
        return self.__start_process

    @property
    def end_process(self) -> List[str]:
        return self.__end_process

    @property
    def edges(self) -> List[Edges]:
        return self.__edges

    @property
    def action(self) -> str:
        return self.sync


class GlobalVar:
    def __init__(self, variables_name: List[str], variables_value: List[float]):
        """GlobalVar: variables_name[i] = variables_value[i]

        Args:
            variables_name (List[str]): _description_
            variables_value (List[float]): _description_
        """
        self.variables_name: List[str] = variables_name
        self.variables_value: List[float] = variables_value

    def __str__(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        if self.variables_name:
            res = '['
            for i in range(len(self.variables_name)):
                res += f'{self.variables_name[i]}={self.variables_value[i]}; '
            res += ']'
            return res
    
    def __repr__(self):
        return self.__str__()


class SimTrace:
    """_summary_
    """
    def __init__(self, trace_string: str, parse_raw: bool = True):
        """第i个state和第i个transition有相同的clock constraints
       
        第i个transition前面跟第i个state, 详情看__str__()

        Args:
            trace_string (str): _description_
            parse_raw (bool, optional): whether parse the raw trace string to components. Defaults to True.
        """
        self.__raw: str = trace_string
        self.__states: List[List[str]] = None
        self.__global_variables: List[GlobalVar] = None
        self.__clock_constraints: List[ClockZone] = None
        self.__transitions: List[Transition] = None
        self.__is_parse_raw = parse_raw
        if self.__is_parse_raw:
            self.__parse_raw()

    def __str__(self):
        """_summary_

            State [0]: ['Cars.Idle', 'TrafficLights.cRed_pGreen', 'LV1Pedestrian2.Idle']
            global_variables [0]: [Cars.tCCrssMax=4; Cars.tCCrssMin=1; LV1Pedestrian2.tPCrssMin=0; LV1Pedestrian2.tPCrssMax=10; ]
            Clock_constraints [0]: [t(0) - tTL ≤ 0; t(0) - Cars.tc ≤ 0; t(0) - TrafficLights.tTL ≤ 0; t(0) - LV1Pedestrian2.tp ≤ 0; t(0) - LV1Pedestrian2.tTL ≤ 0; tTL - t(0) ≤ 55; tTL - Cars.tc ≤ 0; Cars.tc - TrafficLights.tTL ≤ 0; TrafficLights.tTL - LV1Pedestrian2.tp ≤ 0; LV1Pedestrian2.tp - LV1Pedestrian2.tTL ≤ 0; LV1Pedestrian2.tTL - tTL ≤ 0; ]
            transitions [0]: pWantCrss: LV1Pedestrian2 -> ['TrafficLights']
            -----------------------------------
            State [1]: ['Cars.Idle', 'TrafficLights._id8', 'LV1Pedestrian2.CheckTL']
            global_variables [1]: [Cars.tCCrssMax=4; Cars.tCCrssMin=1; LV1Pedestrian2.tPCrssMin=0; LV1Pedestrian2.tPCrssMax=10; ]
            Clock_constraints [1]: [t(0) - tTL ≤ 0; t(0) - Cars.tc ≤ 0; t(0) - TrafficLights.tTL ≤ 0; t(0) - LV1Pedestrian2.tp ≤ 0; t(0) - LV1Pedestrian2.tTL ≤ 0; tTL - t(0) ≤ 55; tTL - Cars.tc ≤ 0; Cars.tc - TrafficLights.tTL ≤ 0; TrafficLights.tTL - LV1Pedestrian2.tp ≤ 0; LV1Pedestrian2.tp - LV1Pedestrian2.tTL ≤ 0; LV1Pedestrian2.tTL - tTL ≤ 0; ]
            transitions [1]: pGreen: TrafficLights -> ['LV1Pedestrian2']
            -----------------------------------
            State [2]: ['Cars.Idle', 'TrafficLights.cRed_pGreen', 'LV1Pedestrian2._id27']
            global_variables [2]: [Cars.tCCrssMax=4; Cars.tCCrssMin=1; LV1Pedestrian2.tPCrssMin=0; LV1Pedestrian2.tPCrssMax=10; ]
            Clock_constraints [2]: [t(0) - tTL ≤ 0; t(0) - Cars.tc ≤ 0; t(0) - TrafficLights.tTL ≤ 0; t(0) - LV1Pedestrian2.tp ≤ 0; t(0) - LV1Pedestrian2.tTL ≤ 0; tTL - t(0) ≤ 55; tTL - Cars.tc ≤ 0; Cars.tc - TrafficLights.tTL ≤ 0; TrafficLights.tTL - LV1Pedestrian2.tp ≤ 0; LV1Pedestrian2.tp - LV1Pedestrian2.tTL ≤ 0; LV1Pedestrian2.tTL - tTL ≤ 0; ]
            transitions [2]: pCrss: LV1Pedestrian2 -> ['Cars']
            -----------------------------------
            State [3]: ['Cars.Idle', 'TrafficLights.cRed_pGreen', 'LV1Pedestrian2.Crossing']
            global_variables [3]: [Cars.tCCrssMax=4; Cars.tCCrssMin=1; LV1Pedestrian2.tPCrssMin=0; LV1Pedestrian2.tPCrssMax=10; ]
            Clock_constraints [3]: [t(0) - tTL ≤ 0; t(0) - Cars.tc ≤ 0; t(0) - TrafficLights.tTL ≤ 0; t(0) - LV1Pedestrian2.tp ≤ 0; t(0) - LV1Pedestrian2.tTL ≤ 0; tTL - t(0) ≤ 55; tTL - Cars.tc ≤ 0; Cars.tc - TrafficLights.tTL ≤ 0; TrafficLights.tTL - LV1Pedestrian2.tTL ≤ 0; LV1Pedestrian2.tp - t(0) ≤ 10; LV1Pedestrian2.tp - tTL ≤ 0; LV1Pedestrian2.tTL - tTL ≤ 0; ]
            transitions [3]: None: TrafficLights.cRed_pGreen -> TrafficLights.cRed_pYellow
            -----------------------------------
            State [4]: ['Cars.Idle', 'TrafficLights.cRed_pYellow', 'LV1Pedestrian2.Crossing']
            global_variables [4]: [Cars.tCCrssMax=4; Cars.tCCrssMin=1; LV1Pedestrian2.tPCrssMin=0; LV1Pedestrian2.tPCrssMax=10; ]
            Clock_constraints [4]: [t(0) - tTL ≤ -55; t(0) - Cars.tc ≤ 0; t(0) - TrafficLights.tTL ≤ 0; t(0) - LV1Pedestrian2.tp ≤ 0; t(0) - LV1Pedestrian2.tTL ≤ 0; tTL - t(0) ≤ 60; tTL - Cars.tc ≤ 0; tTL - LV1Pedestrian2.tp ≤ 55; Cars.tc - TrafficLights.tTL ≤ 55; TrafficLights.tTL - LV1Pedestrian2.tTL ≤ -55; LV1Pedestrian2.tp - t(0) ≤ 10; LV1Pedestrian2.tTL - tTL ≤ 0; ]
            transitions [4]: None: TrafficLights.cRed_pYellow -> TrafficLights.cGreen_pRed
            -----------------------------------
            State [5]: ['Cars.Idle', 'TrafficLights.cGreen_pRed', 'LV1Pedestrian2.Crossing']
            global_variables [5]: [Cars.tCCrssMax=4; Cars.tCCrssMin=1; LV1Pedestrian2.tPCrssMin=0; LV1Pedestrian2.tPCrssMax=10; ]
            Clock_constraints [5]: [t(0) - tTL ≤ -60; t(0) - Cars.tc ≤ 0; t(0) - TrafficLights.tTL ≤ 0; t(0) - LV1Pedestrian2.tp ≤ 0; t(0) - LV1Pedestrian2.tTL ≤ 0; tTL - Cars.tc ≤ 0; tTL - LV1Pedestrian2.tp ≤ 55; Cars.tc - TrafficLights.tTL ≤ 60; 
            TrafficLights.tTL - LV1Pedestrian2.tTL ≤ -60; LV1Pedestrian2.tp - t(0) ≤ 10; LV1Pedestrian2.tTL - tTL ≤ 0; ]
            transitions [5]: cWantCrss: Cars -> ['TrafficLights']
            -----------------------------------
            State [6]: ['Cars.CheckTL', 'TrafficLights._id5', 'LV1Pedestrian2.Crossing']
            global_variables [6]: [Cars.tCCrssMax=4; Cars.tCCrssMin=1; LV1Pedestrian2.tPCrssMin=0; LV1Pedestrian2.tPCrssMax=10; ]
            Clock_constraints [6]: [t(0) - tTL ≤ -60; t(0) - Cars.tc ≤ 0; t(0) - TrafficLights.tTL ≤ 0; t(0) - LV1Pedestrian2.tp ≤ 0; t(0) - LV1Pedestrian2.tTL ≤ 0; tTL - Cars.tc ≤ 0; tTL - LV1Pedestrian2.tp ≤ 55; Cars.tc - TrafficLights.tTL ≤ 60; 
            TrafficLights.tTL - LV1Pedestrian2.tTL ≤ -60; LV1Pedestrian2.tp - t(0) ≤ 10; LV1Pedestrian2.tTL - tTL ≤ 0; ]
            transitions [6]: cGreen: TrafficLights -> ['Cars']
            -----------------------------------
            State [7]: ['Cars.Crossing', 'TrafficLights.cGreen_pRed', 'LV1Pedestrian2.Crossing']
            global_variables [7]: [Cars.tCCrssMax=4; Cars.tCCrssMin=1; LV1Pedestrian2.tPCrssMin=0; LV1Pedestrian2.tPCrssMax=10; ]
            Clock_constraints [7]: [t(0) - tTL ≤ 0; t(0) - Cars.tc ≤ 0; t(0) - TrafficLights.tTL ≤ 0; t(0) - LV1Pedestrian2.tp ≤ 0; t(0) - LV1Pedestrian2.tTL ≤ 0; tTL - TrafficLights.tTL ≤ 60; tTL - LV1Pedestrian2.tp ≤ 55; Cars.tc - t(0) ≤ 1; Cars.tc - tTL ≤ -60; TrafficLights.tTL - LV1Pedestrian2.tTL ≤ -60; LV1Pedestrian2.tp - t(0) ≤ 10; LV1Pedestrian2.tTL - tTL ≤ 0; ]

        Returns:
            _type_: _description_
        """
        if not self.__is_parse_raw:
            self.__is_parse_raw = True
            self.__parse_raw()

        res = ''
        for i in range(len(self.__states)):
            res += f'State [{i}]: {self.__states[i].__str__()}\n'
            res += f'global_variables [{i}]: {self.__global_variables[i].__str__()}\n'
            res += f'Clock_constraints [{i}]: {self.__clock_constraints[i].__str__()}\n'
            if i < len(self.__states) - 1:
                res += f'transitions [{i}]: {self.__transitions[i].__str__()}\n'
                res += f'-----------------------------------\n'
        return res

    def __repr__(self):
        return self.__str__()

    def __parse_raw(self):
        """Parse raw string to components.
        """
        trace_text = self.__raw
        clock_constraints, states, global_variables, transitions = [], [], [], []
        for tr_ind in range(len(trace_text)):
            state_text, globalvar_name, globalvar_val, clockzones_text, transitions_text = [], [], [], [], []
            if trace_text[tr_ind].startswith('State'):
                tmp_trace_i = trace_text[tr_ind][7:].strip().split(' ')
                for tr_sub in range(len(tmp_trace_i)):
                    if ("=" in tmp_trace_i[tr_sub]) and ('<' not in tmp_trace_i[tr_sub]):
                        # globalvariables
                        var_name, var_val = tmp_trace_i[tr_sub].split('=')
                        globalvar_name.append(var_name.strip())
                        globalvar_val.append(var_val.strip())
                    elif ('<' in tmp_trace_i[tr_sub]) and ('-' in tmp_trace_i[tr_sub]):
                        # clockzones
                        clocks, clk_bound = [x.strip() for x in tmp_trace_i[tr_sub].split('<')]
                        clock1, clock2 = [x.strip() for x in clocks.split('-')]
                        if clk_bound[0] == '=':
                            clk_bound = clk_bound[1:]
                            is_equal = True
                        else:
                            is_equal = False
                        clkzone = OneClockZone(clock1=clock1.strip(), clock2=clock2.strip(' '),
                                            is_equal=is_equal, bound_value=clk_bound.strip(' '))
                        clockzones_text.append(clkzone)
                    else:
                        # state
                        state_text.append(tmp_trace_i[tr_sub].strip())
                clock_constraints.append(ClockZone(clockzones_text))
                states.append(state_text)
                global_variables.append(GlobalVar(globalvar_name, globalvar_val))
            elif trace_text[tr_ind].startswith('Transition'):
                tmp_trace_i = trace_text[tr_ind][12:].strip().split('}')[:-1]
                edges_list = []
                end_process = []
                sync_symbol = None
                start_process = None
                for tr_sub in range(len(tmp_trace_i)):
                    trans_comp, edge_trans = tmp_trace_i[tr_sub].split('{')
                    start_location, end_location = [x.strip() for x in trans_comp.split('->')]
                    guard, sync, update = [x.strip() for x in edge_trans.split(';')[:-1]]
                    # strip
                    tmp_edge = Edges(start_location, end_location, guard, sync, update)
                    if tmp_edge.sync_type == 'send':
                        start_process = tmp_edge.process
                        sync_symbol = tmp_edge.sync_symbol
                    elif tmp_edge.sync_type == 'receive':
                        end_process.append(tmp_edge.process)
                    else:
                        start_process = tmp_edge.process
                        end_process.append(tmp_edge.process)
                    edges_list.append(tmp_edge)
                transitions.append(Transition(sync=sync_symbol, start_process=start_process,
                                              end_process=end_process, edges=edges_list))
            else:
                pass
        self.__states = states
        self.__clock_constraints = clock_constraints
        self.__transitions = transitions
        self.__global_variables = global_variables

    def save_raw(self, file_name: str) -> None:
        # save raw data to .txt file
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(self.raw)

    @property
    def raw(self) -> str:
        """Original raw string of the trace.

        Returns:
            str: Original raw string of the trace.
        """
        return self.__raw

    @property
    def states(self) -> List[List[str]]:
        return self.__states

    @property
    def clock_constraints(self) -> List[ClockZone]:
        return self.__clock_constraints

    @property
    def transitions(self) -> List[Transition]:
        return self.__transitions

    # 这个就是get_untimed_pattern
    @property
    def actions(self) -> List[str]:
        return [x.action for x in self.transitions if x.action is not None]

    def get_untime_pattern(self) -> List[str]:
        return self.actions

    def filter_by_index(self, index_array: List[int]) -> SimTrace:
        # 用__slice__方法改写
        """Filter the corresponding `SimTrace` by index.

        Args:
            index_array (List[int]): _description_

        Returns:
            SimTrace: _description_
        """
        new_states = [self.__states[i] for i in range(len(self.__states)) if i in index_array]
        new_clock_cons = [self.__clock_constraints[i] for i in range(len(self.__clock_constraints)) if i in index_array]
        new_transitions = [self.__transitions[i] for i in range(len(self.__transitions)) if i in index_array]
        new_global_var = [self.__global_variables[i] for i in range(len(self.__global_variables)) if i in index_array]
        new_simtrace = SimTrace(new_states, new_clock_cons, new_transitions, new_global_var)
        return new_simtrace

    def filter_by_actions(self, focused_actions: List[str]) -> SimTrace:
        """Filter the transitions by actions.

        Args:
            focused_actions (List[str], optional): actions that you take cares of.

        Returns:
            SimTrace: _description_
        """
        if focused_actions is None:
            return self
        
        index_array = [i for i in range(len(self.transitions)) if self.transitions[i].action in focused_actions]
        return self.filter_by_index(index_array)


class Tracer:
    """
    Analyze the `xtr` file generated by verification from command line
    """
    @staticmethod
    def get_timed_trace(model_path: str, xtr_trace_path: str) -> SimTrace:
        """Analyze the `xtr_trace_path` trace file generated by `model_path` model and return the instance `SimTrace`.

        The internal process is as following: 
        1. Convert the `model_path` model into a `.if` file.
        2. Analyze `.if` file and the `xtr_trace_path` to get the instance `SimTrace`.
        3. [reference](https://github.com/UPPAALModelChecker/utap).

        Args:
            model_path (str): the path of the `.xml` model file
            xtr_trace_path (str): the path of the `.xtr` trace file
            save_raw (bool, optional): determine whether to save the raw trace text. Defaults to False.

        Raises:
            FileNotFoundError: _description_

        Returns:
            SimTrace: if you want to save the parsed raw trace, you can use SimTrace.save_raw(file_name)
        """

        trace_path = xtr_trace_path
        verifyta = Verifyta()
        # use Verifta to compile model_path to if format file
        if_file = verifyta.compile_to_if(model_path=model_path)
        # .if 文件名和拓展名
        # file_path, file_ext = os.path.splitext(if_file)
        # construct command
        cmd_command = f'{TRACER_CUSTOM_PATH} {if_file} {trace_path}'
        # cmd result
        trace_text = os.popen(cmd_command).read()
        # remove .if file
        os.remove(if_file)
        res = SimTrace(trace_text)
        return res
