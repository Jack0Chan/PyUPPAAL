""" NTA Module
    This module contains classes and functions for working with UPPAAL NTA models.
    
"""
from __future__ import annotations
from dataclasses import dataclass
import xml.etree.ElementTree as ET
from typing import List, Tuple


@dataclass
class Location:
    """
    Represents a location in a UPPAAL model.

    A location in UPPAAL is a state in the state machine of a template. It can have various properties like being an initial, urgent, or committed state, along with invariants, names, and positions.

    Example Usage:
        # Creating a basic location with an ID and position.
        location = Location(location_id=1, location_pos=(100, 200))

        # Creating a location with additional properties.
        location = Location(
            location_id=2,
            location_pos=(150, 250),
            name="Start",
            invariant="x <= 5",
            is_initial=True
        )
    """

    def __init__(self, location_id: int, location_pos: Tuple(int, int),
                 name: str = None, name_pos: Tuple(int, int) = None,
                 invariant: str = None,  invariant_pos: Tuple(int, int) = None,
                 rate_of_exponential: float = None, rate_of_exp_pos: Tuple(int, int) = None,
                 is_initial: bool = False, is_urgent: bool = False, is_committed: bool = False,
                 is_branchpoint: bool = False,
                 comments: str = None, comments_pos: Tuple(int, int) = None,
                 test_code_on_enter: str = None, test_code_on_exit: str = None) -> None:
        """_summary_

        Args:
            location_id (int): A unique identifier for the location.
            location_pos (Tuple[int, int]): The graphical position of the location in the UPPAAL model.
            name (str, optional): The name of the location. Defaults to None.
            name_pos (Tuple[int, int], optional): The position of the location's name label. Defaults to None.
            invariant (str, optional): The invariant condition of the location. Defaults to None.
            invariant_pos (Tuple[int, int], optional): The position of the invariant label. Defaults to None.
            rate_of_exponential (float, optional): The rate of exponential distribution for stochastic transitions. Defaults to None.
            rate_of_exp_pos (Tuple[int, int], optional): The position of the rate of exponential label. Defaults to None.
            is_initial (bool, optional): Indicates if this location is the initial location. Defaults to False.
            is_urgent (bool, optional): Indicates if this location is an urgent location. Defaults to False.
            is_committed (bool, optional): Indicates if this location is a committed location. Defaults to False.
            is_branchpoint (bool, optional): Indicates if this location is a branchpoint. Defaults to False.
            comments (str, optional): Comments or annotations for the location. Defaults to None.
            comments_pos (Tuple[int, int], optional): The position of the comment label. Defaults to None.
            test_code_on_enter (str, optional): Test code to be executed upon entering this location. Defaults to None.
            test_code_on_exit (str, optional): Test code to be executed upon exiting this location. Defaults to None.
        """
        # 界面隐含属性
        # location_id自动更新，用户不要修改
        self.location_id: int = location_id
        self.location_pos: Tuple(int, int) = location_pos

        # 界面文本属性
        # UI Tab: Location
        self.name: str | None = name
        self.name_pos: Tuple(int, int) | None = name_pos

        self.invariant: str | None = invariant
        self.invariant_pos: Tuple(int, int) | None = invariant_pos

        self.rate_of_exponential: float | None = rate_of_exponential
        self.rate_of_exp_pos: Tuple(int, int) | None = rate_of_exp_pos

        self.is_initial: bool = is_initial
        self.is_urgent: bool = is_urgent
        self.is_committed: bool = is_committed
        self.is_branchpoint: bool = is_branchpoint

        # UI Tab: Comments
        self.comments: str | None = comments
        self.comments_pos: Tuple(int, int) | None = comments_pos

        # UI Tab: Test Code
        self.test_code_on_enter: str | None = test_code_on_enter
        self.test_code_on_exit: str | None = test_code_on_exit

    @property
    def Element(self) -> ET.Element:
        """xml element as xml.etree.ElementTree.Element

        Returns:
            ET.Element: xml.etree.ElementTree.Element
        """
        # 如果是branch point，xml标签为branch point
        if self.is_branchpoint:
            res = ET.Element('branchpoint',
                             {'id': f'id{self.location_id}',
                              'x': str(self.location_pos[0]),
                              'y': str(self.location_pos[1]),
                              })
            res.text = " "
            return res
        else:
            # 如果是正常的location，xml标签为location
            x = self.location_pos[0]
            y = self.location_pos[1]
            res = ET.Element('location',
                             {'id': f'id{self.location_id}',
                              'x': str(x),
                              'y': str(y)})

            # 添加名字
            if self.name is not None:
                if self.name_pos is None:
                    self.name_pos = (x-10, y-34)
                elem = ET.Element('name', {'x': str(self.name_pos[0]),
                                           'y': str(self.name_pos[1])})
                elem.text = self.name
                res.append(elem)

            # 添加 inv
            if self.invariant is not None:
                if self.invariant_pos is None:
                    self.invariant_pos = (x-10, y+17)
                elem = ET.Element('label', {'kind': 'invariant',
                                            'x': str(self.invariant_pos[0]),
                                            'y': str(self.invariant_pos[1])})
                elem.text = self.invariant
                res.append(elem)

            # 添加 rate_of_exponential
            if self.rate_of_exponential is not None:
                if self.rate_of_exp_pos is None:
                    self.rate_of_exp_pos = (x-10, y+34)
                elem = ET.Element('label', {'kind': 'exponentialrate',
                                            'x': str(self.rate_of_exp_pos[0]),
                                            'y': str(self.rate_of_exp_pos[1])})
                elem.text = str(self.rate_of_exponential)
                res.append(elem)

            # is_initial需要再template里指定

            # 添加 test_code_on_enter
            if self.test_code_on_enter is not None:
                elem = ET.Element('label', {'kind': 'testcodeEnter'})
                elem.text = self.test_code_on_enter
                res.append(elem)

            # 添加 test_code_on_exit
            if self.test_code_on_exit is not None:
                elem = ET.Element('label', {'kind': 'testcodeExit'})
                elem.text = self.test_code_on_exit
                res.append(elem)

            # 添加 comments
            if self.comments is not None:
                if self.comments_pos is None:
                    self.comments_pos = (x-10, y+59)
                elem = ET.Element('label', {'kind': 'comments',
                                            'x': str(self.comments_pos[0]),
                                            'y': str(self.comments_pos[1])})
                elem.text = self.comments
                res.append(elem)

            # 添加 is_committed
            if self.is_committed:
                res.append(ET.Element('committed'))

            # 添加 is_urgent
            if self.is_urgent:
                res.append(ET.Element('urgent'))
            return res

    @property
    def xml(self) -> str:
        """获取xml字符串

        Returns:
            str: xml字符串
        """
        element = self.Element
        return ET.tostring(element, encoding="utf-8").decode("utf-8")

    @staticmethod
    def from_xml(location_xml: str | ET.Element) -> Location:
        """_summary_

        Args:
            location_xml (str | ET.Element): string that meets xml element format of location. For example:
            A committed location with many properties such as invariant, testcode, etc.         
            <location id="id1" x="0" y="0">
                <name x="-10" y="-34">location_name</name>
                <label kind="invariant" x="-10" y="17">inv_inv</label>
                <label kind="exponentialrate" x="-10" y="34">roe_roe</label>
                <label kind="testcodeEnter">on_enter_on_enter</label>
                <label kind="testcodeExit">on_exit_on_exit</label>
                <label kind="comments" x="-10" y="59">comments_comments</label>
                            <committed/>
                    </location>

        Returns:
            Location: location instance
        """
        # root of location element
        root = location_xml
        if isinstance(location_xml, str):
            root = ET.fromstring(location_xml)

        if root.tag == "branchpoint":
            return Location(location_id=int(root.get("id")[2:]),
                            location_pos=(int(root.get("x")), int(root.get("y"))),
                            is_branchpoint=True)
        elif root.tag == "location":
            name_elem = root.find("name")
            name: str = None
            # (x, y)
            name_pos = None
            if name_elem is not None:
                name = name_elem.text
                name_pos = (int(name_elem.get("x")), int(name_elem.get("y")))

            # 获取 location 的各种 label 对应的 text
            invariant = None
            invariant_pos = None
            rate_of_exponential = None
            rate_of_exp_pos = None
            comments = None
            comments_pos = None
            test_code_on_enter = None
            test_code_on_exit = None
            for label_elem in root.iter("label"):
                if label_elem.get('kind') == "invariant":
                    invariant = label_elem.text
                    invariant_pos = (int(label_elem.get("x")), int(label_elem.get("y")))
                elif label_elem.get('kind') == "exponentialrate":
                    rate_of_exponential = float(label_elem.text)
                    rate_of_exp_pos = (int(label_elem.get("x")), int(label_elem.get("y")))
                elif label_elem.get('kind') == "comments":
                    comments = label_elem.text
                    comments_pos = (int(label_elem.get("x")), int(label_elem.get("y")))
                elif label_elem.get('kind') == "testcodeEnter":
                    test_code_on_enter = label_elem.text
                elif label_elem.get('kind') == "testcodeExit":
                    test_code_on_exit = label_elem.text
                else:
                    pass
            # 判断location类型(initial, urgent, committed)
            # 注意, is_initial不是从location里表示, 而是在template里有initial_ref = location_id标识。
            # 但是用户使用的时候, 为了符合用户操作界面的直觉，可以对location设置initial。
            # is_initial = root.find("initial") is not None
            # 在加载的时候，我们将从template加载is_initial, 这里默认设置成False
            is_urgent = root.find("urgent") is not None
            is_committed = root.find("committed") is not None

            res = Location(location_id=int(root.get("id")[2:]),
                           location_pos=(int(root.get("x")), int(root.get("y"))),
                           name=name,
                           name_pos=name_pos,
                           invariant=invariant,
                           invariant_pos=invariant_pos,
                           rate_of_exponential=rate_of_exponential,
                           rate_of_exp_pos=rate_of_exp_pos,
                           # 在加载的时候，我们将从template加载is_initial, 这里默认设置成False
                           is_initial=False,
                           is_urgent=is_urgent,
                           is_committed=is_committed,
                           comments=comments,
                           comments_pos=comments_pos,
                           test_code_on_enter=test_code_on_enter,
                           test_code_on_exit=test_code_on_exit)

            return res
        else:
            raise ValueError(f"can not parse: {root.tag}. Only support location, branchpoint.")


@dataclass
class Edge:
    """在界面里叫Edge, 在xml里叫做transition
    Represents a transition (edge) between two locations in a UPPAAL model.

    In UPPAAL, an edge (referred to as 'transition' in XML) defines the behavior and conditions for moving from one state (location) to another. It can include synchronization labels, guards, updates, selections, and more.

    Example Usage:
        # Creating an edge with basic properties.
        edge = Edge(
            source_location_id=1, 
            target_location_id=2,
            source_location_pos=(100, 200),
            target_location_pos=(300, 400),
            guard="x < 5"
        )

        # Creating an edge with additional properties like synchronization and update.
        edge = Edge(
            source_location_id=1, 
            target_location_id=2,
            source_location_pos=(100, 200),
            target_location_pos=(300, 400),
            sync="a!",
            update="x=0"
        )
    """

    def __init__(self, source_location_id: int, target_location_id: int,
                 source_location_pos: Tuple(int, int),
                 target_location_pos: Tuple(int, int),
                 select: str = None, select_pos: Tuple(int, int) = None,
                 sync: str = None, sync_pos: Tuple(int, int) = None,
                 update: str = None, update_pos: Tuple(int, int) = None,
                 guard: str = None, guard_pos: Tuple(int, int) = None,
                 probability_weight: float = None, prob_weight_pos: Tuple(int, int) = None,
                 comments: str = None, comments_pos: Tuple(int, int) = None,
                 test_code: str = None,
                 nails: List[Tuple(int, int)] = []) -> None:
        """

        Args:
            source_location_id (int): The ID of the source location from where the edge originates.
            target_location_id (int): The ID of the target location where the edge leads to.
            source_location_pos (Tuple[int, int]): The graphical position of the source location in the UPPAAL model.
            target_location_pos (Tuple[int, int]): The graphical position of the target location in the UPPAAL model.
            select (str, optional): The selection expression for non-deterministic assignments. Defaults to None.
            select_pos (Tuple[int, int], optional): The position of the select label. Defaults to None.
            sync (str, optional): The synchronization label used for process synchronization. Defaults to None.
            sync_pos (Tuple[int, int], optional): The position of the sync label. Defaults to None.
            update (str, optional): The update expression executed when the transition is taken. Defaults to None.
            update_pos (Tuple[int, int], optional): The position of the update label. Defaults to None.
            guard (str, optional): The guard condition that must be true for the transition to be enabled. Defaults to None.
            guard_pos (Tuple[int, int], optional): The position of the guard label. Defaults to None.
            probability_weight (float, optional): The probability weight for stochastic transitions. Defaults to None.
            prob_weight_pos (Tuple[int, int], optional): The position of the probability weight label. Defaults to None.
            comments (str, optional): Comments or annotations for the edge. Defaults to None.
            comments_pos (Tuple[int, int], optional): The position of the comment label. Defaults to None.
            test_code (str, optional): Test code associated with the edge. Defaults to None.
            nails (List[Tuple[int, int]], optional): List of coordinates for bend points (nails) in the edge. Defaults to an empty list.

        Raises:
            ValueError: Raised if both probability_weight and guard are set, as an edge cannot be both a normal and a probability edge.

        """
        # 界面隐含属性
        self.source_location_id: int = source_location_id
        self.source_location_pos: Tuple(int, int) = source_location_pos

        self.target_location_id: int = target_location_id
        self.target_location_pos: Tuple(int, int) = target_location_pos

        # 界面文本属性
        # UI Tab: Edge
        self.select: str | None = select
        self.select_pos: Tuple(int, int) | None = select_pos
        # 普通 edge 包含 guard，不包含 probability_weight
        self.guard: str | None = guard
        self.guard_pos: Tuple(int, int) | None = guard_pos

        self.sync: str | None = sync
        self.sync_pos: Tuple(int, int) | None = sync_pos

        self.update: str | None = update
        self.update_pos: Tuple(int, int) | None = update_pos

        # 由 branch_point 出来的边带有 probability_weight, 没有guard
        self.probability_weight: float | None = probability_weight
        self.prob_weight_pos: Tuple(int, int) | None = prob_weight_pos

        # UI Tab: Comments
        self.comments: str | None = comments
        self.comments_pos: Tuple(int, int) | None = comments_pos

        # UI Tab: Test Code
        self.test_code: str | None = test_code

        # 转折点 List[(x, y)]
        self.nails: List[Tuple(int, int)] = nails

        # 不能同时为normal edge和probability edge
        if not (self.probability_weight is None or self.guard is None):
            err_info = "An edge can not be both normal or probability. "
            err_info += "That is, can not have both probability_weight and guard. "
            err_info += f"Currently we have: probability_weight = {self.probability_weight}, guard = {self.guard}."
            raise ValueError(err_info)

    @property
    def Element(self) -> ET.Element:
        """xml element as xml.etree.ElementTree.Element

        Returns:
            ET.Element: xml.etree.ElementTree.Element
        """
        # 两头location的中点
        x = (self.source_location_pos[0] + self.target_location_pos[0]) // 2
        y = (self.source_location_pos[1] + self.target_location_pos[1]) // 2

        transition = ET.Element('transition')
        # 构建并添加source
        source = ET.Element('source', {'ref': f'id{self.source_location_id}'})
        transition.append(source)
        # 构建并添加target
        target = ET.Element('target', {'ref': f'id{self.target_location_id}'})
        transition.append(target)

        # 构建并添加select
        if self.select is not None:
            if self.select_pos is None:
                self.select_pos = (x+18, y-51)

            label_select = ET.Element('label', {'kind': 'select',
                                                'x': str(self.select_pos[0]),
                                                'y': str(self.select_pos[1])})
            label_select.text = self.select
            transition.append(label_select)

        # 构建并添加guard
        if self.guard is not None:
            if self.guard_pos is None:
                self.guard_pos = (x+18, y-34)
            label_guard = ET.Element('label', {'kind': 'guard',
                                               'x': str(self.guard_pos[0]),
                                               'y': str(self.guard_pos[1])})
            label_guard.text = self.guard
            transition.append(label_guard)

        # 构建并添加synchronisation
        if self.sync is not None:
            if self.sync_pos is None:
                self.sync_pos = (x+18, y-17)
            label_sync = ET.Element('label', {'kind': 'synchronisation',
                                              'x': str(self.sync_pos[0]),
                                              'y': str(self.sync_pos[1])})
            label_sync.text = self.sync
            transition.append(label_sync)

         # 构建并添加assignment: update
        if self.update is not None:
            if self.update_pos is None:
                self.update_pos = (x+18, y)
            label_update = ET.Element('label', {'kind': 'assignment',
                                                'x': str(self.update_pos[0]),
                                                'y': str(self.update_pos[1])})
            label_update.text = self.update
            transition.append(label_update)

        # 构建并添加 testcode
        if self.test_code is not None:
            elem = ET.Element('label', {'kind': 'testcode'})
            elem.text = self.test_code
            transition.append(elem)

        # 构建并添加 comments
        if self.comments is not None:
            if self.comments_pos is None:
                self.comments_pos = (x+18, y+25)
            elem = ET.Element('label', {'kind': 'comments',
                                        'x': str(self.comments_pos[0]),
                                        'y': str(self.comments_pos[1])})
            elem.text = self.comments
            transition.append(elem)

        # 构建并添加probability
        if self.probability_weight is not None:
            if self.prob_weight_pos is None:
                self.prob_weight_pos = (x+18, y+44)
            elem = ET.Element('label', {'kind': 'probability',
                                        'x': str(self.prob_weight_pos[0]),
                                        'y': str(self.prob_weight_pos[1])})
            elem.text = str(self.probability_weight)
            transition.append(elem)

        # 构建并添加nail (弯曲结点)
        if self.nails is not None:
            for nail in self.nails:
                nail_element = ET.Element('nail', {'x': str(nail[0]),
                                                   'y': str(nail[1])})
                transition.append(nail_element)
        return transition

    @property
    def xml(self) -> str:
        """        
        >>> <transition>
                >>> 	<source ref="id1"/>
                >>> 	<target ref="id2"/>
                >>> 	<label kind="select" x="18" y="-51">nnn:id</label>
                >>>	    <label kind="guard" x="18" y="-34">guard:=0</label>
                >>> 	<label kind="synchronisation" x="18" y="-17">sync?</label>
                >>> 	<label kind="assignment" x="18" y="0">update</label>
                >>> 	<label kind="testcode">testcode_testcode</label>
                >>> 	<label kind="comments" x="18" y="25">comments_comments</label>
                >>> 	<nail x="51" y="42"/>
                >>> 	<nail x="76" y="34"/>
                >>> 	<nail x="68" y="0"/>
                >>> 	<nail x="102" y="42"/>
                >>> </transition>
        """
        element = self.Element
        return ET.tostring(element, encoding="utf-8").decode("utf-8")

    @staticmethod
    def from_xml(edge_xml: str | ET.Element) -> Edge:
        """ 

        Args:
            et (str | ET.Element): string that meets xml element format of branch point. 
            Example1: normal transition
            <transition>
                <source ref="id1"/>
                <target ref="id2"/>
                <label kind="select" x="18" y="-51">nnn:id</label>
                <label kind="guard" x="18" y="-34">guard:=0</label>
                <label kind="synchronisation" x="18" y="-17">sync?</label>
                <label kind="assignment" x="18" y="0">update</label>
                <label kind="testcode">testcode_testcode</label>
                <label kind="comments" x="18" y="25">comments_comments</label>
                <nail x="51" y="42"/>
                <nail x="76" y="34"/>
                    </transition>

            Example2: probability transition
        Returns:
            Edge: edge instance
        """
        root = edge_xml
        if isinstance(edge_xml, str):
            root = ET.fromstring(edge_xml)

        # 获取 edge 的各种 label 对应的 text
        select = None
        select_pos = None
        guard = None
        guard_pos = None
        sync = None
        sync_pos = None
        update = None
        update_pos = None
        probability_weight = None
        prob_weight_pos = None
        comments = None
        comments_pos = None
        test_code = None
        for label_elem in root.iter("label"):
            if label_elem.get('kind') == "select":
                select = label_elem.text
                select_pos = (int(label_elem.get("x")), int(label_elem.get("y")))
            elif label_elem.get('kind') == "guard":
                guard = label_elem.text
                guard_pos = (int(label_elem.get("x")), int(label_elem.get("y")))
            elif label_elem.get('kind') == "synchronisation":
                sync = label_elem.text
                sync_pos = (int(label_elem.get("x")), int(label_elem.get("y")))
            elif label_elem.get('kind') == "assignment":
                update = label_elem.text
                update_pos = (int(label_elem.get("x")), int(label_elem.get("y")))
            elif label_elem.get('kind') == "probability":
                probability_weight = label_elem.text
                prob_weight_pos = (int(label_elem.get("x")), int(label_elem.get("y")))
            elif label_elem.get('kind') == "testcode":
                test_code = label_elem.text
            elif label_elem.get('kind') == "comments":
                comments = label_elem.text
                comments_pos = (int(label_elem.get("x")), int(label_elem.get("y")))
            else:
                pass
        # 获取nails
        nails = []
        for nail_elem in root.iter("nail"):
            x = int(nail_elem.get("x"))
            y = int(nail_elem.get("y"))
            nails.append((x, y))

        return Edge(source_location_id=int(root.find("source").get("ref")[2:]),
                    target_location_id=int(root.find("target").get("ref")[2:]),
                    source_location_pos=(-1, -1),
                    target_location_pos=(-1, -1),
                    select=select, select_pos=select_pos,
                    guard=guard, guard_pos=guard_pos,
                    sync=sync, sync_pos=sync_pos,
                    update=update, update_pos=update_pos,
                    probability_weight=probability_weight, prob_weight_pos=prob_weight_pos,
                    comments=comments, comments_pos=comments_pos,
                    test_code=test_code,
                    nails=nails)


@dataclass
class Template:
    """ Represents a template in a UPPAAL model, defining a set of locations (states), edges (transitions), and other properties.

    A template in UPPAAL is a reusable structure that can be instantiated multiple times within a model. It contains locations, edges, declarations, and other components necessary for modeling a component or a system.

    """
    # 别忘记新发现的 branch point

    def __init__(self, name: str,
                 locations: List[Location],
                 init_ref: int,
                 edges: List[Edge] = None,
                 params: str = None,
                 declaration: str = None) -> None:
        """ Template

        Args:
            name (str): The name of the template.
            locations (List[Location]): A list of locations (states) within the template.
            init_ref (int): The reference ID of the initial location in the template.
            edges (List[Edge], optional): A list of edges (transitions) between locations. Defaults to None.
            params (str, optional): Parameters for the template. Defaults to None.
            declaration (str, optional): Declarations (variables, clocks, etc.) local to the template. Defaults to None.

        Example Usage:
            # Creating a simple template with two locations and one edge.
            loc1 = Location(location_id=1, location_pos=(100, 100), name="Start")
            loc2 = Location(location_id=2, location_pos=(200, 100), name="End")
            edge = Edge(source_location_id=1, target_location_id=2, guard="x >= 5")
            template = Template(name="ExampleTemplate", locations=[loc1, loc2], init_ref=1, edges=[edge])

            # Creating a template with declarations and parameters.
            declaration = "int counter = 0;"
            params = "int param1, int param2"
            template = Template(name="ParametrizedTemplate", locations=[loc1, loc2], init_ref=1, edges=[edge], params=params, declaration=declaration)

        """

        # <template>
        #     <name x="5" y="5">Template</name>
        #     <declaration>// Place local declarations here.</declaration>
        #     <location id="id0" x="0" y="0">
        #     </location>
        #     <init ref="id0"/>
        # </template>

        # name: str, params: str = "",
        # declaration: str = "", locations: List[Location] = [Location()],
        # transitions: List[Transition] = []

        # template 必须要有 name
        self.name: str = name
        # template 初始必有 location
        self.locations: List[Location] = locations
        # 用于指定 initial state
        self.init_ref: int = init_ref
        # template 初始可以没有边
        # self.edges: Optional(List[Edge]) = edges
        self.edges: List[Edge] | None = edges
        # params 可以不存在，即初始化时可以为空
        self.params: str | None = params
        self.declaration: str | None = declaration

        # 界面隐含属性
        # init_ref 默认为0，用户可以在 template() 通过输入 init_ref 自行调整
        # 因为与其增加 set_init() 函数使得复杂度增加
        # 不如当要设立新的 init state 时，新建另一个模型
        # init_ref 可以通过 Template() 实例化时，传入 init_ref 参数来指定
        # self.location_id: int >>> template 自身的 id 似乎没有用

    @property
    def Element(self) -> ET.Element:
        """xml element as xml.etree.ElementTree.Element

        Returns:
            ET.Element: xml.etree.ElementTree.Element
        """
        res = ET.Element('template')

        temp_name_elem = ET.Element('name')
        temp_name_elem.text = self.name
        res.append(temp_name_elem)

        if self.params is not None:
            elem = ET.Element('parameter')
            elem.text = self.params
            res.append(elem)

        if self.declaration is not None:
            elem = ET.Element('declaration')
            elem.text = self.declaration
            res.append(elem)

        # add location to template
        for location in self.locations:
            res.append(location.Element)

        # if self.branch_points is not None:
        #     for branch_point in self.branch_points:
        #         res.append(branch_point.Element)

        # init_ref 在 .xml 文件中出现的位置,
        # 是在 location 和 branch_point全部出现完之后
        init_id_elem = ET.Element('init', {'ref': f'id{self.init_ref}'})
        res.append(init_id_elem)

        if self.edges is not None:
            for edge in self.edges:
                res.append(edge.Element)
        return res

    @property
    def xml(self) -> str:
        """Convert `self` to ET.Element(part of `.xml` file) as `string`, which is not epected to be used by users.

        Returns:
            str: A string representing the `Template` instance in UPPAAL `.xml` format.
        """
        element = self.Element
        return ET.tostring(element, encoding="utf-8").decode("utf-8")

    @staticmethod
    def from_xml(template_xml: str | ET.Element) -> Template:
        """parse `template` from `.xml` file by the following steps:
        1. template的name
        2. parameter
        3. declaration
        4. location(s)
        5. branchpoint(s)
        6. init ref (id of initial location)
        7. transitions

        Args:
            template_xml (str | ET.Element): The XML string or ElementTree Element representing the UPPAAL template.

        Returns:
            Template: A Template object constructed from the parsed XML data.

        """
        root = template_xml
        if isinstance(template_xml, str):
            root = ET.fromstring(template_xml)

        # find template's name
        temp_name_elem = root.find("name")
        name: str = None
        if temp_name_elem is not None:
            name = temp_name_elem.text

        # params
        params_elem = root.find("parameter")
        params: str = None
        if params_elem is not None:
            params = params_elem.text

        # declaration
        declaration_elem = root.find("declaration")
        declaration: str = None
        if declaration_elem is not None:
            declaration = declaration_elem.text

        locations = []
        edges = []
        # branch_points = []

        for l_elem in root.iter("location"):
            locations.append(Location.from_xml(l_elem))

        for bp_elem in root.iter("branchpoint"):
            # branchpoint 是特殊的location
            locations.append(Location.from_xml(bp_elem))

        init_ref_elem = root.find("init")
        init_ref: int = None
        if init_ref_elem is not None:
            init_ref = int(init_ref_elem.get("ref")[2:])

        # edge_element, edge 也叫 transition
        for e_elem in root.iter("transition"):
            edges.append(Edge.from_xml(e_elem))

        temp_res = Template(name, locations, init_ref, edges,
                            params, declaration)

        return temp_res

    # @staticmethod
    # def input_template(name: str, signals: List[Tuple[str, str, str]], init_id: int) -> Template:
    #     """_summary_

    #     >>> monitor = Template.construct_input_template(xxx)
    #     >>> umodel = UModel(xxx)
    #     >>> umodel.add_template(monitor: Tempalte)
    #     >>> umodel.add_template_to_system(str: template_name)

    #     Args:
    #         name (str): The name of the input template.
    #         signals (List[Tuple[str, str, str]]): A list of tuples where each tuple represents an input signal.
    #             Each tuple consists of (action_name, guard_condition, invariant_condition).
    #             - action_name (str): The name of the action or signal.
    #             - guard_condition (str): The guard condition associated with the action.
    #             - invariant_condition (str): The invariant condition associated with the location.
    #         init_id (int): The initial ID to use for the locations in this template.

    #     Returns:
    #         Template: A UPPAAL template object representing the input signals with their respective guards and invariants.

    #     Example Usage:
    #         >>> input_signals = [('signal1', 'x >= 10', 'x <= 20'), ('signal2', 'y >= 5', 'y <= 10')]
    #         >>> input_template = Monitors.input_template('InputSignals', input_signals, 1)
    #         >>> print(input_template.name)
    #         'InputSignals'
    #     """

    #     # 创建locations
    #     locations = []
    #     edges = []
    #     for i, signal_i in enumerate(signals):
    #         # [signal, guard, inv, name]
    #         location_pos = (300 * i, 200)
    #         location = Location(location_id=init_id + i, location_pos=location_pos, invariant=signal_i[2])
    #         locations.append(location)
    #         # [signal, guard, inv]
    #         edge = Edge(source_location_id=init_id + i,
    #                     target_location_id=init_id + i + 1,
    #                     source_location_pos=location_pos,
    #                     target_location_pos=(location_pos[0]+300, 200),
    #                     guard=signal_i[1], sync=signal_i[0]+'!')
    #         edges.append(edge)
    #     # 需要多一个尾巴location
    #     location = Location(location_id=init_id + len(signals), location_pos=(300 * len(signals), 200), name='pass')
    #     locations.append(location)

    #     # 获得clock name并创建declaration
    #     clk_name = signals[0][1].split('>')[0]
    #     declaration = f'clock {clk_name};'
    #     input_temp = Template(name=name, locations=locations,
    #                           init_ref=init_id, edges=edges, declaration=declaration)
    #     return input_temp
