# coding=utf-8
from ast import Raise
import sys
from typing import List, Tuple, Dict
import xml.etree.cElementTree as ET

from pyuppaal.namedtuple import TimedActions
from .verifyta import Verifyta
from .iTools import UFactory
from .tracer import SimTrace, Tracer
import os

# verifyta_ins = Verifyta()

class UModel:
    """
    载入UPPAAL模型，进行分析、编辑、验证、保存等操作
    """

    def __init__(self, model_path: str):
        # 模型路径，如 '../AVNRT_Initial_straight.xml'
        self.model_path: str = model_path
        self.element_tree: ET.ElementTree = ET.ElementTree(file=self.model_path)
        self.root_elem: ET.Element = self.element_tree.getroot()
        if not Verifyta()._verifyta_path:
            raise ValueError('Path of verifyta is not set. Please do Verifyta().set_verifyta_path().')

    def get_model_path(self):
        return self.model_path

    def save(self):
        new_model_path = self.model_path
        with open(new_model_path, 'w') as f:
            self.element_tree.write(new_model_path, encoding="utf-8", xml_declaration=True)
        self.model_path = new_model_path
        return self.model_path

    def save_as(self, new_model_path: str):
        with open(new_model_path, 'w') as f:
            self.element_tree.write(new_model_path, encoding="utf-8", xml_declaration=True)
        self.model_path = new_model_path
        return new_model_path

    def copy_as(self, new_model_path: str):
        with open(new_model_path, 'w') as f:
            self.element_tree.write(new_model_path, encoding="utf-8", xml_declaration=True)
        # self.model_path = new_model_path
        return new_model_path
    
    def get_communication_graph(self, save_path=None):
        """
        get the communication graph of the uppaal model and save it to a `.md` file
        save_path: string, the path of aiming file
        return mermaid string
        """
        from iTools import build_cg
        mermaid = build_cg(self.model_path)
        if save_path is None:
            # rfind: 找到最右边的index
            # 如果直接从左find，那么下面这个路径就找不到
            # ../AVNRT_Initial_straight.md
            save_path = self.model_path[: self.model_path.rfind(".")] + "_CG.md"
        with open(save_path, "w") as f:
            f.write(mermaid)
        return mermaid

    def verify(self, trace_path: str):
        """
        验证模型，并将验证结果保存到trace_path中
        """
        # 取出文件名../AVNRT_Initial_straight.xml
        idx = self.model_path.rfind('/')
        # tmp_model_path: ../tmp_verify_AVNRT_Initial_straight.xml
        tmp_model_path = f'{self.model_path[:idx + 1]}tmp_verify_{self.model_path[idx + 1:]}'
        self.save(tmp_model_path)
        # print(tmp_model_path)
        return Verifyta().simple_verify(tmp_model_path, trace_path)

    def get_templates(self):
        """
        根据名字获取相应template的Element
        template_name: string, template的名字
        """
        return self.element_tree.iter("template")

    def get_template(self, template_name: str):
        """
        根据名字获取相应template的Element
        template_name: string, template的名字
        """
        for template in self.element_tree.iter("template"):
            if template.find('name').text == template_name:
                return template
        return None

    def remove_template(self, template_name: str):
        """
        删除指定的template
        template_name: string
        if template is not found, return False.
        if template is successfully removed, return True.
        """
        template_elem = self.get_template(template_name)
        if template_elem is None:
            return False
        self.root_elem.remove(template_elem)
        return True
    
    # def same_name_template(self, template_name: str):


    def clear_queries(self):
        """
        删除queries_elem
        主要被set_queries调用
        """
        root = self.root_elem
        queries_elem = root.find('queries')
        if queries_elem is None:
            return False
        root.remove(queries_elem)
        return True

    def set_queries(self, queries: List[str]):
        """
        设置query
        queries: List[str], query组成的list
        返回修改queries后的self.get_queries()
        """
        # 首先删除所有的queries
        self.clear_queries()
        # 然后构造queries并插入到模型中
        queries_elem = UFactory.queries(queries)
        self.root_elem.append(queries_elem)
        return self.get_queries()

    def get_queries(self):
        """
        返回queries的字符串
        """
        query_formula_elems = self.element_tree.findall('./queries/query/formula')
        queries = ''.join([query_elem.text for query_elem in query_formula_elems])
        return queries

    def get_system(self):
        """
        返回system的字符串
        """
        system_elem = self.element_tree.find('system')
        return system_elem.text

    def set_system(self, system_str: str):
        """
        修改system的字符串为system_str
        """
        system_elem = self.element_tree.find('system')
        system_elem.text = system_str
        return system_str

    def add_system(self, system_str: str):
        """
        添加system。值得注意的是，这里实现方法是简单拼接system_str到末尾，并调整好末尾分号的位置，
        那么，如果想添加多个system，比如test1和test2，那么直接传入'test1, test2'即可
        返回self.get_system()
        """
        current_system = self.get_system()
        new_system = f'{current_system[:current_system.rfind(";")]},{system_str};'
        self.set_system(new_system)
        return self.get_system()

    def get_declaration(self):
        """
        返回declaration的字符串
        """
        declaration_elem = self.element_tree.find('declaration')
        return declaration_elem.text

    def set_declaration(self, declaration_str: str):
        """
        设置整个declarations
        """
        declaration_elem = self.element_tree.find('declaration')
        declaration_elem.text = declaration_str
        return declaration_str

    def add_declaration(self, declaration_str: str):
        """
        添加一条新的语句到最后一行或者第一行
        """
        current_declaration = self.get_declaration()
        new_declaration = f'{current_declaration[:-1]},{declaration_str};'
        self.set_declaration(new_declaration)
        return self.get_declaration()

    def get_max_location_id(self) -> int:
        """
        获取当前模型最大的location_id，方便制造新的模板
        """
        location_elems = self.element_tree.findall('./template/location')
        # <location id="id0" x="-187" y="-76">
        # <location id="id1" x="25" y="-76">
        # <location id="id2" x="-51" y="-119">
        ids = [int(location_elem.attrib['id'][2:]) for location_elem in location_elems]
        return max(ids)

    def get_broadcast_chan(self) -> List[str]:
        declarations = self.get_declaration()
        systems = self.get_system()
        start_index = 0
        broadcast_chan = []
        while True:
            start_index = declarations.find('broadcast chan', start_index, -1)
            if start_index == -1:
                break
            end_index = declarations.find(';', start_index, -1)
            tmp_actions = declarations[start_index+15:end_index].strip().split(',')
            tmp_actions = [x.strip() for x in tmp_actions]
            broadcast_chan += tmp_actions
            start_index = end_index
        start_index = 0
        # while True:
        #     start_index = systems.find('broadcast chan', start_index, -1)
        #     if start_index == -1:
        #         break
        #     end_index = systems.find(';', start_index, -1)
        #     tmp_actions = systems[start_index+15:end_index].strip().split(',')
        #     tmp_actions = [x.strip() for x in tmp_actions]
        #     broadcast_chan += tmp_actions
        #     start_index = end_index
        return list(set(broadcast_chan))
            

    def add_monitor(self, monitor_name: str, signals: TimedActions, observe_actions: List[str] = None, 
                    strict: bool = False, allpattern: bool = False):
        """
        在<system></system>前添加新的线性monitor，并且自动添加到system中
        如果name有冲突，会自动替换原template
        monitor_name: string
                 signals: List[Tuple[str, str, str]],
                 每个Tuple分别对应[signal, guard, inv]
                 example: ['act_path!', 'gclk>=10', 'gclk<=10']
                 signal, guard, inv, name 都可以是None
                 signal: 信号名称
                 guard: int
                 inv: int
                 注意：在连接的时候是按照信号在list出现的顺序连接的
        startID: int, 用来设置Monitor中最小的startID, 防止id冲突
        strict: bool, 判断是否构建strict monitor，正常来说是false
        """
        # 处理observe_actions is None的情况
        if observe_actions is None:
            observe_actions = self.get_broadcast_chan()

        start_id = self.get_max_location_id() + 1
        # 删除相同名字的monitor
        self.remove_template(monitor_name)
        monitor = UFactory.monitor(monitor_name, signals.convert_to_list_tuple(), observe_actions, start_id, strict, allpattern)
        self.root_elem.insert(-2, monitor)
        # 将新到monitor加入到system中
        self.add_system(monitor_name)
        return None

    def add_input(self, input_template_name: str, signals: TimedActions):
        """
        在<system></system>前添加新的线性monitor，并且自动添加到system中
        如果name有冲突，会自动替换原template
        monitor_name: string
               signals: List[Tuple[str, int, int]],
                 每个Tuple分别对应[signal, guard, inv]
                 signal, guard, inv, name 都可以是None
                 signal: 信号名称
                 guard: int
                 inv: int
                 注意：在连接的时候是按照信号在list出现的顺序连接的
        startID: int, 用来设置Monitor中最小的startID, 防止id冲突
        strict: bool, 判断是否构建strict monitor，正常来说是false
        """
        start_id = self.get_max_location_id() + 1
        # 删除相同名字的monitor
        self.remove_template(input_template_name)
        input_model = UFactory.input(input_template_name, signals.convert_to_list_tuple(), start_id)
        self.root_elem.insert(-2, input_model)
        # 将新到monitor加入到system中
        self.add_system(input_template_name)
        return None

    def find_a_pattern(self, inputs: TimedActions, observes: TimedActions, 
                       observe_actions: List[str] = None, focused_actions: List[str] = None, hold=False, options = None):
        """
        inputs: 输入信号模块的TimedActions
        observers: 观测信号模块的TimedActions
        input_actions: 输入信号列表
        observe_actions
        """
        # 设置路径
        # 新模型路径，不覆盖原模型
        new_model_path = os.path.splitext(self.model_path)[0] + '_pattern.xml'
        self.copy_as(new_model_path=new_model_path)
        new_umodel = UModel(new_model_path)
        # 将要保存的path路径
        # trace_path = f"{new_model_path.replace('.xml', '')}"

        patterns = []
        # 构建Monitor0

        new_umodel.add_input('input0', inputs)
        new_umodel.add_monitor('Monitor0', observes, observe_actions=observe_actions, strict=True)
        # 设置验证语句
        query = 'E<> Monitor0.pass'
        new_umodel.set_queries([query])
        # 保存构建好的模型
        new_umodel.save()
        # 获取第0个pattern
        Verifyta().simple_verify(new_model_path, options=options)
        trace_path = os.path.splitext(new_model_path)[0] + '-1.xtr'
        if not os.path.exists(trace_path):
            return []

        # 通过Trace 得到 Simtrace对象
        simtrace = Tracer.get_timed_trace(new_model_path, trace_path)
        # focused_actions = list(set(input_actions + hidden_actions + observe_actions))
        # print(focused_actions)
        pattern_seq = simtrace.filter_by_actions(focused_actions)

        if not hold:
            os.remove(new_model_path)
            os.remove(trace_path)
        return query, pattern_seq.actions

    def find_all_patterns(self, inputs: TimedActions, observes: TimedActions, 
                          observe_actions: List[str]=None, focused_actions: List[str]=None, hold: bool=False, max_patterns: int=None):
        """
        注意这里的input已经在模型中，并且原模型不包含任何Monitor

        observable_events: List[Tuple[str, str, str]]
        在给定input和observation的情况下寻找所有可能的counter example
        基本思路：
        Monitor0: observable events
        Monitor1: 基于Monitor0返回的trace
        """
        # 首先
        monitor_pass_str, new_patterns = self.find_a_pattern(inputs, observes, observe_actions, focused_actions, hold=True)
        new_model_path = os.path.splitext(self.model_path)[0] + '_pattern.xml'
        new_umodel = UModel(new_model_path)
        
        # 根据初始的pattern构建monitor并循环, 初始Moniter为0
        all_patterns = []
        monitor_id = 0
        iter = 1
        while len(new_patterns) != 0 and (iter <= max_patterns) if max_patterns is not None else True:
            monitor_id += 1
            all_patterns.append((monitor_pass_str, new_patterns))
            # 将pattern[List] -> TimedActions
            new_observes = TimedActions(new_patterns)
            new_umodel.add_monitor(f'Monitor{monitor_id}', new_observes, observe_actions=focused_actions, strict=True, allpattern=True)

            # 构造验证语句
            # 构造monitor.pass
            # !Monitor0.pass & !Monitor1.pass
            monitor_pass_str = ' && '.join([f'!Monitor{i}.pass' for i in range(1, monitor_id+1)])
            # E<> !Monitor0.pass & !Monitor1.pass
            monitor_pass_str = f'E<> Monitor0.pass && {monitor_pass_str}'

            # 设置验证语句
            new_umodel.set_queries([monitor_pass_str])
            # 保存构建好的模型
            new_umodel.save()
            
            Verifyta().simple_verify(new_umodel.model_path)
            
            trace_path = os.path.splitext(new_umodel.model_path)[0] + '-1.xtr'
            if not os.path.exists(trace_path):
                return []
            
            # 通过Trace 得到 Simtrace对象
            simtrace = Tracer.get_timed_trace(new_umodel.model_path, trace_path)
            new_patterns = simtrace.filter_by_actions(focused_actions).actions
            iter = iter + 1
        if not hold:
            os.remove(new_model_path)
            os.remove(trace_path)

        return all_patterns


    def find_a_pattern_with_query(self, query: str = None, focused_actions: List[str] = None, hold=False, options=None):
        """
        input_actions: 输入信号列表
        observe_actions
        """
        # 设置路径
        # 新模型路径，不覆盖原模型
        new_model_path = os.path.splitext(self.model_path)[0] + '_pattern.xml'
        self.copy_as(new_model_path=new_model_path)
        new_umodel = UModel(new_model_path)
        
        if query is not None:
            new_umodel.set_queries(queries=query)

        Verifyta().simple_verify(new_model_path,options=options)
        trace_path = os.path.splitext(new_model_path)[0] + '-1.xtr'
        if not os.path.exists(trace_path):
            return []
        
        # 通过Trace 得到 Simtrace对象
        simtrace = Tracer.get_timed_trace(self.model_path, trace_path)
        # focused_actions = list(set(input_actions + hidden_actions + observe_actions))
        # print(focused_actions)
        pattern_seq = simtrace.filter_by_actions(focused_actions)

        if not hold:
            os.remove(new_model_path)
            os.remove(trace_path)

        return new_umodel.get_queries(), pattern_seq.actions
    
    def find_all_patterns_with_query(self, query: str=None, focused_actions: List[str]=None, hold: bool=False, max_patterns: int=None):
        """
        注意这里的input已经在模型中，并且原模型不包含任何Monitor

        observable_events: List[Tuple[str, str, str]]
        在给定input和observation的情况下寻找所有可能的counter example
        基本思路：
        Monitor0: observable events
        Monitor1: 基于Monitor0返回的trace
        """
        # 首先
        query = query.strip()
        if not (query.startswith('A[]') or query.startswith('E<>')):
            raise NotImplementedError('Only support E<> and A[] query!')
        
        if query.startswith('A[]'):
            default_query = query[3:].strip()
            if default_query[0] == '!':
                default_query = "E<> " + default_query[1:].strip()
            elif default_query[0:3] == "not":
                default_query = "E<> " + default_query[3:].strip()
            else:
                default_query = "E<> ! " + default_query.strip()
        else:
            default_query = query
        default_query, new_patterns = self.find_a_pattern_with_query(default_query, focused_actions, hold=True)
        new_model_path = os.path.splitext(self.model_path)[0] + '_pattern.xml'
        new_umodel = UModel(new_model_path)
        monitor_pass_str = default_query
        # 根据初始的pattern构建monitor并循环, 初始Moniter为0
        all_patterns = []
        monitor_id = 0
        iter = 1
        while len(new_patterns) != 0:
            all_patterns.append((monitor_pass_str, new_patterns))
            if max_patterns is not None and iter >= max_patterns:
                break
            monitor_id += 1
            # 将pattern[List] -> TimedActions
            new_observes = TimedActions(new_patterns)
            new_umodel.add_monitor(f'Monitor{monitor_id}', new_observes, observe_actions=focused_actions, strict=True, allpattern=True)

            # 构造验证语句
            # 构造monitor.pass
                # E<> Monitor0.pass & !Monitor1.pass
            monitor_pass_str = ' && '.join([f'!Monitor{i}.pass' for i in range(1, monitor_id+1)])
            # E<> !Monitor0.pass & !Monitor1.pass
            monitor_pass_str = f'{default_query} && {monitor_pass_str}'
                
            
            # 设置验证语句
            new_umodel.set_queries([monitor_pass_str])
            # 保存构建好的模型
            new_umodel.save()
            
            Verifyta().simple_verify(new_umodel.model_path)
            
            trace_path = os.path.splitext(new_umodel.model_path)[0] + '-1.xtr'
            if not os.path.exists(trace_path):
                return []
            
            # 通过Trace 得到 Simtrace对象
            simtrace = Tracer.get_timed_trace(new_umodel.model_path, trace_path)
            new_patterns = simtrace.filter_by_actions(focused_actions).actions
            iter = iter + 1
        if not hold:
            os.remove(new_model_path)
            os.remove(trace_path)
        return all_patterns