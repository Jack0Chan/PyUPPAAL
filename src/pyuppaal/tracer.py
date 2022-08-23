# 这一行的import能够指定class的method返回自身类
# 参考链接：https://www.nuomiphp.com/eplan/11188.html
from __future__ import annotations
from typing import List, Tuple, Dict
import xml.etree.cElementTree as ET
from .verifyta import Verifyta
from .config import *
import os
import platform


platform_system = platform.system()
tracer_custom = TRACER_CUSTOM_WINDOWS if platform.system() == 'Windows' else TRACER_CUSTOM_LINUX


# ClockZone = namedtuple('ClockZone', ['clock1', 'clock2', 'is_equal', 'bound_value'])
# Transition = namedtuple('Transition', ['sync', 'start_process', 'end_process'])

class OneClockZone:
    def __init__(self, clock1: str, clock2: str, is_equal: bool, bound_value: int):
        """
        clock1 - clock2 < or ≤ bound_value
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
        return self.__clock1

    @property
    def clock2(self) -> str:
        return self.__clock2

    @property
    def is_equal(self) -> bool:
        return self.__is_equal

    @property
    def bound_value(self) -> int:
        return self.__bound_value


class ClockZone:
    def __init__(self, clockzones: List[OneClockZone]):
        """
        ClockZone List
        """
        self.__clockzones: List[OneClockZone] = clockzones

    def __str__(self):
        res = f'[]'
        if len(self.clockzones) > 0:
            res = '['
            for i in range(len(self.clockzones)):
                res += f'{self.clockzones[i].__str__()}; '
            res += ']'
        return res

    def __repr__(self):
        return self.__str__()

    @property
    def clockzones(self) -> List[OneClockZone]:
        return self.__clockzones

class Edges:
    def __init__(self, start_location, end_location, Guard: str, Sync: str, Update: str):
        """Edges
        process.start_location -> process.end_location: {Guard, Sync, Update} 
        """
        # 下面变量名改为小写
        self.__start_location = start_location
        self.__end_location = end_location
        self.__Guard = Guard
        self.__Sync = Sync
        self.__Update = Update
        self.__process = self.start_location.split('.')[0]
        # self.is_sync = Sync != '0'
        # self.is_grard = Guard != '1'

    def __str__(self):
        res = f'{self.process}.{self.start_location} -> {self.process}.{self.end_location}:'
        res = res + f'{{{self.Guard};{self.Sync};{self.Update}}}'
        return res

    @property
    def start_location(self):
        return self.__start_location

    @property
    def end_location(self):
        return self.__end_location

    @property
    def Guard(self):
        return self.__Guard

    @property
    def Sync(self):
        return self.__Sync

    @property
    def Update(self):
        return self.__Update

    @property
    def process(self):
        return self.__process

    @property
    def is_sync(self):
        return self.Sync[-1] == '!' or self.Sync[-1] == '?'

    @property
    def sync_symbol(self):
        if self.is_sync:
            return self.Sync[:-1]
        else:
            return None

    @property
    def is_guard(self):
        return self.Guard != '1'

    @property
    def sync_type(self):
        if self.is_sync:
            return 'send' if self.Sync[-1] == '!' else 'receive'
        else:
            return None


class Transition:
    def __init__(self, sync: str, start_process: str, end_process: List[str], edges: List[Edges] = None):
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
        """
        GlobalVar: variables_name[i] = variables_value[i]
        """
        self.variables_name: List[str] = variables_name
        self.variables_value: List[float] = variables_value

    def __str__(self):
        res = f'[]'
        if len(self.variables_name) > 0:
            res = '['
            for i in range(len(self.variables_name)):
                res += f'{self.variables_name[i]}={self.variables_value[i]}; '
            res += ']'
        return res


class SimTrace:
    def __init__(self, states: List[List[str]] = [],
                 clock_constraints: List[ClockZone] = [],
                 transitions: List[Transition] = [],
                 global_variables: List[GlobalVar] = []):
        """
        第i个state和第i个transition有相同的clock constraints
        第i个transition前面跟第i个state，详情看__str__()
        """
        self.__states: List[List[str]] = states
        self.__global_variables: List[GlobalVar] = global_variables
        self.__clock_constraints: List[ClockZone] = clock_constraints
        self.__transitions: List[Transition] = transitions

        # check length correct
        # is_equal_conlen = len(self.__states) == len(self.__clock_constraints)
        # is_equal_tralen = len(self.__states) == len(
        #     self.__transitions) + 1 or (len(self.__states) == len(self.__transitions) == 0)
        # if not (is_equal_conlen and is_equal_tralen):
        #     raise ValueError(f'length should satisfy: len(states) == len(clock_constraints) == len(transitions) + 1\n'
        #                      f'current length: len(states) = {len(self.__states)}, '
        #                      f'len(clock_constraints) = {len(self.__clock_constraints)}, '
        #                      f'len(transitions) + 1 = {len(self.__transitions)+1}.')

    def __str__(self):
        res = ''
        for i in range(len(self.__states)):
            res += f'State [{i}]: {self.__states[i].__str__()}\n'
            res += f'global_variables [{i}]: {self.__global_variables[i].__str__()}\n'
            res += f'Clock_constraints [{i}]: {self.__clock_constraints[i].__str__()}\n'
            if i < len(self.__states) - 1:
                res += f'transitions [{i}]: {self.__transitions[i].__str__()}\n'
                res += f'-----------------------------------\n'
        return res

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

    def set_empty(self) -> None:
        self.__states: List[List[str]] = []
        self.__global_variables: List[GlobalVar] = []
        self.__clock_constraints: List[ClockZone] = []
        self.__transitions: List[Transition] = []

    def filter_by_index(self, index_array: List[int]) -> SimTrace:
        # 改为slice方法
        """通过下标索引筛选出对应的SimTrace

        Args:
            index_array (List[int]): 索引

        Returns:
            SimTrace: 返回一个SimTrace对象
        """
        new_states = [self.__states[i] for i in range(len(self.__states)) if i in index_array]
        new_clock_cons = [self.__clock_constraints[i] for i in range(len(self.__clock_constraints)) if i in index_array]
        new_transitions = [self.__transitions[i] for i in range(len(self.__transitions)) if i in index_array]
        new_global_var = [self.__global_variables[i] for i in range(len(self.__global_variables)) if i in index_array]
        new_simtrace = SimTrace(new_states, new_clock_cons, new_transitions, new_global_var)
        return new_simtrace

    def filter_by_actions(self, focused_actions: List[str]=None) -> SimTrace:
        """
        filter edges by actions
        return 保留edges以及clock constraints
        """
        if focused_actions is None:
            return self
        
        index_array = [i for i in range(len(self.transitions)) if self.transitions[i].action in focused_actions]
        return self.filter_by_index(index_array)


    # def filter_by_clocks(self, concerned_clocks: List[str], is_both: bool) -> SimTrace:
    #     """通过clockZone筛选trace

    #     Args:
    #         concerned_clocks (List[str]): _description_
    #         is_both (bool): _description_

    #     Returns:
    #         SimTrace: _description_
    #     """
    #     if is_both:
    #         pass
    #     else:
    #         pass
    #     pass
    #     raise NotImplementedError('NotImplementedError') 


class Tracer:
    """
    用来分析由命令行验证得到的xtr格式的trace
    """

    @staticmethod
    def get_timed_trace(model_path: str, trace_path: str, hold: bool=False) -> SimTrace:
        """
        获取trace_path的trace以及每个转移状态对应的gclk的区间
        注意由于UPPAAL验证返回的限制，这个trace并不是具体的时间，而是gclk的限制
        能够帮助我们构建更快速验证的Monitor，但是不一定能帮我们划分参数
        返回 一个 SimulationTrace class.

        hold: 保留中间生成文件(.if & .txt)
        """
        verifyta = Verifyta()
        # use Verifta to compile model_path to if format file
        if_file = verifyta.compile_to_if(model_path=model_path)
        file_path, file_ext = os.path.splitext(if_file)
        # use trcer_custom to generate txt file
        trace_txt = file_path +'.txt'
        cmd_command = f'{tracer_custom} {if_file} {trace_path} {trace_txt}'
        cmd_res = os.popen(cmd_command).read()
        # debug
        # print(cmd_command)
        # print(cmd_res)
        
        # check file exist
        if not os.path.exists(trace_txt):
            error_info = f'trace txt file {trace_txt} has not generated.'
            raise FileNotFoundError(error_info)
        # load trace txt file
        f = open(trace_txt, 'r')
        trace_text = f.readlines()
        f.close()

        # construct SimulationTrace instance
        clock_constraints, states, global_variables, transitions = [], [], [], []
        for tr_ind in range(len(trace_text)):
            state_text, globalvar_name, globalvar_val, clockzones_text, transitions_text = [], [], [], [], []
            if trace_text[tr_ind].startswith('State'):
                tmp_trace_i = trace_text[tr_ind][7:].strip().split(' ')
                # print(trace_text[tr_ind][7:].strip())
                for tr_sub in range(len(tmp_trace_i)):
                    if ("=" in tmp_trace_i[tr_sub]) and ('<' not in tmp_trace_i[tr_sub]):
                        # globalvariables
                        var_name, var_val = tmp_trace_i[tr_sub].split('=')
                        globalvar_name.append(var_name.strip())
                        globalvar_val.append(var_val.strip())
                    elif ('<' in tmp_trace_i[tr_sub]) and ('-' in tmp_trace_i[tr_sub]):
                        # clockzones
                        # print(tmp_trace_i[tr_sub])
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
                global_variables.append(GlobalVar(
                    globalvar_name, globalvar_val))
                # print(clockzones_text[0].__str__())
                # print(state_text)
                # print(globalvar_name, globalvar_val)
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
            else:
                pass
        # remove if and txt file
        if not hold:
            os.remove(if_file)
            os.remove(trace_txt)
        return SimTrace(states, clock_constraints, transitions, global_variables)
