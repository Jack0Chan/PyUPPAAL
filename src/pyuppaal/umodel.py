"""umodel
"""
# support return typing UModel
from __future__ import annotations
import os
import xml.etree.ElementTree as ET
from typing import List, Tuple
from .datastruct import TimedActions
from .verifyta import Verifyta
from .iTools import UFactory, build_cg, Mermaid
from .tracer import SimTrace, Tracer


class UModel:
    """Load UPPAAL model for analysis, editing, verification and other operations.
    """

    def __init__(self, model_path: str, auto_save=True):
        """_summary_

        Args:
            model_path (str): _description_
            auto_save (bool, optional): whether auto save the model after each operation. Defaults to True.
        """
        self.__model_path: str = model_path
        self.__element_tree: ET.ElementTree = ET.ElementTree(
            file=self.model_path)
        self.__root_elem: ET.Element = self.__element_tree.getroot()
        self.auto_save: bool = auto_save

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
            self.__element_tree.write(
                new_model_path, encoding="utf-8", xml_declaration=True)
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
        m = Mermaid(mermaid_str)
        if is_beautify:
            m.beautify()
        if save_path:
            m.export(save_path)
        return m

    def verify(self, trace_path: str = None, verify_options: str = None) -> List[str]:
        """Verify and return the verify result. If `trace_path` is not given, it wll return the list of terminal result.

        Args:
            trace_path (str, optional): _description_. Defaults to None.
            verify_options (str, optional): _description_. Defaults to None.

        Returns:
            List[str]: _description_
        """
        if trace_path:
            return Verifyta().easy_verify(self.model_path, trace_path, verify_options)[0]
        else:
            return Verifyta().verify(self.model_path, verify_options)[0]

    def easy_verify(self, verify_options: str = "-t 1") -> SimTrace | None:
        """Easily verify current model, create a `.xtr` trace file that has the same name as `self.model_path`, and return the SimTrace (if exists).

        Args:
            verify_options (str, optional): verify options, and `-t` must be set because returning a `SimTrace` requires a `.xtr` trace file. Defaults to '-t 1', returning the shortest trace.

        Returns:
            SimTrace | None: if exists a counter example, return a SimTrace, else return None.
        """
        if '-t' not in verify_options:
            err_info = '"-t" must be set in verify_options, '
            err_info += f'current verify_options: {verify_options}.'
            raise ValueError(err_info)
        xtr_trace_path = self.model_path.replace('.xml', '.xtr')

        verify_cmd_res = Verifyta().easy_verify(
            self.model_path, xtr_trace_path, verify_options=verify_options)[0]
        if 'Formula is satisfied' in verify_cmd_res:
            res = Tracer.get_timed_trace(
                self.model_path, xtr_trace_path.replace('.xtr', '-1.xtr'))
        else:
            return None
        return res

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
            if self.auto_save:
                self.save()
            return False
        self.__root_elem.remove(template_elem)
        if self.auto_save:
            self.save()
        return True

    # ======== queries ========
    @property
    def queries(self) -> List[str]:
        """Get all queries string.

        Returns:
            List[str]: _description_
        """
        query_formula_elems = self.__element_tree.findall(
            './queries/query/formula')
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
            if self.auto_save:
                self.save()
            return False
        root.remove(queries_elem)
        if self.auto_save:
            self.save()
        return True

    def set_queries(self, queries: List[str] | str) -> None:
        """Delete all the queries in the model and then inserts the new queries into the model

        Args:
            queries (List[str] | str): A list of queries or a single query

        """

        if isinstance(queries, str):
            queries = [queries]

        # 首先删除所有的queries
        self.clear_queries()
        # 然后构造queries并插入到模型中
        queries_elem = UFactory.queries(queries)
        self.__root_elem.append(queries_elem)
        if self.auto_save:
            self.save()

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
        if self.auto_save:
            self.save()

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
        if self.auto_save:
            self.save()

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
            tmp_actions = declarations[start_index +
                                       15:end_index].strip().split(',')
            tmp_actions = [x.strip() for x in tmp_actions]
            broadcast_chan += tmp_actions
            start_index = end_index
        start_index = 0
        return list(set(broadcast_chan))

    def add_observer_template(self, observations: TimedActions, focused_actions: List[str] | None = None, template_name: str = 'Observer', is_strict: bool = True) -> None:
        """Add an observer template, which will also be embedded in `system declarations`. Template that has the same name will be over written.

        An observer is xxx.

        Args:
            observations (TimedActions): observed actions, observed time lower_bound, observed time upper_bound.
            template_name (str, optional): the name of the template. Defaults to 'observer'.
            is_strict (bool, optional): if strict, any other observations will be illegal. 
                For example, assume you set observations `a1, gclk=1, a2, gclk=3`, and there exists trace T: `a1, gclk=1, a2, gclk=2, a2, gclk=3`.
                If `is_strict_observer` is True, then T is invalid. Defaults to True.

        Returns:
            _type_: _description_
        """
        if focused_actions is None:
            focused_actions = list(map(lambda x: x.replace(
                '!', '').replace('?', ''), observations.actions))
        self.add_monitor_template(
            template_name, observations, focused_actions, strict=is_strict)

    def add_pattern_template(self, pattern_list: List[str], template_name: str) -> None:
        """Add a pattern template, which will also be embedded in `system declarations`. Template that has the same name will be over written.

        Args:
            pattern_list (List[str]): pattern to be monitored.
            template_name (str): _description_

        Returns:
            _type_: _description_
        """
        raise NotImplementedError

    def add_input_template(self, signals: TimedActions, template_name: str = 'Input') -> None:
        """Add a linear input template, which will also be embedded in `system declarations`. Template that has the same name will be over written.

        Args:
            signals (TimedActions): _description_
            template_name (str, optional): _description_. Defaults to 'Input'.

        Returns:
            _type_: _description_
        """
        assert len(signals) > 0

        start_id = self.__max_location_id + 1
        # 删除相同名字的monitor
        self.remove_template(template_name)

        clock_name, signals = self.__parse_signals(signals)
        input_model = UFactory.input(
            template_name, signals.convert_to_list_tuple(clock_name), start_id)
        self.__root_elem.insert(-2, input_model)

        # 将新到monitor加入到system中
        self.__add_template_to_system(template_name)

        return None

    def __add_template_to_system(self, template_name: str):
        """Add a template to system declarations.

        Args:
            template_name (str): the name of the template.

        """
        system_lines: List[str] = self.system.split('\n')
        system_lines: List[str] = list(map(lambda x: x.strip(), system_lines))
        for i, line in enumerate(system_lines):
            if line.strip().startswith('system'):
                system_items = list(
                    map(lambda s: s.strip(), line.strip()[6:-1].split(',')))
                if template_name not in system_items:
                    system_items.append(template_name)
                system_lines[i] = f"system {', '.join(system_items)};"
                break

        self.set_system('\n'.join(system_lines))

    # all patterns
    def add_monitor_template(self, monitor_name: str, signals: TimedActions, focused_actions: List[str] = None, strict: bool = True, allpattern: bool = False):
        """Add new linear monitor template, which will also be embedded in `system declarations`. 

        If `monitor_name` already exists in current templates, it will be overwritten.

        Args:
            monitor_name (str): the template name of the monitor.
            signals (TimedActions): actions, lower_bound, upper_bound.
            focused_actions (List[str], optional): _description_. Defaults to None.
            strict (bool, optional): _description_. Defaults to True.
            allpattern (bool, optional): _description_. Defaults to False.

        Returns:
            _type_: _description_
        """

        # 处理focused_actions is None的情况
        if focused_actions is None:
            focused_actions = self.broadcast_chan

        clock_name, signals = self.__parse_signals(signals)

        if '?' in "".join(focused_actions) or '!' in "".join(focused_actions):
            raise ValueError(
                f"focused_actions should not contain '?' or '!', current focused_actions: {focused_actions}")

        start_id = self.__max_location_id + 1
        # 删除相同名字的monitor
        self.remove_template(monitor_name)
        monitor = UFactory.monitor(monitor_name, signals.convert_to_list_tuple(
            clock_name), focused_actions, start_id, strict, allpattern)
        self.__root_elem.insert(-2, monitor)
        # 将新到monitor加入到system中

        self.__add_template_to_system(monitor_name)

    def __parse_signals(self, signals: TimedActions, default_name: str = "input_clk") -> Tuple[str, TimedActions]:
        """Parse the signals, if the signal name is not specified, then use the default name.

        Args:
            signals (TimedActions): the signals to be parsed.
            default_name (str): the default clock name for the signals.

        Returns:
            Tuple[str, TimedActions]: the clock name and the parsed signals.
        """

        parsed_actions = list(map(lambda x: x.replace(
            '?', '').replace('!', ''), signals.actions))

        if len(signals) > 0 and not isinstance(signals.lb[0], str):
            signals.lb = list(map(str, signals.lb))

        if len(signals) > 0 and not isinstance(signals.ub[0], str):
            signals.ub = list(map(str, signals.ub))

        if len(signals) > 0 and signals.lb[0].strip().find('>') > 0 and signals.lb[0].strip()[0] != '>':
            # If the stmt has clk name, like 'a1 > 1', then use the clk name
            # Only accept input like "a1 > 1" or "a1>1", not ">1" or "1"
            clock_name = signals.lb[0].split('>')[0]
        else:  # Otherwise, we use the default clock name
            # accept input like ">1" or "1"
            clock_name = default_name

        len_lb = len(signals.lb)
        for i in range(len_lb):  # Remove the clock name and operator
            # Note that '>=' must be removed first, otherwise '>=' will be removed to '='
            signals.lb[i] = signals.lb[i].replace(
                clock_name, '').replace('>=', '').replace('>', '').strip()
            signals.ub[i] = signals.ub[i].replace(
                clock_name, '').replace('<=', '').replace('<', '').strip()

        return clock_name, TimedActions(parsed_actions, signals.lb, signals.ub)

    def __find_a_pattern(self, focused_action: List[str] = None, hold: bool = True, options: str = None) -> SimTrace | None:
        """Find a pattern in the current model.

        Args:
            focused_action (List[str], optional): the actions that we want to focus on. Defaults to None.
            hold (bool, optional): whether to keep the temp file. Defaults to True.
            options (str, optional): options for the verifier. Defaults to None.

        Returns:
            SimTrace | None: the founded patterns. None if no pattern is found.
        """
        self.save()
        if options is not None:
            sim_trace = self.easy_verify(options)
        else:
            sim_trace = self.easy_verify()

        if sim_trace is None:
            return None

        trace_path = os.path.splitext(self.model_path)[0] + '-1.xtr'
        pattern_seq = sim_trace.filter_by_actions(focused_action)

        if not hold:
            os.remove(trace_path)
            os.remove(self.model_path)

        return pattern_seq

    def find_all_patterns(self, focused_actions: List[str] = None,
                          hold: bool = True,
                          max_patterns: int = None) -> List[SimTrace]:
        """Find all patterns of the first query in the model.

        Args:
            focused_actions (List[str], optional): the actions that we want to focus on. Defaults to None.
            hold (bool, optional): whether to keep the temp files. Defaults to True.
            max_patterns (int, optional): the maximum number of patterns to find. If None, then all patterns will be found. Defaults to None.

        Returns:
            List[SimTrace]: the list of patterns.
        """
        queries = self.queries
        if len(queries) == 0:
            return []
        all_patterns = self.__find_all_patterns_of_a_query(
            queries[0], focused_actions, hold, max_patterns)
        return all_patterns

    def __find_all_patterns_of_a_query(self, query: str = None,
                                       focused_actions: List[str] = None,
                                       hold: bool = True,
                                       max_patterns: int = None) -> List[SimTrace] | None:
        """Find all patterns that satisfy the query

        Args:
            query (str, optional): the query to be verified. Defaults to None.
            focused_actions (List[str], optional): the actions that we want to focus on. Defaults to None.
            hold (bool, optional): whether to keep the temp files. Defaults to True.
            max_patterns (int, optional): the maximum number of patterns to find. If None, then all patterns will be found. Defaults to None.

        Raises:
            NotImplementedError: only support E<> and A[] queries. Raise when other queries are given

        Returns:
            List[SimTrace]: a list of patterns that satisfy the query.
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

        new_model_path = os.path.splitext(self.model_path)[0] + '_pattern.xml'
        new_umodel = self.copy_as(new_model_path=new_model_path)

        new_umodel.set_queries(default_query)
        new_patterns = new_umodel.__find_a_pattern(
            focused_actions, hold=hold)  # Keep the temp files until the end

        if new_patterns is None:
            return []

        query_str = default_query
        # 根据初始的pattern构建monitor并循环, 初始Moniter为0
        all_patterns = []
        monitor_id = 0
        iter_ = 1
        while new_patterns is not None:
            all_patterns.append(new_patterns)

            if max_patterns is not None and iter_ >= max_patterns:
                break

            monitor_id += 1
            # 将pattern[List] -> TimedActions
            new_observes = TimedActions(new_patterns.actions)
            new_umodel.add_monitor_template(f'Monitor{monitor_id}', new_observes,
                                            focused_actions=focused_actions, strict=True, allpattern=True)

            # 构造验证语句
            # 构造monitor.pass
            # E<> Monitor0.pass & !Monitor1.pass
            query_str = ' && '.join(
                [f'!Monitor{i}.pass' for i in range(1, monitor_id+1)])
            # E<> !Monitor0.pass & !Monitor1.pass
            query_str = f'{default_query} && {query_str}'

            new_umodel.set_queries(query_str)
            new_patterns = new_umodel.__find_a_pattern(
                focused_actions, hold=hold)
            # Keep the temp files until the end

            if new_patterns is None:
                break

            trace_path = os.path.splitext(new_umodel.model_path)[0] + '-1.xtr'

            iter_ = iter_ + 1

        if not hold:
            os.remove(new_model_path)
            os.remove(trace_path)

        return all_patterns
