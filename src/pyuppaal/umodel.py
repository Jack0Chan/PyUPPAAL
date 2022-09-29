"""umodel
"""
# support return typing UModel
from __future__ import annotations
from enum import auto

# system powershell
from subprocess import run
from typing import List
import xml.etree.cElementTree as ET

from .datastruct import TimedActions
from .verifyta import Verifyta
from .iTools import UFactory, build_cg ,Mermaid
from .tracer import SimTrace, Tracer
import os
import warnings

class UModel:
    """Load UPPAAL model for analysis, editing, verification and other operations.
    """
    def __init__(self, model_path: str, auto_save = True):
        """_summary_

        Args:
            model_path (str): _description_
            auto_save (bool, optional): whether auto save the model after each operation. Defaults to True.
        """
        self.__model_path: str = model_path
        self.__element_tree: ET.ElementTree = ET.ElementTree(file=self.model_path)
        self.__root_elem: ET.Element = self.__element_tree.getroot()
        self.auto_save: bool = auto_save
        if len(self.queries) >= 2:
            warnings.warn(f'Currently we only support models with only 1 query. If you want more queries, please split the models. Current queries: {self.queries}.')
        

    @property
    def model_path(self) -> str:
        """Current model path.

        Returns:
            str: Current model path.
        """
        return self.__model_path

    def save_as(self, new_model_path: str) -> UModel:
        """Save the model to a new path with `self.model_path` changed to `new_model_path`.

        Args:
            new_model_path (str): target model path.

        Returns:
            UModel: self.
        """
        with open(new_model_path, 'w', encoding='utf-8') as f:
            self.__element_tree.write(new_model_path, encoding="utf-8", xml_declaration=True)
        self.__model_path = new_model_path
        return self

    def save(self) -> UModel:
        """Save the current model.

        Returns:
            UModel: self.
        """
        return self.save_as(self.model_path)

    def copy_as(self, new_model_path: str) -> UModel:
        """Make a copy of the current model and return the copied instance.

        Args:
            new_model_path (str): target copy file path.

        Returns:
            UModel: copied instance.
        """
        with open(new_model_path, 'w', encoding='utf-8') as f:
            self.__element_tree.write(
                new_model_path, encoding="utf-8", xml_declaration=True)
        return UModel(new_model_path)

    def get_communication_graph(self, save_path=None, is_beautify=True) -> Mermaid:
        """Get the communication graph of the UPPAAL model, and return a `Mermaid` instance.

        Args:
            save_path (_type_, optional): `<.md | .svg | .pdf | .png>`, the path to save the file. Defaults to None.
            is_beautify (bool, optional): whether beautify the mermaid file by merging edges. Defaults to True.

        Returns:
            Mermaid: _description_
        """
        mermaid_str = build_cg(self.model_path)
        m=Mermaid(mermaid_str)
        if is_beautify:
            m.beautify()
        if save_path:
            m.export(save_path)
        return m

    def verify(self, trace_path: str = None, verify_options: str=None) -> str:
        """Verify and return the terminal output.

        Args:
            trace_path (str, optional): _description_. Defaults to None.
            verify_options (str, optional): _description_. Defaults to None.

        Returns:
            str: _description_
        """
        if trace_path:
            return Verifyta().easy_verify(self.model_path, trace_path, verify_options)[0]
        else:
            return Verifyta().verify(self.model_path, verify_options)[0]

    def easy_verify(self, verify_options: str="-t 1") -> SimTrace | None:
        """Easily verify current model, create a `.xtr` trace file that has the same name as `self.model_path`, and return the SimTrace (if exists).

        Args:
            verify_options (str, optional): verify options, and `-t` must be set because returning a `SimTrace` requires a `.xtr` trace file. Defaults to '-t 1', returning the shortest trace.

        Returns:
            SimTrace | None: if exists a counter example, return a SimTrace, else return None.
        """
        xtr_trace_path = self.model_path.replace('.xml', '.xtr')
        Verifyta().easy_verify(self.model_path, xtr_trace_path, verify_options=verify_options)
        try:
            return Tracer.get_timed_trace(self.model_path, xtr_trace_path.replace('.xtr', '-1.xtr'))
        except:
            return None

    # ======== templates ========
    @property
    def templates(self) -> List[str]:
        """Get all template names of current model.

        Returns:
            List[str]: list of all template names.
        """
        template_names = self.__element_tree.findall("./template/name")
        return [i.text for i in template_names]

    def remove_template(self, template_name: str) -> bool:
        """
        Delete the template according to the input name.

        :param str template_name: the name of template
        :return: `True` when succeed, `False` when fail
        """
        # get template
        template_elem = None
        for template in self.__element_tree.iter("template"):
            if template.find('name').text == template_name:
                template_elem = template
        # remove template
        if template_elem is None:
            if self.auto_save: self.save()
            return False
        self.__root_elem.remove(template_elem)
        if self.auto_save: self.save()
        return True

    # ======== queries ========
    @property
    def queries(self) -> List[str]:
        """Get all queries string.

        Returns:
            List[str]: _description_
        """
        query_formula_elems = self.__element_tree.findall('./queries/query/formula')
        queries = [query_elem.text for query_elem in query_formula_elems]
        return queries

    def clear_queries(self) -> bool:
        """Clear all queries of the model.

        Returns:
            bool: _description_
        """
        root = self.__root_elem
        queries_elem = root.find('queries')
        if queries_elem is None:
            if self.auto_save: self.save()
            return False
        root.remove(queries_elem)
        if self.auto_save: self.save()
        return True

    def set_queries(self, queries: List[str]) -> None:
        """Set the queries of current model.

        Args:
            queries (List[str]): `List` of queries to be set.
        """
        # 首先删除所有的queries
        self.clear_queries()
        # 然后构造queries并插入到模型中
        queries_elem = UFactory.queries(queries)
        self.__root_elem.append(queries_elem)
        if self.auto_save: self.save()

    # ======== system ========
    @property
    def system(self) -> str:
        """Get the system of the model.

        Returns:
            str: _description_
        """
        system_elem = self.__element_tree.find('system')
        return system_elem.text

    def set_system(self, system_str: str) -> None:
        """Set the system element of current model.

        Args:
            system_str (str): target system string you want to set.
        """
        system_elem = self.__element_tree.find('system')
        system_elem.text = system_str
        if self.auto_save: self.save()

    # ======== declaration ========
    @property
    def declaration(self) -> str:
        """Get the declaration of the model.

        Returns:
            str: _description_
        """
        declaration_elem = self.__element_tree.find('declaration')
        return declaration_elem.text

    def set_declaration(self, declaration_str: str) -> None:
        """Set the declaration element of current model.

        Args:
            declaration_str (str): target declaration string you want to set.
        """
        declaration_elem = self.__element_tree.find('declaration')
        declaration_elem.text = declaration_str
        if self.auto_save: self.save()

    # ======== other ========
    @property
    def __max_location_id(self) -> int:
        """Get the maximum location_id so as to make it easier to create a new template.

        Returns:
            int: max location id.
        """
        location_elems = self.__element_tree.findall('./template/location')
        # <location id="id0" x="-187" y="-76">
        # <location id="id1" x="25" y="-76">
        # <location id="id2" x="-51" y="-119">
        ids = [int(location_elem.attrib['id'][2:])
               for location_elem in location_elems]
        return max(ids)

    @property
    def broadcast_chan(self) -> List[str]:
        """Get broadcast channels in Declaration.

        Returns:
            List[str]: List of broadcast channels.
        """
        declarations = self.declaration
        systems = self.system
        start_index = 0
        broadcast_chan = []
        while True:
            start_index = declarations.find('broadcast chan', start_index, -1)
            if start_index == -1:
                break
            end_index = declarations.find(';', start_index, -1)
            tmp_actions = declarations[start_index +15:end_index].strip().split(',')
            tmp_actions = [x.strip() for x in tmp_actions]
            broadcast_chan += tmp_actions
            start_index = end_index
        start_index = 0
        return list(set(broadcast_chan))

    def add_observer_template(self, observations: TimedActions, template_name: str='observer', is_strict_observer: bool = True):
        """Add an observer template, which will also be embedded in `system declarations`. Template that has the same name will be over written.

        An observer is xxx.

        Args:
            observations (TimedActions): observed actions, observed time lower_bound, observed time upper_bound.
            template_name (str, optional): the name of the template. Defaults to 'observer'.
            is_strict_observer (bool, optional): if strict, any other observations will be illegal. 
                For example, assume you set observations `a1, gclk=1, a2, gclk=3`, and there exists trace T: `a1, gclk=1, a2, gclk=2, a2, gclk=3`.
                If `is_strict_observer` is True, then T is invalid. Defaults to True.

        Returns:
            _type_: _description_
        """
        raise NotImplementedError

    def add_pattern_template(self, pattern_list: List[str], template_name: str):
        """Add a pattern template, which will also be embedded in `system declarations`. Template that has the same name will be over written.
        
        Args:
            pattern_list (List[str]): pattern to be monitored.
            template_name (str): _description_

        Returns:
            _type_: _description_
        """
        raise NotImplementedError

    def add_input(self, signals: TimedActions, template_name: str='input'):
        """Add a linear input template, which will also be embedded in `system declarations`. Template that has the same name will be over written.

        Args:
            signals (TimedActions): _description_
            template_name (str, optional): _description_. Defaults to 'input'.

        Returns:
            _type_: _description_
        """
        start_id = self.__max_location_id + 1
        # 删除相同名字的monitor
        self.remove_template(template_name)
        input_model = UFactory.input(
            template_name, signals.convert_to_list_tuple(), start_id)
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
                if template_name not in tmpl or template_name+';' not in tmpl:
                    tmpl.insert(0, template_name)
                cur_system[i] = 'system ' + ','.join(tmpl) + ';'
                break
        cur_system = '\n'.join(cur_system)
        self.set_system(cur_system)
        if self.auto_save: self.save()
        return None

    # all patterns
    # def add_monitor(self, monitor_name: str, signals: TimedActions, observe_actions: List[str] = None, strict: bool = True, allpattern: bool = False):
        """Add new linear monitor template, which will also be embedded in `system declarations`. 
        
        If `monitor_name` already exists in current templates, it will be overwritten.

        Args:
            monitor_name (str): the template name of the monitor.
            signals (TimedActions): actions, lower_bound, upper_bound.
            observe_actions (List[str], optional): _description_. Defaults to None.
            strict (bool, optional): _description_. Defaults to True.
            allpattern (bool, optional): _description_. Defaults to False.

        Returns:
            _type_: _description_
        """

        """
        

        :param str monitor_name: the name of monitor
        :param TimedActions signals: specific data type `List[Tuple[signal, guard, inv]]`, `signal`, `guard` and `inv` are `str` type and can be `None`
        :param List[str] observe_actions: observe actions @yhc is there any observe_actions in Timed actions?
        :param bool strict: determine whether monitor is strict or not
        :param bool allpattern: determine whether allpattern is enabled
        """
        # 处理observe_actions is None的情况
        if observe_actions is None:
            observe_actions = self.broadcast_chan

        start_id = self.__max_location_id + 1
        # 删除相同名字的monitor
        self.remove_template(monitor_name)
        monitor = UFactory.monitor(monitor_name, signals.convert_to_list_tuple(), observe_actions, start_id, strict, allpattern)
        self.__root_elem.insert(-2, monitor)
        # 将新到monitor加入到system中
        cur_system = self.system
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
        if self.auto_save: self.save()
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
            new_umodel.add_monitor(f'Monitor{monitor_id}', new_observes, observe_actions=focused_actions, strict=True, allpattern=True)
            
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

            Verifyta().easy_verify(new_umodel.model_path)

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

        Verifyta().easy_verify(new_model_path, options=options)
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
        注意这里的input已经在模型中, 并且原模型不包含任何Monitor

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

            Verifyta().easy_verify(new_umodel.model_path)

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
