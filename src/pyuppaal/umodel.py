# support return typing UModel
from __future__ import annotations

# system powershell
from subprocess import run

# coding=utf-8
from typing import List
import xml.etree.cElementTree as ET

from .datastruct import TimedActions
from .verifyta import Verifyta
from .iTools import UFactory, build_cg
from .tracer import SimTrace, Tracer
import os


class UModel:
    """
    Load UPPAAL model for analysis, editing, verification and storage operations.

    :param str model_path: the path of model file
    """

    def __init__(self, model_path: str):
        # 模型路径，如 '../AVNRT_Initial_straight.xml'
        self.__model_path: str = model_path
        self.__element_tree: ET.ElementTree = ET.ElementTree(
            file=self.model_path)
        self.__root_elem: ET.Element = self.__element_tree.getroot()
        # if not Verifyta().verifyta_path:
        #     raise ValueError('Path of verifyta is not set. Please do Verifyta().set_verifyta_path(xxx).')

    @property
    def model_path(self) -> str:
        """
        :return: the path of model file
        """
        return self.__model_path

    def save_as(self, new_model_path: str) -> UModel:
        """
        Store the model file to a new path with the original `model_path` changed.

        :param str new_model_path: a new path to store
        :return: the saved Umodel
        """
        with open(new_model_path, 'w') as f:
            self.__element_tree.write(
                new_model_path, encoding="utf-8", xml_declaration=True)
        self.__model_path = new_model_path
        return UModel(new_model_path)

    def copy_as(self, new_model_path: str) -> UModel:
        """
        store the model file to a new path with the original `model_path` unchanged.

        :param str new_model_path: a new path to store
        :return: the copied Umodel
        """
        with open(new_model_path, 'w') as f:
            self.__element_tree.write(
                new_model_path, encoding="utf-8", xml_declaration=True)
        return UModel(new_model_path)

    def save(self) -> UModel:
        """
        Store the model file to the original path

        :return: the original Umodel
        """
        new_model_path = self.model_path
        return self.save_as(new_model_path)

    def get_communication_graph(self, save_path=None) -> None:
        """
        Get the communication graph of the uppaal model and save it to a `<.md | .svg | .png | .pdf>` file.

        :param str save_path: `<.md | .svg | .png | .pdf>` the path to save graph file
        :return: None
        """
        
        # if save_path is None:
        # rfind: 找到最右边的index
        # 如果直接从左find，那么下面这个路径就找不到
        # ../AVNRT_Initial_straight.md
        
        mermaid = build_cg(self.model_path)
        # do something with mermaid
        mermaid = merge_mermaid(mermaid)
        
        temp_path = self.model_path[: self.model_path.rfind(".")] + "_CG.md"
        with open(temp_path, "w") as f:
            f.write(mermaid)
        if save_path==None:
            return None
        if save_path.endswith(".svg") or save_path.endswith(".png") or save_path.endswith(".pdf"):
            cmd='mmdc -i ' + temp_path + ' -o ' + save_path
            # cmd = 'mmdc -i ' + temp_path + ' -o ' + save_path +' -t dark -b transparent'
            # run('Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass',shell=True)
            run(cmd, shell=True)
            os.remove(temp_path)

    def cg_mermaid_to_list(mermaid_str: str) -> List[List[str]]:
        """
        Transform from mermaid to List[source, edge_name, target]

        # FROM:
        # mermaid_str = mermaid
        # graph TD
        # TrafficLights
        # LV1Pedestrian2
        # Cars
        # TrafficLights--cGreen-->Cars
        # TrafficLights--cYellow-->Cars
        # LV1Pedestrian2--pCrss-->Cars

        # TO:
        # [[TrafficLights, cGreen, Cars],
        #  [TrafficLights, cYellow, Cars],
        #  [LV1Pedestrian2, pCrss, Cars]]
         
        """
        
        # 去掉开头和结尾的冗余
        mermaid_list = mermaid_str.replace('```', '').split('\n')
        res = []
        for i in mermaid_list:
            if '--' in i:
                # i TrafficLights--cYellow-->Cars 变成 [TrafficLights, cYellow, Cars]
                res.append(i.replace('>', '').split('--'))

        return res

    def merge_edges(mermaid_list: List[List[str]]) -> Dict:
        """
        Transform from List[source, edge_name, target] to dict

        # FROM:
        # [[TrafficLights, cGreen, Cars],
        # [TrafficLights, cYellow, Cars],
        # [LV1Pedestrian2, pCrss, Cars]]

        # TO:
        # {"[TrafficLights, Cars]": [cGreen, cYellow]
        # "[LV1Pedestrian2, Cars]" : [pCrss]}
        """
        
        edges_dict = {}
        for i in mermaid_list:
            key = str([i[0], i[2]])
            value = i[1]
            if key in edges_dict:
                edges_dict[key].append(value)
            else:
                edges_dict[key] = [value]
        # remove duplicate
        for key in edges_dict:
            edges_dict[key] = sorted(list(set(edges_dict[key])))
        return edges_dict


    def dict_to_mermaid(edges_dict: Dict, join_str: str = ',') -> str:
        """
        Transform from dict to mermaid

        # FROM:
        # {"[TrafficLights, Cars]": [cGreen, cYellow]
        # "[LV1Pedestrian2, Cars]" : [pCrss]}

        # TO:
        # mermaid
        # graph TD
        # TrafficLights--cGreen,cYellow-->Cars
        # LV1Pedestrian2--pCrss-->Cars
        """
        edges_str = ''
        for key in edges_dict:
            # str转list获取边的两端
            [source, target] = eval(key)
            edge_name = join_str.join(edges_dict[key])
            edges_str += f"{source}--{edge_name}-->{target}\n"
        res = f'''```mermaid\ngraph TD\n{edges_str}```'''
        return res

    def merge_mermaid(mermaid_str: str) -> str:
        mermaid_list = cg_mermaid_to_list(mermaid_str)
        edges_dict = merge_edges(mermaid_list)
        res = dict_to_mermaid(edges_dict)
        return res

    def filter_mermaid(mermaid_str: str, excluded_component: List[str]) -> str:
        res = ''
        for i in mermaid_str.split('\n'):
            for j in excluded_component:
                if j not in i:
                    res += f'{i}\n'
        return res


    def verify(self, trace_path: str) -> str:
        """
        Verify the model, and save the result in `trace_path`, `< .xtr | .xml>`.

        :param str trace_path: the path of trace file, `< .xtr | .xml>`
        :return: the path of verification result
        """
        # 取出文件名../AVNRT_Initial_straight.xml
        idx = self.model_path.rfind('/')
        # tmp_model_path: ../tmp_verify_AVNRT_Initial_straight.xml
        tmp_model_path = f'{self.model_path[:idx + 1]}tmp_verify_{self.model_path[idx + 1:]}'
        self.save(tmp_model_path)
        # print(tmp_model_path)
        return Verifyta().simple_verify(tmp_model_path, trace_path)[0]


# templates


    def get_templates(self) -> List[str]:
        """
        :return: the element of template in `List[str]` type
        """
        return self.__element_tree.iter("template")

    def get_template(self, template_name: str) -> str:
        """
        Get the element according to the input name.

        :param str template_name : the name of template
        :return: the element of template in `str` type
        """
        for template in self.__element_tree.iter("template"):
            if template.find('name').text == template_name:
                return template
        return None

    def remove_template(self, template_name: str) -> bool:
        """
        Delete the template according to the input name.

        :param str template_name: the name of template
        :return: `True` when succeed, `False` when fail
        """
        template_elem = self.get_template(template_name)
        if template_elem is None:
            return False
        self.__root_elem.remove(template_elem)
        return True


# queries


    def get_queries(self) -> List[str]:
        """
        :return: the str list of queries
        """
        query_formula_elems = self.__element_tree.findall(
            './queries/query/formula')
        queries = ''.join(
            [query_elem.text for query_elem in query_formula_elems])
        return queries

    def clear_queries(self) -> bool:
        """
        Delete `queries_elem`, mainly called by `set_queries`
        """
        root = self.__root_elem
        queries_elem = root.find('queries')
        if queries_elem is None:
            return False
        root.remove(queries_elem)
        return True

    def set_queries(self, queries: List[str]) -> None:
        """
        :param List[str] queries: list of queries
        :return: `self.get_queries()` after setting queries
        """
        # 首先删除所有的queries
        self.clear_queries()
        # 然后构造queries并插入到模型中
        queries_elem = UFactory.queries(queries)
        self.__root_elem.append(queries_elem)


# system


    def get_system(self) -> str:
        """
        :return: the str of system
        """
        system_elem = self.__element_tree.find('system')
        return system_elem.text

    def set_system(self, system_str: str) -> None:
        """
        set the str of system to `system_str`

        :param str system_str: aiming str
        """
        system_elem = self.__element_tree.find('system')
        system_elem.text = system_str

    # def add_system(self, system_str: str) -> None:
    #     """
    #     添加system。值得注意的是，这里实现方法是简单拼接system_str到末尾，并调整好末尾分号的位置，
    #     那么，如果想添加多个system，比如test1和test2，那么直接传入'test1, test2'即可
    #     返回self.get_system()
    #     """
    #     current_system = self.get_system()
    #     new_system = f'{current_system[:current_system.rfind(";")]},{system_str};'
    #     self.set_system(new_system)

# declaration
    def get_declaration(self) -> str:
        """
        :return: str of declararion
        """
        declaration_elem = self.__element_tree.find('declaration')
        return declaration_elem.text

    def set_declaration(self, declaration_str: str) -> None:
        """
        set the str of declaration to `declaration_str`

        :param str declaration_str: aiming str
        """
        declaration_elem = self.__element_tree.find('declaration')
        declaration_elem.text = declaration_str

    # def add_declaration(self, declaration_str: str) -> None:
    #     """
    #     添加一条新的语句到最后一行或者第一行
    #     """
    #     current_declaration = self.get_declaration()
    #     new_declaration = f'{current_declaration[:-1]},{declaration_str};'
    #     self.set_declaration(new_declaration)

# other
    def get_max_location_id(self) -> int:
        """
        Get the maximum location_id so as to make it easier to create new template

        :return: the maximum location_id
        """
        location_elems = self.__element_tree.findall('./template/location')
        # <location id="id0" x="-187" y="-76">
        # <location id="id1" x="25" y="-76">
        # <location id="id2" x="-51" y="-119">
        ids = [int(location_elem.attrib['id'][2:])
               for location_elem in location_elems]
        return max(ids)

    def get_broadcast_chan(self) -> List[str]:
        """
        @yhc get broadcast channels in Declarations

        :return: `List[str]`, List of broadcast channels.
        """
        declarations = self.get_declaration()
        systems = self.get_system()
        start_index = 0
        broadcast_chan = []
        while True:
            start_index = declarations.find('broadcast chan', start_index, -1)
            if start_index == -1:
                break
            end_index = declarations.find(';', start_index, -1)
            tmp_actions = declarations[start_index +
                                       15:end_index].strip().split(',')
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


# all patterns

    def add_monitor(self, monitor_name: str, signals: TimedActions, observe_actions: List[str] = None, strict: bool = False, allpattern: bool = False,is_auto_save: bool = True):
        """
        Add new linear monitor template, it will also be embedded in `system declarations`. When conflicting, the original monitor will be overwritten.

        :param str monitor_name: the name of monitor
        :param TimedActions signals: specific data type `List[Tuple[signal, guard, inv]]`, `signal`, `guard` and `inv` are `str` type and can be `None`
        :param List[str] observe_actions: observe actions @yhc is there any observe_actions in Timed actions?
        :param bool strict: determine whether monitor is strict or not
        :param bool allpattern: determine whether allpattern is enabled
        """
        # 处理observe_actions is None的情况
        if observe_actions is None:
            observe_actions = self.get_broadcast_chan()

        start_id = self.get_max_location_id() + 1
        # 删除相同名字的monitor
        self.remove_template(monitor_name)
        monitor = UFactory.monitor(monitor_name, signals.convert_to_list_tuple(
        ), observe_actions, start_id, strict, allpattern)
        self.__root_elem.insert(-2, monitor)
        # 将新到monitor加入到system中
        cur_system = self.get_system()
        cur_system = cur_system.split('\n')
        cur_system = [x.strip() for x in cur_system]
        for i in range(len(cur_system)):
            if cur_system[i].startswith('system'):
                tmpl = cur_system[i][6:].split(',')
                tmpl = [y.strip() for y in tmpl]
                tmpl = [y.strip(';') for y in tmpl]
                if monitor_name not in tmpl:
                    tmpl.insert(0, monitor_name)
                cur_system[i] = 'system ' + ','.join(tmpl) + ';'
                break
        cur_system = '\n'.join(cur_system)
        self.set_system(cur_system)
        if is_auto_save== True:
            self.save()
        
        return None

    def add_input(self, input_template_name: str, signals: TimedActions):
        """
        Add new linear input template, it will also be embedded in `system declarations`.
        """
        start_id = self.get_max_location_id() + 1
        # 删除相同名字的monitor
        self.remove_template(input_template_name)
        input_model = UFactory.input(
            input_template_name, signals.convert_to_list_tuple(), start_id)
        self.__root_elem.insert(-2, input_model)
        # 将新到monitor加入到system中
        cur_system = self.get_system()
        cur_system = cur_system.split('\n')
        cur_system = [x.strip() for x in cur_system]
        for i in range(len(cur_system)):
            if cur_system[i].startswith('system'):
                tmpl = cur_system[i][6:].split(',')
                tmpl = [y.strip() for y in tmpl]
                tmpl = [y.strip(';') for y in tmpl]
                if input_template_name not in tmpl or input_template_name+';' not in tmpl:
                    tmpl.insert(0, input_template_name)
                cur_system[i] = 'system ' + ','.join(tmpl) + ';'
                break
        cur_system = '\n'.join(cur_system)
        self.set_system(cur_system)
        return None

    def find_a_pattern(self, inputs: TimedActions, observes: TimedActions,
                       observe_actions: List[str] = None, focused_actions: List[str] = None, hold=False, options: str = None):
        """
        :param TimedActions inputs: TimedActions of input signal model
        :param TimedActions observes: TimedActions of observe signal model
        :param List[str] input_actions: list of input signal
        :param List[str] observe_actions: list of observe signal
        :param bool hold: whether save history files
        :param str options: verifyta options
        :return: query, pattern_seq.actions @yhc SimTrace？
        """
        # 设置路径
        # 新模型路径，不覆盖原模型
        new_model_path = os.path.splitext(self.model_path)[0] + '_pattern.xml'
        new_umodel = self.copy_as(new_model_path=new_model_path)
        # 将要保存的path路径
        # trace_path = f"{new_model_path.replace('.xml', '')}"

        patterns = []
        # 构建Monitor0

        new_umodel.add_input('input0', inputs)
        new_umodel.add_monitor('Monitor0', observes,
                               observe_actions=observe_actions, strict=True)
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
                          observe_actions: List[str] = None, focused_actions: List[str] = None, hold: bool = False, max_patterns: int = None):
        """
        注意这里的input已经在模型中，并且原模型不包含任何Monitor

        observable_events: List[Tuple[str, str, str]]
        在给定input和observation的情况下寻找所有可能的counter example
        基本思路：
        Monitor0: observable events
        Monitor1: 基于Monitor0返回的trace

        :param TimedActions inputs: TimedActions of input signal model
        :param TimedActions observes: TimedActions of observe signal model
        :param List[str] input_actions: list of input signal
        :param List[str] observe_actions: list of observe signal
        :param bool hold: whether save history files
        :param str options: verifyta options
        :return: query, pattern_seq.actions @yhc SimTrace？
        """
        # 首先
        monitor_pass_str, new_patterns = self.find_a_pattern(
            inputs, observes, observe_actions, focused_actions, hold=True)
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
            new_umodel.add_monitor(f'Monitor{monitor_id}', new_observes,
                                   observe_actions=focused_actions, strict=True, allpattern=True)

            # 构造验证语句
            # 构造monitor.pass
            # !Monitor0.pass & !Monitor1.pass
            monitor_pass_str = ' && '.join(
                [f'!Monitor{i}.pass' for i in range(1, monitor_id+1)])
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
            simtrace = Tracer.get_timed_trace(
                new_umodel.model_path, trace_path)
            new_patterns = simtrace.filter_by_actions(focused_actions).actions
            iter = iter + 1
        if not hold:
            os.remove(new_model_path)
            os.remove(trace_path)

        return all_patterns

    def find_a_pattern_with_query(self, query: str = None, focused_actions: List[str] = None, hold=False, options=None):
        """
        :param str query: input query
        :param List[str] focused_actions: actions you are interested in
        """
        # 设置路径
        # 新模型路径，不覆盖原模型
        new_model_path = os.path.splitext(self.model_path)[0] + '_pattern.xml'
        self.copy_as(new_model_path=new_model_path)
        new_umodel = UModel(new_model_path)

        if query is not None:
            new_umodel.set_queries(queries=query)

        Verifyta().simple_verify(new_model_path, options=options)
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

    def find_all_patterns_with_query(self, query: str = None, focused_actions: List[str] = None, hold: bool = False, max_patterns: int = None):
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
        default_query, new_patterns = self.find_a_pattern_with_query(
            default_query, focused_actions, hold=True)
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
            new_umodel.add_monitor(f'Monitor{monitor_id}', new_observes,
                                   observe_actions=focused_actions, strict=True, allpattern=True)

            # 构造验证语句
            # 构造monitor.pass
            # E<> Monitor0.pass & !Monitor1.pass
            monitor_pass_str = ' && '.join(
                [f'!Monitor{i}.pass' for i in range(1, monitor_id+1)])
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
            simtrace = Tracer.get_timed_trace(
                new_umodel.model_path, trace_path)
            new_patterns = simtrace.filter_by_actions(focused_actions).actions
            iter = iter + 1
        if not hold:
            os.remove(new_model_path)
            os.remove(trace_path)
        return all_patterns
