# coding=utf-8
from typing import List, Tuple, Dict
import xml.etree.cElementTree as ET
from .verifyta import Verifyta
from .iTools import UFactory
from .tracer import Tracer


class UModel:
    """
    载入UPPAAL模型，进行分析、编辑、验证、保存等操作
    """

    def __init__(self, model_path: str):
        # 模型路径，如 '../AVNRT_Initial_straight.xml'
        self.model_path: str = model_path
        self.element_tree: ET.ElementTree = ET.ElementTree(file=self.model_path)
        self.root_elem: ET.Element = self.element_tree.getroot()
        if not Verifyta().verifyta_path:
            raise ValueError('Path of verifyta is not set. Please do Verifyta().set_verifyta_path().')

    def save_model(self, new_model_path: str):
        with open(new_model_path, 'w') as f:
            self.element_tree.write(new_model_path, encoding="utf-8", xml_declaration=True)
        self.model_path = new_model_path

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
        self.save_model(tmp_model_path)
        # print(tmp_model_path)
        return Verifyta().simple_verify(tmp_model_path, trace_path)

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

    def get_queries(self):
        """
        返回queries的字符串
        """
        query_formula_elems = self.element_tree.findall('./queries/query/formula')
        queries = [query_elem.text for query_elem in query_formula_elems]
        return queries

    def __remove_queries(self):
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
        self.__remove_queries()
        # 然后构造queries并插入到模型中
        queries_elem = UFactory.queries(queries)
        self.root_elem.append(queries_elem)
        return self.get_queries()

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

    def add_monitor(self, monitor_name: str, signals: List[Tuple[str, str, str]], strict: bool = False):
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
        self.remove_template(monitor_name)
        monitor = UFactory.monitor(monitor_name, signals, start_id)
        if strict:
            monitor = UFactory.strict_monitor(monitor_name, signals, start_id)
        self.root_elem.insert(-2, monitor)
        # 将新到monitor加入到system中
        self.add_system(monitor_name)
        return None

    def add_monitor_allpatterns(self, monitor_name: str, signals: List[Tuple[str, str, str]], edge_signal_dict: Dict[str, str]):
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
        self.remove_template(monitor_name)
        monitor = UFactory.monitor_allpatterns(monitor_name, signals, start_id, edge_signal_dict)
        self.root_elem.insert(-2, monitor)
        # 将新到monitor加入到system中
        self.add_system(monitor_name)
        return None

    def add_input(self, signals: List[Tuple[str, str, str]], input_template_name: str = 'Input'):
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
        monitor = UFactory.input(input_template_name, signals, start_id)
        self.root_elem.insert(-2, monitor)
        # 将新到monitor加入到system中
        # self.add_system(input_name)
        return None

    def find_a_pattern(self, observable_events: List[Tuple[str, str, str]], trace_path):
        """
        注意这里的input已经在模型中，并且原模型不包含任何Monitor

        observable_events: List[Tuple[str, str, str]]
        在给定input和observation的情况下寻找所有可能的counter example
        基本思路：
        Monitor0: observable events
        Monitor1: 基于Monitor0返回的trace
        """
        # 设置路径
        # 新模型路径，不覆盖原模型
        new_model_path = self.model_path.replace('../Test/', '../Test/patterns_')
        # 将要保存的path路径
        # trace_path = f"{new_model_path.replace('.xml', '')}"

        patterns = []
        # 构建Monitor0
        self.add_monitor('Monitor0', observable_events, strict=True)
        # 设置验证语句
        self.set_queries(['E<> Monitor0.pass'])
        # 保存构建好的模型
        self.save_model(new_model_path)
        # 获取第0个pattern
        pattern = Tracer.validate_and_get_untime_pattern(new_model_path, trace_path, self.edge_signal_dict)
        return pattern

    def find_all_patterns(self, observable_events: List[Tuple[str, str, str]], trace_path):
        """
        注意这里的input已经在模型中，并且原模型不包含任何Monitor

        observable_events: List[Tuple[str, str, str]]
        在给定input和observation的情况下寻找所有可能的counter example
        基本思路：
        Monitor0: observable events
        Monitor1: 基于Monitor0返回的trace
        """
        # 设置路径
        # 新模型路径，不覆盖原模型
        # new_model_path = self.model_path.replace('../Test/', '../Test/patterns_')
        new_model_path = self.model_path.replace('../Umodel_test/', '../Umodel_test/patterns_')
        # 将要保存的path路径
        # trace_path = f"{new_model_path.replace('.xml', '')}"

        patterns = []
        # 构建Monitor0
        self.add_monitor('Monitor0', observable_events, strict=True)
        # 设置验证语句
        self.set_queries(['E<> Monitor0.pass'])
        # 保存构建好的模型
        self.save_model(new_model_path)
        # 获取第0个patterns
        pattern = Tracer.validate_and_get_untime_pattern(new_model_path, trace_path, self.edge_signal_dict)

        # 根据上一个pattern构建monitor并循环
        monitor_id = 0
        while len(pattern) != 0:
            # print('new_pattern:', pattern)
            patterns.append(pattern)
            monitor_id += 1
            # Method1:
            # 上一个pattern改为monitor的形式
            # 设置每个location的inv为observation的最大时间
            # old_pattern_obs_events = [(signal.replace('!', '?'), '', observable_events[-1][-1]) for signal in pattern]
            # Method2:改成timeTrace的时刻
            old_pattern_obs_events = Tracer.get_old_pattern_obs_events(trace_path, self.edge_signal_dict)
            # Method3:

            # 构建Monitor_k
            # print(old_pattern_obs_events)
            # self.add_monitor(f'Monitor{monitor_id}', old_pattern_obs_events)
            self.add_monitor_allpatterns(f'Monitor{monitor_id}', old_pattern_obs_events, self.edge_signal_dict)

            # 构造验证语句
            # 构造monitor.pass
            # !Monitor0.pass & !Monitor1.pass
            monitor_pass_str = ' && '.join([f'!Monitor{i}.pass' for i in range(1, monitor_id + 1)])
            # E<> !Monitor0.pass & !Monitor1.pass
            monitor_pass_str = f'E<> Monitor0.pass && {monitor_pass_str}'

            # 设置验证语句
            self.set_queries([monitor_pass_str])
            # 保存构建好的模型
            self.save_model(new_model_path)
            pattern = Tracer.validate_and_get_untime_pattern(new_model_path, trace_path, self.edge_signal_dict)
        # print(patterns)
        return patterns

    def new(self, a):
        # print(a)
        for key in a:
            self.key = a

