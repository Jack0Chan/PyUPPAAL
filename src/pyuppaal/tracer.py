"""使用方法 ./trace_custom.exe xxx.if xxx.xtr your_output.txt
注意输入要是LF行尾, 不能是CRLF, 否则会报错unknown section
"""
# 这一行的import能够指定class的method返回自身类
# 参考链接：https://www.nuomiphp.com/eplan/11188.html
from __future__ import annotations
from dataclasses import replace
import os
from typing import Dict, Generator, List
from xml.etree.ElementTree import Element, ElementTree
from .verifyta import Verifyta
import xml.etree.cElementTree as ET
from .utap import utap_parser


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
            res = f'{self.sync}: {self.start_process} -> {self.end_process}; '
            # if self.edges is not None:
            for edge in self.edges:
                res = res + f'{edge.start_location} -> {edge.end_location}; '
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

    def __init__(self, trace_string: str):
        """第i个state和第i个transition有相同的clock constraints

        第i个transition前面跟第i个state, 详情看__str__()

        Args:
            trace_string (str): _description_
            parse_raw (bool, optional): whether parse the raw trace string to components. Defaults to True.
        """
        self.__has_parse_raw = False
        self.__raw: str = trace_string
        self.__states: List[List[str]] = None
        self.__global_variables: List[GlobalVar] = None
        self.__clock_constraints: List[ClockZone] = None
        self.__transitions: List[Transition] = None

        # self.__parse_raw()

    def __str__(self):
        """Convert the trace to string.

        Examples:
            >>> trace = SimTrace(trace_from_pedestrian)
            >>> str(trace)
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

        Returns:
            _type_: _description_
        """
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
        return f'SimTrace(...)'

    def __len__(self):
        self.__parse_raw()
        return len(self.actions)

    def __getitem__(self, index: int | slice | List[int]) -> SimTrace:
        """Get the corresponding `SimTrace` by index.

        Args:
            index (int | slice): The indexs for slicing.

        Returns:
            SimTrace: The corresponding sliced SimTrace.
        """
        self.__parse_raw()
        if isinstance(index, (int, slice)):
            new_trace: SimTrace = SimTrace("")
            new_trace.__has_parse_raw = True
            new_trace.__states = self.__states[index]
            new_trace.__clock_constraints = self.__clock_constraints[index]
            new_trace.__transitions = self.__transitions[index]
            new_trace.__global_variables = self.__global_variables[index]
            return new_trace
        else:
            new_trace: SimTrace = SimTrace("")
            new_trace.__has_parse_raw = True
            new_trace.__states = [self.__states[i] for i in index]
            new_trace.__clock_constraints = [
                self.__clock_constraints[i] for i in index]
            new_trace.__transitions = [self.__transitions[i] for i in index]
            new_trace.__global_variables = [
                self.__global_variables[i] for i in index]
            return new_trace

    @property
    def raw(self) -> str:
        """Original raw string of the trace.

        Examples:
            >>> trace = SimTrace(trace_from_pedestrian)
            >>> trace.raw
            State: Cars.Idle TrafficLights.cRed_pGreen LV1Pedestrian2.Idle Cars.tCCrssMax=4 Cars.tCCrssMin=1 LV1Pedestrian2.tPCrssMin=0 LV1Pedestrian2.tPCrssMax=10 t(0)-tTL<=0 t(0)-Cars.tc<=0 t(0)-TrafficLights.tTL<=0 t(0)-LV1Pedestrian2.tp<=0 t(0)-LV1Pedestrian2.tTL<=0 tTL-t(0)<=55 tTL-Cars.tc<=0 Cars.tc-TrafficLights.tTL<=0 TrafficLights.tTL-LV1Pedestrian2.tp<=0 LV1Pedestrian2.tp-LV1Pedestrian2.tTL<=0 LV1Pedestrian2.tTL-tTL<=0
            Transition: LV1Pedestrian2.Idle -> LV1Pedestrian2.CheckTL {1; pWantCrss!; 1;} TrafficLights.cRed_pGreen -> TrafficLights._id8 {1; pWantCrss?; 1;}
            State: Cars.Idle TrafficLights._id8 LV1Pedestrian2.CheckTL Cars.tCCrssMax=4 Cars.tCCrssMin=1 LV1Pedestrian2.tPCrssMin=0 LV1Pedestrian2.tPCrssMax=10 t(0)-tTL<=0 t(0)-Cars.tc<=0 t(0)-TrafficLights.tTL<=0 t(0)-LV1Pedestrian2.tp<=0 t(0)-LV1Pedestrian2.tTL<=0 tTL-t(0)<=55 tTL-Cars.tc<=0 Cars.tc-TrafficLights.tTL<=0 TrafficLights.tTL-LV1Pedestrian2.tp<=0 LV1Pedestrian2.tp-LV1Pedestrian2.tTL<=0 LV1Pedestrian2.tTL-tTL<=0
            Transition: TrafficLights._id8 -> TrafficLights.cRed_pGreen {1; pGreen!; 1;} LV1Pedestrian2.CheckTL -> LV1Pedestrian2._id27 {1; pGreen?; 1;}
            State: Cars.Idle TrafficLights.cRed_pGreen LV1Pedestrian2._id27 Cars.tCCrssMax=4 Cars.tCCrssMin=1 LV1Pedestrian2.tPCrssMin=0 LV1Pedestrian2.tPCrssMax=10 t(0)-tTL<=0 t(0)-Cars.tc<=0 t(0)-TrafficLights.tTL<=0 t(0)-LV1Pedestrian2.tp<=0 t(0)-LV1Pedestrian2.tTL<=0 tTL-t(0)<=55 tTL-Cars.tc<=0 Cars.tc-TrafficLights.tTL<=0 TrafficLights.tTL-LV1Pedestrian2.tp<=0 LV1Pedestrian2.tp-LV1Pedestrian2.tTL<=0 LV1Pedestrian2.tTL-tTL<=0
            Transition: LV1Pedestrian2._id27 -> LV1Pedestrian2.Crossing {1; pCrss!; tp = 0;} Cars.Idle -> Cars.Idle {1; pCrss?; 1;}

        Returns:
            str: Original raw string of the trace.
        """
        return self.__raw

    @property
    def states(self) -> List[List[str]]:
        self.__parse_raw()
        return self.__states

    @property
    def clock_constraints(self) -> List[ClockZone]:
        self.__parse_raw()
        return self.__clock_constraints

    @property
    def transitions(self) -> List[Transition]:
        self.__parse_raw()
        return self.__transitions

    # 这个就是get_untimed_pattern
    @property
    def actions(self) -> List[str]:
        self.__parse_raw()
        return [x.action for x in self.transitions if x.action is not None]

    @property
    def untime_pattern(self) -> List[str]:
        self.__parse_raw()
        return self.actions

    @property
    def global_variables(self) -> List[GlobalVar]:
        self.__parse_raw()
        return self.__global_variables

    def filter_by_actions(self, focused_actions: List[str]) -> SimTrace:
        """Filter the transitions by actions.

        Args:
            focused_actions (List[str], optional): actions that you take cares of.

        Returns:
            SimTrace: _description_
        """
        self.__parse_raw()
        if focused_actions is None:
            return self
        index_array = [i for i in range(
            len(self.transitions)) if self.transitions[i].action in focused_actions]
        return self[index_array]

    def __parse_raw(self) -> None:
        """Parse raw string to components.
        """
        if self.__has_parse_raw:
            return
        trace_text = self.__raw
        trace_text = trace_text.split('\n')
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
                        clocks, clk_bound = [
                            x.strip() for x in tmp_trace_i[tr_sub].split('<')]
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
                global_variables.append(
                    GlobalVar(globalvar_name, globalvar_val))
            elif trace_text[tr_ind].startswith('Transition'):
                # Transition: PHisAAVFast.Retro -> PHisAAVFast._id15 {t >= tCondMin; actNode1!; t = 0;} NHisA.Rest -> NHisA._id7 {1; actNode?; 1;}
                # [PHisAAVFast.Retro -> PHisAAVFast._id15 {t >= tCondMin; actNode1!; t = 0;
                # NHisA.Rest -> NHisA._id7 {1; actNode?; 1;
                # '']
                tmp_trace_i = trace_text[tr_ind][12:].strip().split('}')[:-1]
                edges_list = []
                end_process = []
                sync_symbol = None
                start_process = None
                for tr_sub in range(len(tmp_trace_i)):
                    # [NHisA.Rest -> NHisA._id7,
                    #  1; actNode?; 1;
                    trans_comp, edge_trans = tmp_trace_i[tr_sub].split('{')
                    start_location, end_location = [
                        x.strip() for x in trans_comp.split('->')]
                    guard, sync, update = [x.strip()
                                           for x in edge_trans.split(';')[:-1]]
                    # strip
                    tmp_edge = Edges(
                        start_location, end_location, guard, sync, update)
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
                # print(transitions[-1].edges)
                # assert transitions[-1].edges != []
                # assert transitions[-1].edges is not None
            else:
                pass
        self.__states = states
        self.__clock_constraints = clock_constraints
        self.__transitions = transitions
        self.__global_variables = global_variables
        self.__has_parse_raw = True

    def save_raw(self, file_name: str) -> None:
        """Save raw data to file.

        Args:
            file_name (str): _description_
        """
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(self.raw)

    def save(self, file_name: str) -> None:
        """Save self.__str__() to file.

        Args:
            file_name (str): _description_
        """
        with open(file_name, 'w', encoding='utf-8') as f:
            # 这里有parse_raw
            f.write(self.__str__())

    def trim_transitions(self, model_path: str) -> None:
        """It reads the `.xml` file and gets the mapping from formal parameters to real parameters, then it
        replaces the formal parameters in the transitions with the real parameters.

        Args:
            model_path (str): The path of the `.xml` file.

        Raises:
            ValueError: When the `.xml` file is invalid.
        """
        self.__parse_raw()
        element_tree_root: Element | None = ET.ElementTree(
            file=model_path).getroot()
        if element_tree_root is None:
            # When the `.xml` file is invalid.
            raise ValueError(f"Invalid UPPAAL template file")

        # Get template parameters from .xml file
        templates: Generator[Element, None,
                             None] = element_tree_root.iterfind("template")
        param_map: Dict[str, List[str]] = dict()
        for template in templates:
            name_element: Element | None = template.find("name")
            if name_element is None:
                # When the `.xml` file is invalid.
                raise ValueError(f"Invalid UPPAAL template file")

            name: str = name_element.text  # uppaal guaranteed this to have only one
            param_elememt: Element | None = template.find(
                "parameter")  # uppaal guaranteed this to have only one
            if param_elememt is not None:
                param_map[name] = list(map(lambda item: item.strip().split(' ')[-1].replace('&', ''),
                                           param_elememt.text.split(',')))  # remove type and ref annotation
            else:
                param_map[name] = []

        # Get system components defination
        system_element: Element | None = element_tree_root.find("system")
        if system_element is None:
            # When the `.xml` file is invalid.
            raise ValueError(f"Invalid UPPAAL template file")

        system_items: List[str] = list(filter(lambda line: len(line) > 0 and line.find("//") != 0 and line.count(' ') != len(line), # remove comment and empty line
                                    system_element.text.replace("\r\n", "\n").replace('\t', '') .split("\n")))[:-1] # unify "\n", remove "\t" and remove "system"

        source_map: Dict[str, Dict[str, str]] = dict()
        for item in system_items:
            name, constructor = item.replace(";", "").replace(
                " ", "").split('=')  # remove ';' and ' '
            left_brace_index: int = constructor.find('(')
            # get the name of the constructor(template)
            constructor_name: str = constructor[:left_brace_index]
            real_param_list: List[str] = list(filter(
                lambda param: param != '', constructor[left_brace_index + 1: -1].split(',')))  # get corresponding param list
            # get constructor param list
            form_param_list: List[str] = param_map[constructor_name]

            # ? I am not sure if default value is allowed in UPPAAL
            # When the `.xml` file is invalid.
            assert len(real_param_list) == len(
                form_param_list), f"Invalid UPPAAL template file"

            if len(real_param_list) != 0:
                item_map: Dict[str, str] = dict()
                for i, real_param in enumerate(real_param_list):
                    # map form param to real param
                    item_map[form_param_list[i]] = real_param
                source_map[name] = item_map
        # print(source_map)

        for i, transition in enumerate(self.__transitions):
            if transition.sync is not None \
                    and transition.start_process in source_map.keys() \
                    and transition.sync in source_map[transition.start_process]:
                # If not in the keys, then it does not have a parameter, so we just skip it
                self.__transitions[i] = Transition(source_map[transition.start_process][transition.sync],
                                                   transition.start_process, transition.end_process, transition.edges)


class Tracer:
    """
    Analyze the `xtr` file generated by verification from command line
    """
    @staticmethod
    def get_timed_trace(model_path: str, xtr_trace_path: str) -> SimTrace | None:
        """Analyze the `xtr_trace_path` trace file generated by `model_path` model and return the instance `SimTrace`.

        The internal process is as following: 
        1. Convert the `model_path` model into a `.if` file.
        2. Analyze `.if` file and the `xtr_trace_path` to get the instance `SimTrace`.
        3. [reference](https://github.com/UPPAALModelChecker/utap).

        Args:
            model_path (str): the path of the `.xml` model file
            xtr_trace_path (str): the path of the `.xtr` trace file

        Returns:
            SimTrace | None: if you want to save the parsed raw trace, you can use SimTrace.save_raw(file_name)
        """
        if_str = Verifyta().compile_to_if(model_path=model_path)
        trace_text = utap_parser(if_str, xtr_trace_path)
        res = SimTrace(trace_text)
        res.trim_transitions(model_path)
        return res
