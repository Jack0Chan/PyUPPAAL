# 这一行的import能够指定class的method返回自身类
# 参考链接：https://www.nuomiphp.com/eplan/11188.html
from __future__ import annotations
from collections import namedtuple
from typing import List, Tuple, Dict
import xml.etree.cElementTree as ET
from .verifyta import Verifyta


# ClockZone = namedtuple('ClockZone', ['clock1', 'clock2', 'is_equal', 'bound_value'])
# Transition = namedtuple('Transition', ['sync', 'start_process', 'end_process'])

class ClockZone:
    def __init__(self, clock1: str, clock2: str, is_equal: bool, bound_value: int):
        """
        clock1 - clock2 < or ≤ bound_value
        """
        self.clock1: str = clock1
        self.clock2: str = clock2
        self.is_equal: bool = is_equal
        self.bound_value: int = bound_value

    def __str__(self):
        sign = '≤' if self.is_equal else '<'
        res = f'{self.clock1} - {self.clock2} {sign} {self.bound_value}'
        return res


class Transition:
    def __init__(self, sync: str, start_process: str, end_process: List[str], edges: List[str]):
        self.sync: str = sync
        self.start_process: str = start_process
        self.end_process: List[str] = end_process
        # 这个edges暂时没用，但是我们也先存下来了。
        self.edges: List[str] = edges

    def __str__(self):
        res = f'{self.sync}: {self.start_process} -> {self.end_process}'
        return res


class SimulationTrace:
    def __init__(self, states: List[List[str]], clock_constraints: List[ClockZone], transitions: List[Transition]):
        """
        第i个state和第i个transition有相同的clock constraints
        第i个transition前面跟第i个state，详情看__str__()
        """
        # 注意三者长度, 前期开发用，后发布时候续注释掉
        if len(states) == len(clock_constraints) == len(transitions) + 1:
            pass
        else:
            raise ValueError(f'length should satisfy: len(states) == len(clock_constraints) == len(transitions) + 1\n'
                             f'current length: len(states) = {len(states)}, '
                             f'len(clock_constraints) = {len(clock_constraints)}, '
                             f'len(transitions) + 1 = {len(transitions) + 1}.')
        self.__states: List[List[str]] = states
        self.__global_variables = None
        self.__clock_constraints: List[ClockZone] = clock_constraints
        self.__transitions: List[Transition] = transitions

    @property
    def states(self):
        return self.__states

    @property
    def clock_constraints(self):
        return self.__clock_constraints

    @property
    def transitions(self):
        return self.__transitions

    @property
    def actions(self) -> List[str]:
        # __transitions里的sync（action）
        res = []
        return res

    def __str__(self):
        raise NotImplementedError
        res = ''
        return res

    def filter_by_actions(self, actions: List[str]) -> SimulationTrace:
        """
        filter edges by actions
        return 保留edges以及clock constraints
        """
        pass

    def filter_by_clocks(self, concerned_clocks: List[str], is_both: bool) -> SimulationTrace:
        if is_both:
            pass
        else:
            pass
        pass


class Tracer:
    """
    用来分析由命令行验证得到的xml格式的trace
    """

    @staticmethod
    def get_timed_trace(trace_path: str) -> List[Tuple[str, str, str]]:
        """
        获取trace_path的trace以及每个转移状态对应的gclk的区间
        注意由于UPPAAL验证返回的限制，这个trace并不是具体的时间，而是gclk的限制
        能够帮助我们构建更快速验证的Monitor，但是不一定能帮我们划分参数
        返回
        List[Tuple[str, str, str]]，即List<(Signal, lower_bound(类似guard), upper_bound(类似inv))>
        """
        pass

    @staticmethod
    def get_timed_pattern(trace_path: str) -> List[Tuple[str, str, str]]:
        """
        利用convert_trace_to_pattern函数将trace转化为易读的pattern
        能够帮助我们构建更快速验证的Monitor，但是不一定能帮我们划分参数
        """
        pass

    @staticmethod
    def get_transition_clock_bounds(trace_path: str) -> List[Dict[str, Dict[str, Tuple[str, int]]]]:
        """
        获取trace_path的clock_bounds
        trace_path: trace的xml路径
        return clock_bounds的列表
                clock_bounds里的每个Dict代表着（key减value）的取值范围
                比如 {'clock A':{'clock B':["<=",5]}}的意思是
                'clock A-clock B <= 5'

                clock_bound['clock A']['clock B'] = ('<=', 5)
        """
        et = ET.ElementTree(file=trace_path)

        nodes = list()
        for node in et.iter('node'):
            # node.attrib 示例
            # {'id': 'State42', 'location_vector': 'LocVec42', 'dbm_instance': 'DBM42 ', 'variable_vector': 'varvec.1'}
            # attrib_id = node.attrib['id']
            nodes.append(node.attrib['dbm_instance'][:-1])
        # print(nodes)

        # 将dbm按照"DBM1","DBM2"的顺序进行排序
        dbms = []
        i = 1
        while nodes:
            dbm = 'DBM' + str(i)
            if nodes.count(dbm) == 0:
                i += 1
                continue
            else:
                index = nodes.index(dbm)
                dbms.append(nodes[index])
                nodes.pop(index)
        # print(dbms)

        # 寻找所有的dbm_instance
        dbm_instances = {}
        for dbm_instance in et.iter('dbm_instance'):
            dbm_instances[dbm_instance.attrib['id']] = dbm_instance

        # 将所有的dbm_instance的信息按照dbm的顺序进行储存
        transition_clock_bounds = []
        for dbm in dbms:
            dbm_instance = dbm_instances[dbm]
            transition_clock_bound = dict()
            for child in dbm_instance:
                attrib = child.attrib
                # {'clock1': 'NHisV.t', 'clock2': 'NHisV.t', 'bound': '0', 'comp': '<='}
                key_a = attrib['clock1']
                key_b = attrib['clock2']
                val = (attrib['comp'], int(attrib['bound']))
                if key_a in transition_clock_bound:
                    transition_clock_bound[key_a].update({key_b: val})
                else:
                    transition_clock_bound.update({key_a: {key_b: val}})

            transition_clock_bounds.append(transition_clock_bound)

        return transition_clock_bounds

    @staticmethod
    def get_edge_clock_bounds(trace_path: str) -> [Dict[str, List[Tuple[Tuple[str, int], Tuple[str, int]]]]]:
        """
        获取trace_path的edge对应的clock_bounds
        trace_path: trace的xml路径
        return 每条边对应的clock_bounds的列表
                edge对应的clock_bounds里的每个Dict代表着经过key的时间的取值范围
                比如{'PSAHisA.Edge2': [(('>=', 0), ('<=', 28)), (('>=', 0), ('<=', 28))]}的意思是
                '经过PSAHisA.Edge2两次，第一次时间t>=0且t<=28, 第二次t>=0且t<=28'
        """

        et = ET.ElementTree(file=trace_path)

        # 为get_transition_clock_bounds函数
        nodes = list()
        for node in et.iter('node'):
            # node.attrib 示例
            # {'id': 'State42', 'location_vector': 'LocVec42', 'dbm_instance': 'DBM42 ', 'variable_vector': 'varvec.1'}
            # attrib_id = node.attrib['id']
            nodes.append(node.attrib['dbm_instance'][:-1])
        # print(nodes)

        # 将dbm按照"DBM1","DBM2"的顺序进行排序
        dbms = []
        i = 1
        while nodes:
            dbm = 'DBM' + str(i)
            if nodes.count(dbm) == 0:
                i += 1
                continue
            else:
                index = nodes.index(dbm)
                dbms.append(nodes[index])
                nodes.pop(index)
        # print(dbms)

        # 寻找所有的dbm_instance
        dbm_instances = {}
        for dbm_instance in et.iter('dbm_instance'):
            dbm_instances[dbm_instance.attrib['id']] = dbm_instance

        # 将所有的dbm_instance的信息按照dbm的顺序进行储存
        transition_clock_bounds = []
        for dbm in dbms:
            dbm_instance = dbm_instances[dbm]
            transition_clock_bound = dict()
            for child in dbm_instance:
                attrib = child.attrib
                # {'clock1': 'NHisV.t', 'clock2': 'NHisV.t', 'bound': '0', 'comp': '<='}
                key_a = attrib['clock1']
                key_b = attrib['clock2']
                val = (attrib['comp'], int(attrib['bound']))
                if key_a in transition_clock_bound:
                    transition_clock_bound[key_a].update({key_b: val})
                else:
                    transition_clock_bound.update({key_a: {key_b: val}})

            transition_clock_bounds.append(transition_clock_bound)

        #     寻找transition对应的发出信号的边
        edge_clock_bounds = dict()
        count = 0
        # print(trace_path)
        for transition in et.iter('transition'):
            # transition.attrib 示例
            # {'from': 'State1', 'to': 'State2', 'edges': 'Input.Edge1 ConvertIn.Edge1 '}
            # print(transition.attrib)
            edge = transition.attrib['edges'].split(' ')[0]
            # print(edge)
            node = edge.split('.')[0]
            nodet = node + '.t'
            if nodet in transition_clock_bounds[count]:
                # print(edge)
                # print(transition_clock_bounds[count][nodet]['sys.t(0)'][1])
                # print(transition_clock_bounds[count]['sys.t(0)'][nodet][1])
                small = transition_clock_bounds[count]['sys.t(0)'][nodet]
                large = transition_clock_bounds[count][nodet]['sys.t(0)']
                small = (small[0].replace('<', '>'), small[1])
                value = (small, large)
                # print(value)
                if edge not in edge_clock_bounds:
                    edge_clock_bounds[edge] = [value]
                else:
                    edge_clock_bounds[edge].append(value)
            count += 1

        return edge_clock_bounds

    @staticmethod
    def get_parameter_edge(trace_path: str) -> Dict[str, List[str]]:
        """
        {'tERPMinSA': ['NSA.Edge3'], 'tCondMinSAHisA': ['PSAHisA.Edge2'], 'tERPMinHisA': ['NHisA.Edge3'],
        'tCondMinHisASP': ['PHisASP.Edge4'], 'tCondMinHisAFP': ['PHisAFP.Edge2'], 'tERPMinSP': ['NSP.Edge3'],
        'tERPMinFP': ['NFP.Edge4'], 'tCondMinSPHisH': ['PSPHisH.Edge2', 'PSPHisH.Edge5'], 'tCondMinFPHisH': [
        'PFPHisH.Edge2'], 'tERPMinHisH': ['NHisH.Edge3'], 'tCondMinHisHHisV': ['PHisHHisV.Edge2'], 'tERPMinHisV': [
        'NHisV.Edge3']}
        """
        parameter_edge = dict()
        et = ET.ElementTree(file=trace_path)
        for edge in et.iter('edge'):
            # edge.attrib 示例
            # {'id': 'NSA.Edge1', 'from': 'NSA.Rest', 'to': 'NSA._id2'}

            # from xml.etree.ElementTree import Element, tostring, fromstring
            # print(tostring(edge, encoding="unicode"))

            for guard in edge.iter('guard'):
                # t >= tERPMin
                text = guard.text
                if 't >= t' in guard.text:
                    edge = edge.attrib['id']
                    # print(edge.attrib['id'])
                    # NSA.Edge3

                    parameter = 't' + guard.text.split('t >= t')[1]
                    # print(guard.text.split('t >= t')[1])
                    # ERPMin

                    # ERPMin += SA
                    # parameter = ERPMinSA
                    parameter += edge.split('.')[0][1:]

                    if parameter in parameter_edge:
                        parameter_edge[parameter].append(edge)
                    else:
                        parameter_edge[parameter] = [edge]

        return parameter_edge

    @staticmethod
    def get_untime_trace(trace_path: str):
        """
        这里我们不调用get_timed_trace，因为可以减少对DBM的搜索，从而提高运行效率
        获取trace_path的untime的trace
        trace_path: trace的xml路径
        return transitions的列表
                transitions里的每个list的第0个元素是发送edge，后面的为接收edge
                比如['NSA.Edge2', 'PSAHisA.Edge1', 'Monitor.Edge1']的意思是
                'NSA.Edge2'发送信号给了'PSAHisA.Edge1'和'Monitor.Edge1'
        """
        et = ET.ElementTree(file=trace_path)
        # print('======== get_untime_trace', ET.dump(et))
        # 找到trace中所有的edges，方便为transitions的edges添加后缀
        # 比如'NSA.Edge1'添加'.actNode?'后缀变为'NSA.Edge1.actNode?'
        # edges长这样：
        '''
        <edge id="Monitor.Edge1" from="Monitor._id44" to="Monitor._id33">
                <guard>gclk &gt;= 0</guard>
                <sync>actPathSA?</sync>
                <update>1</update>
        </edge>
        '''
        # 构建edge: sync的字典
        # 例如：{'NSA.Edge1': 'actNode?', 'NSA.Edge2': 'actPath!'}
        edges = {}
        for edge in et.iter('edge'):
            # edge.attrib 示例  {'id': 'NSA.Edge1', 'from': 'NSA.Rest', 'to': 'NSA._id2'}
            attrib_id = edge.attrib['id']
            edges[attrib_id] = f"{attrib_id}.{edge.find('sync').text}"

        # 找到trace中所有的transitions
        # transitions长这样：
        '''
        <transition from="State1" to="State2" edges="Input.Edge1 ConvertIn.Edge1 "/>
        <transition from="State2" to="State3" edges="ConvertIn.Edge2 NSA.Edge1 "/>
        <transition from="State3" to="State4" edges="NSA.Edge2 PSAHisA.Edge1 Monitor.Edge1 "/>
        '''
        # transitions例子：['Input.Edge1', 'ConvertIn.Edge1', 'ConvertIn.Edge2']
        transitions = []
        for transition in et.iter('transition'):
            # transition.attrib: {'from': 'State1', 'to': 'State2', 'edges': 'Input.Edge1 ConvertIn.Edge1 '}
            tmp = transition.attrib['edges'].split(' ')
            tmp.pop()
            # 为transitions加后缀，比如
            # [['Input.Edge1', 'ConvertIn.Edge1'], ['ConvertIn.Edge2', 'NSA.Edge1']]变为
            # [['Input.Edge1.sigIn!', 'ConvertIn.Edge1.sigIn?'], ['ConvertIn.Edge2.actNodeSA!', 'NSA.Edge1.actNode?']]
            for i in range(len(tmp)):
                tmp[i] = edges[tmp[i]]
            transitions.append(tmp)

        # print(edges)
        return transitions, edges

    @staticmethod
    def convert_trace_to_pattern(untime_trace: List[List[str]], edge_signal_dict: Dict[str, str]):
        # 改为
        # convert_trace_to_pattern(trace: List[List[str, str, str]], edge_signal_dict: Dict[str, str])
        # -> List[List[str, str, str]]
        # 因为我们的pattern、trace等都定义为timed words
        """
        根据edge_signal_dict将Tracer.get_untime_trace()得到的untime_trace转化成可读信号
        edge_signal_dict示例：{'NSA.Edge2.actPath!': 'actPathSA!'}
        意思是将'NSA.Edge2.actPath!'替换为'actPathSA'
        """
        if edge_signal_dict is None:
            print('self.edge_signal_dict is None, untime_trace is: ')
            print(untime_trace)
        # pattern = [i[0] for i in untime_trace if 'tau' not in i[0]]
        # print(untime_trace)

        # pattern = [edge_signal_dict[i[0]] for i in untime_trace if i[0] in edge_signal_dict]
        pattern = [edge_signal_dict[i[0]] for i in untime_trace[0] if i[0] in edge_signal_dict]
        return pattern

    @staticmethod
    def get_untime_pattern(trace_path: str, edge_signal_dict: Dict[str, str]):
        """
        获取trace_path的untime的pattern，即所有的!actions，并根据edge_signal_dict替换成可读信号
        trace_path: str, xml trace的路径
        edge_signal_dict示例：{'NSA.Edge2.actPath!': 'actPathSA!'}
        意思是将'NSA.Edge2.actPath!'替换为'actPathSA'
        注意，为了方便构造edge_signal_dict，可以调用并打印Tracer.get_untime_trace()
        """

        untime_trace = Tracer.get_untime_trace(trace_path)
        # print('========== get_untime_pattern', trace_path, edge_signal_dict, untime_trace)
        return Tracer.convert_trace_to_pattern(untime_trace, edge_signal_dict)

    @staticmethod
    def validate_and_get_untime_pattern(model_path: str, trace_path: str, edge_signal_dict: Dict[str, str]):
        """
        验证并返回pattern
        model_path: str, 要验证的模型路径
        trace_path: str, 准备保存的trace路径
        """
        verify_res = Verifyta().simple_verify(model_path, trace_path)
        # print('validate_and_get_untime_pattern', verify_res)
        if 'Formula is satisfied' in verify_res:
            # 要创建一个新的trace path，因为如果trace_path是test.xml
            # 那么验证得到的模型应该是test1.xml
            trace_path = trace_path.replace('.xml', '1.xml')
            new_trace_path = trace_path
            pattern = Tracer.get_untime_pattern(new_trace_path, edge_signal_dict)
            # print('======== validate_and_get_untime_pattern', pattern, model_path, trace_path)
            return pattern
        else:
            return []

    @staticmethod
    def get_old_pattern_obs_events(trace_path, edge_signal_dict):
        trace_path = trace_path.replace('.xml', '1.xml')
        trace = Tracer.get_untime_trace(trace_path)[0]
        transition_clock_bounds = Tracer.get_transition_clock_bounds(trace_path)
        old_pattern_obs_events = []
        for i in range(len(trace)):
            transition = trace[i]
            if transition[0] in edge_signal_dict:
                signal = edge_signal_dict[transition[0]]
                signal = signal.replace('!', '?')
                transition_clock_bound = transition_clock_bounds[i]
                small = -transition_clock_bound['sys.t(0)']['sys.gclk'][1]
                large = transition_clock_bound['sys.gclk']['sys.t(0)'][1]
                old_pattern_obs_events.append((signal, 'gclk>=' + str(small), 'gclk<=' + str(large)))
        return old_pattern_obs_events

    @staticmethod
    def extract_simulation_trace(xtr_file: str) -> SimulationTrace:
        pass
