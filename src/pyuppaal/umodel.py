"""umodel
"""
# support return typing UModel
from __future__ import annotations
import os
import xml.etree.ElementTree as ET
from typing import List
from itertools import product
import uuid

# from anytree import PostOrderIter, NodeMixin

# from pyuppaal.iTools.new_factory import Template, Location, Edge
from .verifyta import Verifyta
from .build_cg import build_cg, Mermaid
from .tracer import SimTrace
from .nta import Template
from .monitors import Monitors
from .utap import utap_parser
from .mytree import MyTree


class UModel:
    """Load UPPAAL model for analysis, editing, verification and other operations. If you want to modify the model, you should `from pyuppaal.nta import Template, Location, Edge`.
    """

    def __init__(self, model_path: str = None):
        """_summary_

        Args:
            model_path (str): model path. Defaults to None.
        """
        self.__declaration: str = "// Place global declarations here."
        self.__templates: List[Template] = []
        self.__system: str = "system cannot be None"
        self.__queries: List[str] | None = None
        self.__model_path: str = model_path

        if model_path is None:
            print(
                "Warning: model_path is None, create a new model named 'untiteled.xml' in current directory"
            )
            model_path = "untitled.xml"
            self.__model_path = model_path
            self = UModel.new(model_path)

        if not os.path.exists(model_path):
            err_info = f"Model path: {model_path} does not exist.\n"
            raise ValueError(err_info)
        # 解构xml
        self.__build()

    # region 基础的 getter & setters
    # region ======== declaration ========
    @property
    def declaration(self) -> str:
        return self.__declaration

    @declaration.setter
    def declaration(self, value: str) -> None:
        if not isinstance(value, str):
            err_info = f"declaration requires string, current is: {type(value)}."
            raise ValueError(err_info)
        self.__declaration = value
        self.save()

    # endregion

    # region ======== templates =======
    @property
    def templates(self) -> List[Template]:
        return self.__templates

    @templates.setter
    def templates(self, value: List[Template]) -> None:
        # if not isinstance(value, List[Template]):
        #     err_info = f"declaration requires List[Template], current is: {type(value)}."
        #     raise ValueError(err_info)
        self.__templates = value
        self.save()

    # endregion

    # region ======== system ========
    @property
    def system(self) -> str:
        return self.__system

    @system.setter
    def system(self, value: str) -> None:
        if not isinstance(value, str):
            err_info = f"system requires string, current is: {type(value)}."
            raise ValueError(err_info)
        self.__system = value
        self.save()

    # endregion

    # region ======== queries ========
    @property
    def queries(self) -> List[str] | None:
        return self.__queries

    @queries.setter
    def queries(self, value: str | List[str] | None) -> None:
        """Set the queries of the xml model.
        ```python
        m = UModel('test.xml')
        m.queries = 'A[] not deadlock'
        m.queries = ['A[] not deadlock', 'E<> process.success']
        ```
        Args:
            value (str | List[str] | None): target single query, or list of queries.
        """
        if isinstance(value, str):
            value = [value]
        self.__queries = value
        self.save()

    # endregion

    # region ======== other properties ========
    @property
    def Element(self) -> ET.Element:
        """xml contents of `self`, including
        1. declaration
        2. template(s)
        3. system
        4. query(s)
        """
        # 模型xml文件的标准模板
        root = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE nta PUBLIC '-//Uppaal Team//DTD Flat System 1.1//EN' 'http://www.it.uu.se/research/group/darts/uppaal/flat-1_2.dtd'>
<nta>
</nta>
"""
        root = ET.fromstring(root)
        # nta = res.get("nta") seems to be wrong
        # nta = res.get('nta')
        # 1. 添加declaration
        declaration_elem = ET.Element("declaration")
        declaration_elem.text = self.declaration
        root.append(declaration_elem)

        # 2. 添加templates
        for template in self.templates:
            root.append(template.Element)

        # 3. 添加system
        system_elem = ET.Element("system")
        system_elem.text = self.system
        root.append(system_elem)

        # 4. 添加queries
        if self.queries is not None:
            root.append(self.__queries_element)
        return root

    @property
    def ElementTree(self) -> ET.ElementTree:
        return ET.ElementTree(self.Element)

    @property
    def model_path(self) -> str:
        """Current model path.

        Returns:
            str: Current model path.
        """
        return self.__model_path

    @property
    def max_location_id(self) -> int:
        """Get the maximum location_id so as to make it easier to create a new template, because the id of `Location` is unique.

        Returns:
            int: max location id of `self`.
        """
        res = -1
        for template in self.templates:
            for location in template.locations:
                if location.location_id > res:
                    res = location.location_id
        return res

    # endregion
    # endregion 基础 getter & setters

    # region properties

    @property
    def broadcast_chan(self) -> List[str]:
        """Get broadcast channels in `declaration`.

        Returns:
            List[str]: List of broadcast channels.
        """
        declarations = self.declaration
        # systems = self.system
        start_index = 0
        broadcast_chan = []
        while True:
            start_index = declarations.find("broadcast chan", start_index, -1)
            if start_index == -1:
                break
            end_index = declarations.find(";", start_index, -1)
            tmp_actions = declarations[start_index + 15: end_index].strip().split(",")
            tmp_actions = [x.strip() for x in tmp_actions]
            broadcast_chan += tmp_actions
            start_index = end_index
        start_index = 0
        return list(set(broadcast_chan))

    # endregion

    # region 解构(build)
    @property
    def __queries_element(self) -> ET.Element:
        queries_elem = ET.Element("queries")
        # 构建并加入多个queries element
        for query in self.queries:
            # ==== START: 构建单个query element ====
            # 单个query element包含
            # 1. formula
            # 2. comment
            query_elem = ET.Element("query")
            # 添加 1. formula
            formula_elem = ET.Element("formula")
            formula_elem.text = query
            query_elem.append(formula_elem)
            # 添加 2. comment
            query_elem.append(ET.Element("comment"))
            # ==== END: 构建单个query element ====
            queries_elem.append(query_elem)
        return queries_elem

    def __build(self) -> None:
        """解构xml, 获得self的各种属性, 比如:
        1. declaration,
        2. templates,
        3. system,
        4. queries等.
        """
        element_tree = ET.ElementTree(file=self.model_path)

        # 1. declaration
        self.__declaration = element_tree.find("declaration").text

        # 2. templates
        template_elems = element_tree.findall("./template")
        self.__templates = [Template.from_xml(t) for t in template_elems]

        # 3. system
        self.__system = element_tree.find("system").text

        # 4. queries
        query_formula_elems = element_tree.findall("./queries/query/formula")
        self.__queries = [query_elem.text for query_elem in query_formula_elems]

        self.save()

    # endregion 解构(build)

    # region 导出xml
    @property
    def xml(self) -> str:
        return ET.tostring(self.Element, encoding="utf-8").decode("utf-8")

    # endregion 导出xml

    # region 基础的文件保存、创建等功能
    @staticmethod
    def new(model_path: str) -> UModel:
        """创建一个新的uppaal xml文件

        Args:
            file_name (str): file name

        Returns:
            UModel:  a new UModel instance.
        """
        # 创建一个xml文件
        # 检查输入的合法性
        if not model_path.endswith(".xml"):
            err_info = f"model path must ends with .xml, currently: {model_path}."
            raise ValueError(err_info)
        if os.path.exists(model_path):
            err_info = f"file {model_path} already exists."
            raise ValueError(err_info)

        # 通用模板
        xml_base = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE nta PUBLIC '-//Uppaal Team//DTD Flat System 1.1//EN' 'http://www.it.uu.se/research/group/darts/uppaal/flat-1_2.dtd'>
<nta>
	<declaration>// Place global declarations here.</declaration>
	<template>
		<name x="5" y="5">Template</name>
		<declaration>// Place local declarations here.</declaration>
		<location id="id0" x="0" y="0">
		</location>
		<init ref="id0"/>
	</template>
	<system>// Place template instantiations here.
Process = Template();
// List one or more processes to be composed into a system.
system Process;
    </system>
	<queries>
		<query>
			<formula></formula>
			<comment></comment>
		</query>
	</queries>
</nta>
"""
        et = ET.fromstring(xml_base)
        tree = ET.ElementTree(et)
        with open(model_path, "w", encoding="utf-8") as f:
            tree.write(model_path, encoding="utf-8", xml_declaration=True)
        res = UModel(model_path=model_path)
        return res

    def save_as(self, new_path: str) -> UModel:
        """Save the model to a new path with `self.model_path` changed to `new_model_path`.

        Args:
            new_path (str): target model path.

        Returns:
            UModel: self.
        """
        with open(new_path, "w", encoding="utf-8") as f:
            self.ElementTree.write(new_path, encoding="utf-8", xml_declaration=True)
        self.__model_path = new_path

        return self

    def save(self) -> UModel:
        """Save the current model.

        Returns:
            UModel: self.
        """
        return self.save_as(self.model_path)

    def copy_as(self, new_path: str) -> UModel:
        """Make a copy of the current model and return the copied instance.

        Args:
            new_path (str): target copy file path.

        Returns:
            UModel: new copied instance.
        """
        with open(new_path, "w", encoding="utf-8") as f:
            self.ElementTree.write(new_path, encoding="utf-8", xml_declaration=True)
        return UModel(new_path)

    # endregion 基础的文件保存功能

    # region 验证相关
    def verify(self, trace_path: str = None, verify_options: str = None, keep_tmp_file: bool = True) -> str:
        """Verify and return the verify result. If `trace_path` is not given, it wll return the terminal result.

        Args:
            trace_path (str, optional): the path to save the trace file. Defaults to None.
            verify_options (str, optional): options for verifyta, such as ` -t 0 -o 0`. Defaults to None.
            keep_tmp_file (bool, optional): whether to keep the temp file such as `xtr` or in-process `xml`. Defaults to True.

        Returns:
            str: terminal verify results for `self`.
        """
        return Verifyta().verify(self.model_path, trace_path, verify_options, keep_tmp_file)

    def easy_verify(
        self, verify_options: str = "-t 1", keep_tmp_file=True
    ) -> SimTrace | None:
        """Easily verify current model, create a `.xtr` trace file that has the same name as `self.model_path`, and return parsed counter example as `SimTrace` (if exists). You can do easy_verify with only ONE query each time.

        Args:
            verify_options (str, optional): verify options, and `-t` must be set because returning a `SimTrace` requires a `.xtr` trace file. Defaults to '-t 1', returning the shortest trace.
            keep_tmp_file (bool, optional): whether to keep the temp file such as `xtr` or in-process `xml`. Defaults to True.

        Returns:
            SimTrace | None: if exists a counter example, return a SimTrace, else return None.
        """
        if len(self.queries) != 1:
            err_info = f'You can do easy_verify with only ONE query, current number of queries is: {len(self.queries)}, they are: {self.queries}.'
            raise ValueError(err_info)

        # print(verify_options)
        if "-t" not in verify_options:
            err_info = f'"-t" must be set in verify_options, current verify_options: {verify_options}.'
            raise ValueError(err_info)

        if Verifyta().get_uppaal_version() == 4:  # uppaal4.x
            xtr_trace_path = self.model_path.replace(".xml", ".xtr")
            verify_cmd_res = Verifyta().verify(
                self.model_path, xtr_trace_path, verify_options=verify_options
            )

            # print(verify_cmd_res)
            xtr_trace_path = xtr_trace_path.replace(".xtr", "-1.xtr")
            if "Writing example trace to" in verify_cmd_res or "Writing counter example to" in verify_cmd_res:
                res = self.load_xtr_trace(xtr_trace_path)
                if not keep_tmp_file:
                    os.remove(xtr_trace_path)
                return res
        else:  # uppaal5.x
            xtr_trace_path = self.model_path.replace(".xml", "_xtr")
            verify_cmd_res = Verifyta().verify(
                self.model_path, xtr_trace_path, verify_options=verify_options
            )

            xtr_trace_path = xtr_trace_path.replace("_xtr", "_xtr-1")
            if "Writing witness trace" in verify_cmd_res or "Writing counter example to" in verify_cmd_res:
                res = self.load_xtr_trace(xtr_trace_path)
                if not keep_tmp_file:
                    os.remove(xtr_trace_path)
                return res
        # print("Warning: umodel.py: easy_verify returned None!!!")
        return None

    # endregion

    def __check_unique_id(self) -> bool:
        """check 是否有id重复, 如果没有重复id 则返回True, 有重复id 则打印重复id 并 raise error

        Raises:
            ValueError: 如果有重复id, 则 raise error

        Returns:
            bool: True if no duplicate id, else raise error.
        """
        id_set = set()
        id_set_len = 0
        for template in self.templates:
            for location in template.locations:
                l_id = location.location_id
                id_set.add(l_id)
                if len(id_set) != id_set_len + 1:
                    err_info = f"Location id{l_id} is not unique. Related Template name: {template.name}. "
                    hint_info = "Hint: You can get the max location id by `UModel.max_location_id()`."
                    raise ValueError(err_info + hint_info)
                else:
                    id_set_len += 1
        return True

    def __check_unique_init_ref(self) -> str:
        init_ref_set = set()
        for template in self.templates:
            init_ref_set.add(template.init_ref)
            if len(init_ref_set) != 1:
                err_info = (
                    f'Template "{template.name}" should have unique initial location. '
                )
                hint_info = "Make sure every Template has unqiue initial location.\n"
                raise ValueError(err_info + hint_info)
            else:
                init_ref_set.clear()

    def get_communication_graph(self, save_path=None, is_beautify=True) -> Mermaid:
        """Get the communication graph of the UPPAAL model, and return a `Mermaid` instance.

        Args:
            save_path (_type_, optional): `<.md | .svg | .pdf | .png>`, the path to save the file. Defaults to None.
            is_beautify (bool, optional): whether beautify the mermaid file by merging edges. Defaults to True.

        Returns:
            Mermaid: a `Mermaid` instance.
        """
        mermaid_str = build_cg(self.model_path)
        m = Mermaid(mermaid_str)
        if is_beautify:
            m.beautify()
        if save_path:
            m.export(save_path)
        return m

    def __get_actions(self, observation: List[str] | List[tuple[str, str, str]]):
        """get actions from observations
        Args:
            observation (List[str] | List[tuple[str,str,str]]):
                If List[str], then it is a list of actions.
                If List[tuple[str,str,str]], then it is a list of (action, lower_bound, upper_bound).

        Raises:
            ValueError: if actions is not List[str] or List[tuple[str,str,str]], raise ValueError.

        Returns:
            List[str]: a list of actions.
        """
        if isinstance(observation[0], str):
            return observation
        elif isinstance(observation[0], tuple):
            return [action for action, _, _ in observation]
        else:
            raise ValueError(
                f"observation should be List[str] or List[tuple[str,str,str]], but current is {type(observation)}."
            )

    def __parse_observations(self,
                             observation: List[str] | List[tuple[str, str, str]]
                             ) -> List[tuple[str, str, str]]:
        """parse observations to List[tuple[str,str,str]]
        Args:
            observation (List[str] | List[tuple[str,str,str]]):
                If List[str], then it is a list of actions.
                If List[tuple[str,str,str]], then it is a list of (action, lower_bound, upper_bound).

        Raises:
            ValueError: if actions is not List[str] or List[tuple[str,str,str]], raise ValueError.

        Returns:
            List[tuple[str,str,str]]: a list of (action, lower_bound, upper_bound).
        """
        if isinstance(observation[0], str):
            return [(action, "", "") for action in observation]
        elif isinstance(observation[0], tuple):
            if isinstance(observation[0][1], int):  # if use int"time" not str"gclk >= time"
                processed_observations = []
                for action, lb, ub in observation:
                    lb = f"gclk>={lb}"
                    ub = f"gclk<={ub}"
                    processed_observations.append((action, lb, ub))
                return processed_observations
            return observation
        else:
            raise ValueError(
                f"actions should be List[str] or List[tuple[str,str,str]], but current is {type(observation)}."
            )

    # region 基础编辑
    def remove_template(self, template_name: str) -> bool:
        """Delete the template according to `template_name`.

        Args:
            template_name (str): the name of template you want to delte.

        Returns:
            bool: `True` when succeed, `False` when fail.
        """
        for i, template in enumerate(self.templates):
            if template.name == template_name:
                self.templates.remove(self.templates[i])
                break
        self.save()
        return True

    # endregion

    def add_observer_monitor(
        self,
        observations: List[str] | List[tuple[str, str, str]],
        focused_actions: List[str] | None = None,
        template_name: str = "Observer",
        is_strict: bool = True,
        all_patterns: bool = False,
    ) -> None:
        """Add an observer template, which will also be embedded in `system declarations`. If exists a template with the same name, it will raise error.

        An observer is a monitor that observes the sequence of actions, and it will reach the `pass` state if the observed sequence of actions is a subsequence of the trace.

        Args:
            observations (List[str] | List[tuple[str, str, str]]): observed actions.
                If List[str], then it is a list of actions.
                If List[tuple[str,str,str]], then it is a list of (action, lower_bound, upper_bound).
            focused_actions (List[str] | None, optional): the set of actions you are focused on. Only events in `focused_actions` will be analyzed when `find_all_patterns`. Defaults to None, taking all the events of the current model.
            template_name (str, optional): the name of the template. Defaults to 'observer'.
            is_strict (bool, optional): if strict, any other observations will be illegal.
                For example, assume you set observations `a1, gclk=1, a2, gclk=3`, and there exists trace T: `a1, gclk=1, a2, gclk=2, a2, gclk=3`.
                If `is_strict_observer` is True, then T is invalid. Defaults to True.
            all_patterns (bool, optional): whether the monitor is used for `find_all_patterns`. Defaults to False.

        Raises:
            ValueError: if `template_name` already exists, raise ValueError.

        Returns:
            None
        """
        signals = self.__parse_observations(observations)

        if focused_actions is None:
            focused_actions = list(
                map(
                    lambda x: x.replace("!", "").replace("?", ""),
                    self.__get_actions(signals),
                )
            )

        focused_actions = list(
            map(lambda x: x.replace("!", "").replace("?", ""), focused_actions)
        )

        if template_name in [template.name for template in self.templates]:
            raise ValueError(f"Template <{template_name}> already exists.")

        monitor = Monitors.observer_template(
            name=template_name,
            signals=signals,
            observe_action=focused_actions,
            init_ref=self.max_location_id + 1,
            strict=is_strict,
            allpattern=all_patterns,
        )
        # self.templates.append(monitor)

        # 将新到monitor加入到system中

        self.add_template_to_system(monitor.name)
        self.add_template(monitor)

    def add_input_monitor(
        self,
        inputs: List[str] | List[tuple[str, str, str]],
        template_name: str = "Input",
    ) -> None:
        """Add a linear input template that captures specified `inputs`, which will also be embedded in `system declarations`. Template that has the same name will be over written.

        Args:
            observations (List[str] | List[tuple[str, str, str]]): input actions.
                If List[str], then it is a list of actions.
                If List[tuple[str,str,str]], then it is a list of (action, lower_bound, upper_bound).
            template_name (str, optional): the name of the template. Defaults to 'input'.

        Returns:
            None
        """
        signals = self.__parse_observations(inputs)
        assert len(signals) > 0

        start_id = self.max_location_id + 1
        # 删除相同名字的monitor
        # self.remove_template(template_name)
        if template_name in [template.name for template in self.templates]:
            raise ValueError(f"Template <{template_name}> already exists.")

        # clock_name, signals = self.__parse_signals(signals)
        # input_model = UFactory.input(template_name, signals.to_list_tuple(clock_name), start_id)
        input_monitor = Monitors.input_template(
            name=template_name, signals=signals, init_ref=start_id
        )
        # self.templates.append(input_monitor)

        # self.__root_elem.insert(-2, input_model)

        # 将新到monitor加入到system中
        self.add_template(input_monitor)
        self.add_template_to_system(input_monitor.name)

        return None

    def add_template(self, template: Template) -> None:
        """Add `template` to `self.template`. However, if you also want to embed the template to `system`, you should also call `self.add_template_to_system(template_name: str)`.

        Args:
            template (Template): the template to be added to `self.template`.

        Raises:
            ValueError: raise ValueError if `template` with the same name already exists.
        """

        # Check if the template name already exists
        if template.name in [t.name for t in self.templates]:
            raise ValueError(f"Template <{template.name}> already exists in the model.")

        self.templates.append(template)
        self.save()

    def add_template_to_system(self, template_name: str):
        """Add a template to system declarations.
        For example, a system declaration is "system Process1, Process2;".
        After add Process3 by add_template_to_system('Process3'), we get "system Process1, Process2, Process3;".

        Note that before `add_template_to_system`, you should first call `self.add_template(template: Template)`.

        Args:
            template_name (str): the name of the template.

        Raises:
            ValueError: if template_name already exists, raise ValueError.
        """

        system_lines: List[str] = self.system.split("\n")
        system_lines: List[str] = list(map(lambda x: x.strip(), system_lines))
        for i, line in enumerate(system_lines):
            if line.strip().startswith("system"):
                system_items = list(
                    map(lambda s: s.strip(), line.strip()[6:-1].split(","))
                )
                if template_name not in system_items:
                    system_items.append(template_name)
                else:  # This may not happen. Checked before this.
                    raise ValueError(
                        f"Template {template_name} already exists in system."
                    )
                system_lines[i] = f"system {', '.join(system_items)};"
                break
        self.system = "\n".join(system_lines)

    def find_a_pattern(
        self,
        focused_actions: List[str] = None,
        keep_tmp_file: bool = True,
        options: str = None,
    ) -> SimTrace | None:
        """Find a pattern in the current model.

        Args:
            focused_actions (List[str], optional): the set of actions you are focused on. Only events in `focused_actions` will be analyzed when `find_all_patterns`. Defaults to None, taking all the events of the current model.
            keep_tmp_file (bool, optional): whether to keep the temp file such as `xtr` or in-process `xml`. Defaults to True.
            options (str, optional): options for verifyta, such as ` -t 0 -o 0`. Defaults to None.

        Returns:
            SimTrace | None: pattern will be returend as `SimTrace`. Return `None` if no pattern is found.
        """
        # create a temp model
        # new_model_path = os.path.splitext(self.model_path)[0] + '_a_pattern.xml'
        # new_umodel = self.copy_as(new_path=new_model_path)
        # new_umodel.queries = default_query

        if options is not None:
            sim_trace = self.easy_verify(options)
        else:
            sim_trace = self.easy_verify()

        if sim_trace is None:
            return None

        if Verifyta().get_uppaal_version() == 4:
            trace_path = os.path.splitext(self.model_path)[0] + "-1.xtr"
        else:
            trace_path = os.path.splitext(self.model_path)[0] + "_xtr-1"

        pattern_seq = sim_trace.filter_by_actions(focused_actions)

        if not keep_tmp_file:
            os.remove(trace_path)

        return pattern_seq

    def find_all_patterns(
        self,
        focused_actions: List[str] = None,
        verify_options: str = "-t 1",
        keep_tmp_file: bool = True,
    ) -> List[SimTrace]:
        """Find all patterns of the first query in the model, if the number of patterns is finite.
        If the number of patterns is infinite, it will loop forever.
        It will always search the shortest patterns first, i.e., `verify_options: str = "-t 1"`.
        If you want the fastest patterns first, you can let `verify_options: str = "-t 2"`.

        Args:
            focused_actions (List[str], optional): the set of actions you are focused on. Only events in `focused_actions` will be analyzed when `find_all_patterns`. Defaults to None, it will automatically extract all events from current model.
            verify_options: (str, optional): model checking options of verifyta. Get more details by verifyta -h. Defaults to `-t 1`, and it will search from shortest pattern. Other options, `-t 2` from the fastest pattern.
            keep_tmp_file (bool, optional): whether to keep the temp file such as `xtr` or in-process `xml`. Defaults to True.

        Returns:
            List[SimTrace]: the list of found patterns.
        """
        res = []
        new_model = self.copy_as(f"tmp_find_all_patterns_{uuid.uuid4()}.xml")
        all_patterns_iter = new_model.find_all_patterns_iter(focused_actions, verify_options, keep_tmp_file)
        for simtrace in all_patterns_iter:
            # print(simtrace.untime_pattern)
            res.append(simtrace)
        if not keep_tmp_file:
            os.remove(new_model.model_path)
        return res

    def __add_all_patterns_template(
        self,
        observations: List[str] | List[tuple[str, str, str]],
        focused_actions: List[str] | None = None,
        template_name: str = "all_patterns_monitor",
        is_strict: bool = True,
        all_patterns: bool = False,
    ) -> None:
        """
        Currently just call add_observer_monitor
        """
        return self.add_observer_monitor(
            observations, focused_actions, template_name, is_strict, all_patterns
        )

    def find_all_patterns_iter(
        self,
        focused_actions: List[str] = None,
        verify_options: str = "-t 1",
        keep_tmp_file: bool = True,
    ) -> SimTrace:
        """Find all patterns that satisfy `self.queries[0]` using a generator.

        Args:
            focused_actions (List[str], optional): the set of actions you are focused on. Only events in `focused_actions` will be analyzed when `find_all_patterns`. Defaults to None, it will automatically extract all events from current model.
            verify_options: (str, optional): model checking options of verifyta. Get more details by verifyta -h. Defaults to `-t 1`, and it will search from shortest pattern. Other options, `-t 2` from the fastest pattern.
            keep_tmp_file (bool, optional): whether to keep the temp file such as `xtr` or in-process `xml`. Defaults to True.

        Yields:
            SimTrace: a pattern that satisfies the query.
        """

        query = self.queries[0]
        query = query.strip()
        if not (query.startswith("A[]") or query.startswith("E<>")):
            raise NotImplementedError("Only support E<> and A[] query!")

        if query.startswith("A[]"):
            default_query = query[3:].strip()
            if default_query[0] == "!":
                default_query = "E<> " + default_query[1:].strip()
            elif default_query[0:3] == "not":
                default_query = "E<> " + default_query[3:].strip()
            else:
                default_query = "E<> ! " + default_query.strip()
        else:
            default_query = query

        model_uuid = self.model_path.split("_")[-1]
        new_model_path = f"tmp_find_all_patterns_iter_{model_uuid}"
        new_umodel = self.copy_as(new_path=new_model_path)
        # tmp_find_all_iter_dde41bdf-7482-44f0-8674-ede5fd97e5c8.xml
        new_umodel.queries = default_query
        # print(f"create a new model: {new_umodel.model_path}")

        # Initial pattern search
        new_pattern = new_umodel.find_a_pattern(
            focused_actions, keep_tmp_file, verify_options
        )
        if new_pattern is None:
            if not keep_tmp_file:
                # print(new_umodel.model_path)
                # print("removed and return none.")
                os.remove(new_umodel.model_path)
                # os.remove(os.path.splitext(new_umodel.model_path)[0] + '-1.xtr')
            return

        monitor_id = 0
        pattern_count = 0
        while new_pattern is not None:
            yield new_pattern
            pattern_count += 1
            # iterator should not have max_patterns
            # if max_patterns is not None and pattern_count >= max_patterns:
            #     break

            monitor_id += 1
            # Add new monitor for the found pattern
            new_observes = self.__parse_observations(new_pattern.actions)

            new_umodel.__add_all_patterns_template(
                template_name=f"all_patterns_monitor_{monitor_id}",
                observations=new_observes,
                focused_actions=focused_actions,
                is_strict=True,
                all_patterns=True,
            )

            query_str = " && ".join(
                [f"!all_patterns_monitor_{i}.pass" for i in range(1, monitor_id + 1)]
            )
            query_str = f"{default_query} && {query_str}"

            new_umodel.queries = query_str
            new_pattern = new_umodel.find_a_pattern(
                focused_actions, keep_tmp_file=keep_tmp_file
            )

        if not keep_tmp_file:
            # print(f"remove {new_umodel.model_path}")
            os.remove(new_umodel.model_path)
            # os.remove(os.path.splitext(new_umodel.model_path)[0] + '-1.xtr')

    def __is_valid_suffix(
        self,
        sigma_o: List[str],
        sigma_un: List[str],
        fault: str,
        observation_suffix: List[str],
        keep_tmp_file=True,
    ) -> (bool, "UModel"):
        """determine whether a `observation_suffix` sequence can happen after the `fault`.

        This function will NOT modify the model, a copy named 'tmp_diagnosable_suffix.xml' will be generated, which will be returned by the function.

        Args:
            sigma_o (List[str]): the set of observable events.
            sigma_un (List[str]): the set of unobservable events.
            fault (str): fault name.
            observation_suffix (List[str]): latest observation sequence (suffix sequence).
            keep_tmp_file (bool, optional): whether to keep the temp file such as `xtr` or in-process `xml`. Defaults to True.

        Returns:
            (bool, UModel): 
                `bool` represents whether a `observation_suffix` sequence can happen after the `fault`.
                `UModel` is the copied model.

        """
        tmp_model = self.copy_as(f"tmp_diagnosable_suffix_{uuid.uuid4()}.xml")

        template = Monitors.obs_after_fault_monitor(
            "MObsAfterFault",
            observation_suffix,
            sigma_o,
            sigma_un,
            fault,
            tmp_model.max_location_id + 1,
        )
        tmp_model.add_template(template)
        tmp_model.add_template_to_system(template.name)
        tmp_model.queries = "E<> MObsAfterFault.pass"
        res = tmp_model.verify(keep_tmp_file=keep_tmp_file)
        if not keep_tmp_file:
            os.remove(tmp_model.model_path)
            return ("is satisfied" in res, None)
        return ("is satisfied" in res, tmp_model)

    # def diagnosable_one_fault(self, fault: str, n: int, sigma_o: List[str], sigma_un: List[str], visual=False, keep_tmp_file=True) -> bool:
    # fault_diagnosability_early_return
    # fault_diagnosability_ER+TC
    # fault_diagnosability_ER+TC+MT
    def fault_diagnosability(
        self,
        fault: str,
        n: int,
        sigma_o: List[str],
        sigma_un: List[str],
        visual=False,
        keep_tmp_file=True,
    ) -> (bool, SimTrace):
        """Determine whether the `fault` is `n` diagnosable.

        This function will NOT modify the model. It will copy to 'tmp_diagnosable_suffix.xml' and 'tmp_identify.xml'
        Note: If not keep_tmp_file, it won't be able to get the trace because the tmp model is removed.

        Args:
            fault (str): fault name
            n (int): n-diagnosability
            sigma_o (List[str]): the set of observable events,
            sigma_un (List[str]): the set of unobservable events,
            visual (bool, optional): whether to visualize the analyzing process with a progress bar. Defaults to False.
            keep_tmp_file (bool, optional): whether to keep the temp file such as `xtr` or in-process `xml`. Defaults to True.

        Returns:
            (bool, SimTrace):
                bool: whether the fault is n-diagnosable.
                SimTrace: if is not n-diagnosable, a `SimTrace` will be returend as a proof.
        """
        if visual:
            from tqdm import tqdm

            for suffix in tqdm(
                product(sigma_o, repeat=n),
                total=len(sigma_o) ** n,
                desc=f"   {n}-diagnosability for '{fault}'",
            ):
                suffix = list(suffix)
                if self.__is_valid_suffix(
                    sigma_o, sigma_un, fault, suffix, keep_tmp_file
                )[0]:
                    # print('    valid_suffix: ', suffix)
                    # Note: tmp_model is removed. So if you need the trace, set keep_tmp_file = True
                    verify_res, trace = self.fault_identification(
                        suffix, fault, sigma_o, sigma_un, keep_tmp_file
                    )

                    if verify_res:
                        continue
                    else:
                        # print(f"   '{fault}' is NOT {n}-diagnosable because of the suffix {suffix}.")
                        return False, trace
                else:
                    # print('NOT valid suffix: ', suffix)
                    continue
        else:
            # for suffix in list(product()):
            for suffix in product(sigma_o, repeat=n):
                suffix = list(suffix)
                if self.__is_valid_suffix(
                    sigma_o, sigma_un, fault, suffix, keep_tmp_file
                )[0]:
                    # print('    valid_suffix: ', suffix)

                    # tmp_model is removed. So if you need the trace, set keep_tmp_file = True
                    verify_res, trace = self.fault_identification(
                        suffix, fault, sigma_o, sigma_un, keep_tmp_file
                    )
                    if verify_res:
                        continue
                    else:
                        # print(f"   '{fault}' is NOT {n}-diagnosable because of the suffix {suffix}.")
                        return False, trace
                else:
                    # print('NOT valid suffix: ', suffix)
                    continue
        # print(f"   {fault} is {n}-diagnosable.")
        return True, None

    def fault_diagnosability_optimized(
        self,
        fault: str,
        n: int,
        sigma_o: List[str],
        sigma_un: List[str],
        keep_tmp_file=True,
    ) -> (bool, SimTrace):
        """Determine whether the `fault` is `n` diagnosable.

        This function will NOT modify the model. It will copy to 'tmp_diagnosable_suffix.xml' and 'tmp_identify.xml'
        Note: If not keep_tmp_file, it won't be able to get the trace because the tmp model is removed.

        Args:
            fault (str): fault name
            n (int): n-diagnosability
            sigma_o (List[str]): the set of observable events,
            sigma_un (List[str]): the set of unobservable events,
            keep_tmp_file (bool, optional): whether to keep the temp file such as `xtr` or in-process `xml`. Defaults to True.

        Returns:
            (bool, SimTrace):
                bool: whether the fault is n-diagnosable.
                SimTrace: if is not n-diagnosable, a `SimTrace` will be returend as a proof.
        """
        # FIX ME: bugs to be test
        # should provide different optimization strategies, such as DFS, BFS, randomized
        # here we provide DFS
        root = MyTree(sigma_o=sigma_o, n=n)
        if root.grow():
            while True:
                node = root.leftmost_not_verified_node
                if node is None:
                    return True
                # check if is valid observation sequence
                suffix = list(node.observation_sequence)
                node.has_checked = True
                node.is_valid = self.__is_valid_suffix(sigma_o, sigma_un, fault, suffix, keep_tmp_file)[0]
                # check if it can identify the fault
                if node.is_valid and node.depth == n:
                    can_detect, trace = self.fault_identification(suffix, fault, sigma_o, sigma_un, keep_tmp_file)
                    if not can_detect and node.depth == n:
                        return False, trace

    def fault_identification(
        self,
        suffix_sequence: List[str],
        fault: str,
        sigma_o: List[str],
        sigma_un: List[str],
        keep_tmp_file=True,
    ) -> (bool, SimTrace):
        """Do fault identification of `fault` with `suffix_sequence`.

        Args:
            suffix_sequence (List[str]): latest observation sequence.
            fault (str): the fault to be identified.
            sigma_o (List[str]): the set of observable events.
            sigma_un (List[str]): the set of unobservable events.
            keep_tmp_file (bool, optional): whether to keep the temp file such as `xtr` or in-process `xml`. Defaults to True.

        Returns:
            bool: whether the fault can be identified with `suffix_sequence`.
            SimTrace: if the `fault` can not be identified, a counter-example will be returned.
        """

        tmp_model = self.copy_as(f"tmp_identify_{uuid.uuid4()}.xml")
        sequence_monitor = Monitors.observer_suffix_monitor(
            name="MObserverSuffix",
            suffix_sequence=suffix_sequence,
            sigma_o=sigma_o,
            sigma_un=sigma_un,
            init_ref=tmp_model.max_location_id + 1,
        )
        tmp_model.add_template(sequence_monitor)
        tmp_model.add_template_to_system(sequence_monitor.name)

        f = fault
        fault_monitor = Monitors.fault_monitor(
            f"{f}_Monitor", f, init_ref=tmp_model.max_location_id + 1
        )
        tmp_model.add_template(fault_monitor)
        tmp_model.add_template_to_system(fault_monitor.name)
        # must imply
        tmp_model.queries = f"MObserverSuffix.pass-->{f}_Monitor.pass"
        res = tmp_model.verify().find("NOT") == -1
        trace = tmp_model.easy_verify(keep_tmp_file=keep_tmp_file)
        if not keep_tmp_file:
            os.remove(tmp_model.model_path)
        return (res, trace)

    def fault_tolerance(
        self,
        target_state: str,
        identified_faults: List[str],
        safety_events: List[str],
        sigma_f: List[str],
        sigma_c: List[str],
        control_length: int,
        keep_tmp_file=True,
    ) -> str:
        """Tolerate the `identified_faults` such that the system can reach the `target_state`. 

        Examples:
            >>> possible return results
            "Fault can NOT be tolerated" 
            "Fault can be tolerated, control sequence tail: ['a1', 'a2'], trace: ['a1', 'a2', 'a3', 'a4']"
            "Fault may be tolerated, control sequence tail: ['a1', 'a2'], trace: ['a1', 'a2', 'a3', 'a4']"
            "Fault may be tolerated" means that the the provided control sequence is not confirmed to tolerate `identified_faults`, 
            but there exists such a trace that lead to `target_state`.

        Args:
            target_state (str): the expression of the target state to be reached, which will be concatinated to the ending of TCTL. For example: `f"E<> MInputAfterFault.pass and {target_state}"`.
            identified_faults (List[str]): the set of identified faults.
            safety_events (List[str]): the sequence of safety events that should be applied just after the fault.
            sigma_f (List[str]): the set of fault events.
            sigma_c (List[str]): the set of control events.
            control_length (int): the maximum length of control sequence, i.e., the `identified_faults` should be tolerated within `control_length` of control events.
            keep_tmp_file (bool): whether to keep the temp file such as `xtr` or in-process `xml`. Defaults to True.

        Returns:
            str: the result of tolerance, the control sequence tail, and the trace.
        """
        for _ in range(len(identified_faults)):
            tmp_model = self.copy_as(f"tmp_tolerance_design_input_{uuid.uuid4()}.xml")

            template = Monitors.input_after_fault_monitor(
                "MInputAfterFault",
                identified_faults=identified_faults,
                protecting_events=safety_events,
                sigma_fault=sigma_f,
                sigma_control=sigma_c,
                control_length=control_length,
                init_ref=tmp_model.max_location_id + 1,
            )
            tmp_model.add_template(template)
            tmp_model.add_template_to_system(template.name)
            tmp_model.queries = f"E<> MInputAfterFault.pass and {target_state}"

            result = tmp_model.__find_all_patterns_sfx(
                identified_faults=identified_faults,
                focused_actions=sigma_c + identified_faults,
                keep_tmp_file=keep_tmp_file,
            )  # find all patterns, return SimTrace

            if not keep_tmp_file:
                os.remove(tmp_model.model_path)

        if len(result) == 0:
            return "Fault can NOT be tolerated"

        for i, result_i in enumerate(result):
            tmp_model = self.copy_as(f"tmp_tolerance_check_input_{uuid.uuid4()}.xml")
            control_tail = result_i.untime_pattern[-control_length:]
            # print('==================== control tail ======================\n')
            # print(control_tail)
            # print('\n')
            # print('==================== control tail end ======================\n')
            template = Monitors.tolerance_checker_monitor(
                "MToleranceChecker",
                identified_faults=identified_faults,
                protecting_events=safety_events,
                sigma_fault=sigma_f,
                sigma_control=sigma_c,
                control_sequence=control_tail,
                init_ref=tmp_model.max_location_id + 1,
            )
            tmp_model.add_template(template)
            tmp_model.add_template_to_system(template.name)
            tmp_model.queries = f"MToleranceChecker.pass --> {target_state}"
            verify_res = "is satisfied" in tmp_model.verify()

            if not keep_tmp_file:
                os.remove(tmp_model.model_path)

            if verify_res:
                # print(f"    Control sequence: {control_tail} can help to tolerate the faults {identified_faults}.")
                return f"Fault can be tolerated, control sequence tail: {control_tail}, trace: {result_i}"
            else:
                return f"Fault may be tolerated, control sequence tail: {control_tail}, trace: {result_i}"

    def __find_all_patterns_sfx(
        self,
        identified_faults: List[str],
        focused_actions: List[str] = None,
        keep_tmp_file=True,
    ) -> List[SimTrace]:
        queries = self.queries
        if len(queries) == 0:
            return []

        query = queries[0]
        query = query.strip()
        if not (query.startswith("A[]") or query.startswith("E<>")):
            raise NotImplementedError("Only support E<> and A[] query!")

        if query.startswith("A[]"):
            default_query = query[3:].strip()
            if default_query[0] == "!":
                default_query = "E<> " + default_query[1:].strip()
            elif default_query[0:3] == "not":
                default_query = "E<> " + default_query[3:].strip()
            else:
                default_query = "E<> ! " + default_query.strip()
        else:
            default_query = query

        new_model_path = os.path.splitext(self.model_path)[0] + "_pattern.xml"
        new_umodel = self.copy_as(new_path=new_model_path)
        new_umodel.queries = default_query

        query_str = default_query
        # 根据初始的pattern构建monitor并循环, 初始Moniter为0
        all_patterns = []
        monitor_id = 0

        for new_pattern in self.find_all_patterns_iter(focused_actions=focused_actions, keep_tmp_file=keep_tmp_file):
            all_patterns.append(new_pattern)

            monitor_id += 1

            fault_idx = 0
            for action in new_pattern.actions:
                fault_idx += 1
                if action in identified_faults:
                    break
            print(new_pattern.actions[:fault_idx])
            print(type(new_pattern.actions[:fault_idx]))
            new_observes = self.__parse_observations(new_pattern.actions[:fault_idx])
            new_umodel.__add_all_patterns_template(
                template_name=f"all_patterns_monitor_{monitor_id}",
                observations=new_observes,
                focused_actions=focused_actions,
                is_strict=True,
                all_patterns=True,
            )

            # 删除initial location相连的fail0
            observer_template: Template = new_umodel.templates.pop()
            idx = 0
            target_location_id = -1
            for i, l in enumerate(observer_template.locations):
                if l.name == "fail0":
                    idx = i
                    target_location_id = l.location_id
                    break
            del observer_template.locations[idx]

            edges_idx_to_be_removed = []
            for i, e in enumerate(observer_template.edges):
                if e.target_location_id == target_location_id:
                    edges_idx_to_be_removed.append(i)

            for i in reversed(edges_idx_to_be_removed):
                del observer_template.edges[i]

            new_umodel.templates.append(observer_template)
            new_umodel.save()

            # 构造验证语句
            # 构造monitor.pass
            # E<> Monitor0.pass & !Monitor1.pass
            query_str = " && ".join(
                [f"!all_patterns_monitor_{i}.pass" for i in range(1, monitor_id + 1)]
            )
            # E<> !Monitor0.pass & !Monitor1.pass
            query_str = f"{default_query} && {query_str}"

            new_umodel.queries = query_str

        if not keep_tmp_file:
            os.remove(new_umodel.model_path)
        return all_patterns

    def load_xtr_trace(self, xtr_trace_path: str, keep_if=False) -> SimTrace | None:
        """Analyze the `xtr_trace_path` trace file generated by model and return the instance `SimTrace`.

        The internal process is as following:
        1. Convert the `model_path` model into a `.if` file.
        2. Analyze `.if` file and the `xtr_trace_path` to get the instance `SimTrace`.
        3. reference: https://github.com/UPPAALModelChecker/utap.

        Args:
            model_path (str): the path of the `.xml` model file
            xtr_trace_path (str): the path of the `.xtr` trace file
            keep_if (bool): keep the `.if` file

        Raises:
            FileNotFoundError: if the `xtr_trace_path` file does not exist, raise FileNotFoundError in Verifyta().compile_to_if(self.model_path)
            ValueError: if the `xtr_trace_path` file is not a `.xtr` file, raise ValueError in Verifyta().compile_to_if(self.model_path)
            ValueError: if the `xtr_trace` does not fit the model, raise ValueError in utap_parser(if_name, xtr_trace_path)

        Returns:
            SimTrace | None: if you want to save the parsed raw trace, you can use SimTrace.save_raw(file_name)
        """
        if_name = Verifyta().compile_to_if(self.model_path)
        trace_text = utap_parser(if_name, xtr_trace_path, keep_if=keep_if)

        res = SimTrace(trace_text)
        res.trim_transitions(self.model_path)
        return res
