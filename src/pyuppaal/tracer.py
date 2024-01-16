"""使用方法 ./trace_custom.exe xxx.if xxx.xtr your_output.txt
注意输入要是LF行尾, 不能是CRLF, 否则会报错unknown section
"""
# 这一行的import能够指定class的method返回自身类
# 参考链接：https://www.nuomiphp.com/eplan/11188.html
from __future__ import annotations
from typing import Dict, Generator, List
import xml.etree.ElementTree as ET

from .verifyta import Verifyta
from .utap import utap_parser

class SimTrace:
    """SimTrace is a class that represents a trace.
    """

    def __init__(self, trace_string: str):
        """第i个state和第i个transition有相同的clock constraints

        第i个transition前面跟第i个state, 详情看__str__()

        Args:
            trace_string (str): the raw trace string.
            parse_raw (bool, optional): whether parse the raw trace string to components. Defaults to True.
        """
        self.__has_parse_raw: bool = False
        self.__raw: str = trace_string
        self.__states: List[List[str]] = None
        self.__global_variables: List[GlobalVar] = None
        self.__clock_constraints: List[ClockZone] = None
        self.__transitions: List[Transition] = None

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
            str: the string representation of the trace.
        """
        self.__parse_raw()

        res = ''
        for i, state_i in enumerate(self.__states):
            res += f'State [{i}]: {state_i}\n'
            if len(self.__global_variables[i].variables_value) > 0:
                res += f'global_variables [{i}]: {self.__global_variables[i]}\n'
            else :
                res += f'global_variables [{i}]: None\n'
            if len(self.__clock_constraints[i].clockzones) > 0:
                res += f'Clock_constraints [{i}]: {self.__clock_constraints[i]}\n'
            else :
                res += f'Clock_constraints [{i}]: None\n'
            if i < len(self.__states) - 1:
                res += f'transitions [{i}]: {self.__transitions[i]}\n'
                res += '-----------------------------------\n'
        return res

    def __repr__(self):
        return 'SimTrace(...)'

    def __len__(self):
        self.__parse_raw()
        return len(self.actions)

    def __eq__(self, other):
        return self.__str__() == other.__str__()

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
            SimTrace: The filtered SimTrace.
        """
        self.__parse_raw()
        if focused_actions is None or self.raw is None:
            return self
        index_array = [i for i in range(len(self.transitions)) if self.transitions[i].action in focused_actions]
        return self[index_array]

    def __parse_raw(self) -> None:
        """Parse raw string to components.
        """
        if self.__has_parse_raw:
            return
        trace_text = self.__raw
        trace_text = trace_text.split('\n')
        clock_constraints, states, global_variables, transitions = [], [], [], []
        for trace_text_i in trace_text:
            state_text, globalvar_name, globalvar_val, clockzones_text = [], [], [], []
            if trace_text_i.startswith('State'):
                tmp_trace = trace_text_i[7:].strip().split(' ')
                for tmp_trace_i in tmp_trace:
                    if ("=" in tmp_trace_i) and ('<' not in tmp_trace_i):
                        # globalvariables
                        var_name, var_val = tmp_trace_i.split('=')
                        globalvar_name.append(var_name.strip())
                        globalvar_val.append(var_val.strip())
                    elif ('<' in tmp_trace_i) and ('-' in tmp_trace_i):
                        # clockzones
                        clocks, clk_bound = [
                            x.strip() for x in tmp_trace_i.split('<')]
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
                        state_text.append(tmp_trace_i.strip())
                clock_constraints.append(ClockZone(clockzones_text))
                states.append(state_text)
                global_variables.append(
                    GlobalVar(globalvar_name, globalvar_val))
            elif trace_text_i.startswith('Transition'):
                # Transition: PHisAAVFast.Retro -> PHisAAVFast._id15 {t >= tCondMin; actNode1!; t = 0;} NHisA.Rest -> NHisA._id7 {1; actNode?; 1;}
                # [PHisAAVFast.Retro -> PHisAAVFast._id15 {t >= tCondMin; actNode1!; t = 0;
                # NHisA.Rest -> NHisA._id7 {1; actNode?; 1; '']
                tmp_trace = trace_text_i[12:].strip().split('}')[:-1]
                edges_list = []
                end_process = []
                sync_symbol = None
                start_process = None
                for tmp_trace_i in tmp_trace:
                    # [NHisA.Rest -> NHisA._id7,
                    #  1; actNode?; 1;
                    trans_comp, edge_trans = tmp_trace_i.split('{')
                    start_location, end_location = [
                        x.strip() for x in trans_comp.split('->')]
                    guard, sync, update = [x.strip()
                                           for x in edge_trans.split(';')[:-1]]
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
        self.__has_parse_raw = True

    def save_raw(self, file_name: str) -> None:
        """Save raw data to file.

        Args:
            file_name (str): file name.
        """
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(self.raw)

    def save(self, file_name: str) -> None:
        """Save self.__str__() to file.

        Args:
            file_name (str): file name.
        """
        with open(file_name, 'w', encoding='utf-8') as f:
            # 这里有parse_raw
            f.write(str(self))

    def trim_transitions(self, model_path: str) -> None:
        """It reads the `.xml` file and gets the mapping from formal parameters to real parameters, 
        then it replaces the formal parameters in the transitions with the real parameters.

        Args:
            model_path (str): The path of the `.xml` file.

        Raises:
            ValueError: When the `.xml` file is invalid.
        """
        self.__parse_raw()
        element_tree_root: ET.Element | None = ET.ElementTree(
            file=model_path).getroot()
        if element_tree_root is None:
            # When the `.xml` file is invalid.
            raise ValueError("Invalid UPPAAL template file")

        # Get template parameters from .xml file
        templates: Generator[ET.Element, None,
                             None] = element_tree_root.iterfind("template")
        param_map: Dict[str, List[str]] = dict()
        for template in templates:
            name_element: ET.Element | None = template.find("name")
            if name_element is None:
                # When the `.xml` file is invalid.
                raise ValueError("Invalid UPPAAL template file")

            name: str = name_element.text  # uppaal guaranteed this to have only one
            param_elememt: ET.Element | None = template.find(
                "parameter")  # uppaal guaranteed this to have only one
            if param_elememt is not None:
                param_map[name] = list(map(lambda item: item.strip().split(' ')[-1].replace('&', ''),
                                           param_elememt.text.split(',')))  # remove type and ref annotation
            else:
                param_map[name] = []

        # Get system components defination
        system_element: ET.Element | None = element_tree_root.find("system")
        if system_element is None:
            # When the `.xml` file is invalid.
            raise ValueError("Invalid UPPAAL template file")

        system_items: List[str] = list(filter(lambda line: len(line) > 0 and line.find("//") != 0 and line.count(' ') != len(line),  # remove comment and empty line
                                              system_element.text.replace("\r\n", "\n").replace('\t', '') .split("\n")))[:-1]  # unify "\n", remove "\t" and remove "system"

        source_map: Dict[str, Dict[str, str]] = dict()
        for item in system_items:
            name, constructor = item.replace(";", "").replace(
                " ", "").split('=')  # remove ';' and ' '
            left_brace_index: int = constructor.find('(')
            right_brace_index: int = constructor.find(')')
            # get the name of the constructor(template)
            constructor_name: str = constructor[:left_brace_index]
            # get corresponding param list
            real_param_list: List[str] = list(filter(lambda param: param != '',
                                                     constructor[left_brace_index + 1: right_brace_index].split(',')))
            # get constructor param list
            form_param_list: List[str] = param_map[constructor_name]

            # ? I am not sure if default value is allowed in UPPAAL
            # When the `.xml` file is invalid.
            assert len(real_param_list) == len(form_param_list), "Invalid UPPAAL template file"

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


class OneClockZone:
    """    
    Represents a single clock zone constraint in a timed automaton.

    This class encapsulates a constraint between two clock variables, typically used in the context of timed automata. It specifies a relationship between two clocks and a bound on their difference.
    """

    def __init__(self, clock1: str, clock2: str, is_equal: bool, bound_value: int):
        """clock1 - clock2 < or ≤ bound_value

        Args:
        clock1 (str): Name of the first clock variable.
        clock2 (str): Name of the second clock variable.
        is_equal (bool): Flag to indicate whether the constraint includes equality.
        bound_value (int): The bound value for the difference between the two clocks.
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
            str: Name of the first clock variable.
        """
        return self.__clock1

    @property
    def clock2(self) -> str:
        """clock1 - clock2 < or ≤ bound_value

        Returns:
            str: Name of the second clock variable.
        """
        return self.__clock2

    @property
    def is_equal(self) -> bool:
        """clock1 - clock2 < or ≤ bound_value

        Returns:
            bool: is_equal
        """
        return self.__is_equal

    @property
    def bound_value(self) -> int:
        """clock1 - clock2 < or ≤ bound_value

        Returns:
            int: bound_value
        """
        return self.__bound_value


class ClockZone:
    """Composed by `List` of `OneClockZone`.
    """

    def __init__(self, clockzones: List[OneClockZone]):
        """Composed by `List` of `OneClockZone`.

        For the `.xtr` trace, each state contains several clock zones.

        Args:
            clockzones (List[OneClockZone]): A list of OneClockZone objects.
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
             List[OneClockZone]: The list of OneClockZone objects.
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
        start_location (str): The starting location (state) of the edge in the process.
        end_location (str): The ending location (state) of the edge in the process.
        guard (str): The condition that must be true for the transition to occur.
        sync (str): The synchronization action associated with the transition.
        update (str): The action to be executed when the transition occurs.

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
        """Gets the start location (state) of the edge.

        Returns:
            str: The start location of the edge.
        """
        return self.__start_location

    @property
    def end_location(self) -> str:
        """Gets the end location (state) of the edge.

        Returns:
            str: The end location of the edge.
        """
        return self.__end_location

    @property
    def guard(self) -> str:
        """
        Gets the guard condition of the edge.

        The guard condition must be true for the transition to occur. If the guard is '1', it implies the absence of a specific guard condition.

        Returns:
            str: The guard condition of the edge.
        """
        return self.__guard

    @property
    def has_guard(self) -> bool:
        """
        Determines if the edge has a guard condition.

        Returns:
            bool: True if the edge has a guard condition, False otherwise.
        """
        return self.__guard != '1'

    @property
    def sync(self) -> str:
        """
        Gets the synchronization action of the edge.

        The synchronization action is used for coordinating transitions between different processes.

        Returns:
            str: The synchronization action of the edge.
        """
        return self.__sync

    @property
    def update(self) -> str:
        """
        Gets the update action of the edge.

        The update action is executed when the transition occurs.

        Returns:
            str: The update action of the edge.
        """
        return self.__update

    @property
    def process(self) -> str:
        """
        Gets the process to which the edge belongs.

        Returns:
            str: The name of the process.
        """
        return self.__process

    @property
    def is_sync(self) -> bool:
        """
        Determines if the edge involves synchronization.

        Returns:
            bool: True if the edge involves synchronization, False otherwise.
        """
        return '!' in self.__sync or '?' in self.__sync

    @property
    def sync_type(self) -> str:
        """
        Gets the type of synchronization of the edge.

        The synchronization type can be 'send' (denoted by '!') or 'receive' (denoted by '?').

        Returns:
            str: The synchronization type ('send', 'receive', or None if not applicable).
        """
        if self.is_sync:
            return 'send' if '!' in self.__sync else 'receive'
        return None

    @property
    def sync_symbol(self) -> str:
        """
        Gets the symbol used for synchronization in the edge.

        The symbol represents the event or message involved in the synchronization.

        Returns:
            str: The synchronization symbol, or None if synchronization is not applicable.
        """
        if self.is_sync:
            return self.__sync[:-1]
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
        """
        Initializes a new instance of the Transition class.

        Args:
            sync (str): The synchronization symbol for the transition.
            start_process (str): The name of the start process.
            end_process (List[str]): A list of names of the end processes.
            edges (List[Edges], optional): A list of Edges defining the transition. Defaults to None.
        """
        self.__sync = sync
        self.__start_process = start_process
        self.__end_process = end_process
        self.__edges = edges or []

    def __str__(self):
        """
        Returns a string representation of the transition.

        Format: 'sync: start_process -> end_process; Edge details...'

        Returns:
            str: The string representation of the transition.
        """
        res = f'{self.__sync}: {self.__start_process} -> {", ".join(self.__end_process)}; '
        for edge in self.__edges:
            res += f'{edge.start_location} -> {edge.end_location}; '
        return res.strip()

    def __repr__(self):
        """
        Returns a formal string representation of the Transition object.

        Returns:
            str: Formal string representation of the object.
        """
        return self.__str__()

    @property
    def sync(self) -> str:
        """
        Gets the synchronization symbol of the transition.

        Returns:
            str: The synchronization symbol.
        """
        return self.__sync

    @property
    def start_process(self) -> str:
        """
        Gets the start process of the transition.

        Returns:
            str: The name of the start process.
        """
        return self.__start_process

    @property
    def end_process(self) -> List[str]:
        """
        Gets the end processes of the transition.

        Returns:
            List[str]: The names of the end processes.
        """
        return self.__end_process

    @property
    def edges(self) -> List[Edges]:
        """
        Gets the edges that make up the transition.

        Returns:
            List[Edges]: The list of edges.
        """
        return self.__edges

    @property
    def action(self) -> str:
        """
        Gets the action associated with the transition, typically the sync symbol.

        Returns:
            str: The action of the transition.
        """
        return self.__sync


class GlobalVar:
    """
    Represents global variables in a process model.

    Global variables are shared across different components of the model and can be used to store and manipulate data that is globally accessible.
    """
    def __init__(self, variables_name: List[str], variables_value: List[float]):
        """
        Initializes a new instance of the GlobalVar class.

        Args:
            variables_name (List[str]): A list of names for the global variables.
            variables_value (List[float]): A list of values for the global variables.
        """
        self.variables_name = variables_name
        self.variables_value = variables_value

    def __str__(self):
        """
        Returns a string representation of the global variables.

        Format: '[variable1=value1; variable2=value2; ...]'

        Returns:
            str: The string representation of the global variables.
        """
        res = '['
        for variable_name, variable_value in zip(self.variables_name, self.variables_value):
            res += f'{variable_name}={variable_value}; '
        res = res.strip('; ') + ']'
        return res

    def __repr__(self):
        """
        Returns a formal string representation of the GlobalVar object.

        Returns:
            str: Formal string representation of the object.
        """
        return self.__str__()
