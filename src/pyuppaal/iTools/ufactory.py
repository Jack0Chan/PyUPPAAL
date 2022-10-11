from typing import List, Tuple, Dict
import xml.etree.cElementTree as ET


class UFactory:
    """
    Generate xml elements of UPPAAL, including queries, declaration, location, transition, template and so on.
    """
    @staticmethod
    def __query(query: str) -> ET.Element:
        """Components of `UFactory.queries()`.

        >>> <query>
        >>>     <formula>E&lt;&gt; Output.pass</formula>
        >>>     <comment />
        >>> </query>

        Args:
            query (str): _description_

        Returns:
            ET.Element: _description_
        """
        query_elem = ET.Element('query')

        # 构建并添加formula
        formula_elem = ET.Element('formula')
        formula_elem.text = query
        query_elem.append(formula_elem)

        # 构建并添加comment
        query_elem.append(ET.Element('comment'))
        return query_elem

    @staticmethod
    def queries(queries: List[str]) -> ET.Element:
        """_summary_

        >>> <queries>
        >>>     <query>
        >>>         <formula>E&lt;&gt; Output.pass</formula>
        >>>         <comment />
        >>>     </query>
        >>>     <query>
        >>>         <formula>E&lt;&gt; Output2.pass</formula>
        >>>         <comment />
        >>>     </query>
        >>> </queries>

        Args:
            queries (List[str]): _description_

        Returns:
            ET.Element: _description_
        """
        queries_elem = ET.Element('queries')
        # 构建并加入多个queries element
        for query in queries:
            queries_elem.append(UFactory.__query(query))
        return queries_elem

    # @staticmethod
    # def declaration(declaration: str) -> ET.Element:
    #     """Generate the declararion of UPPAAL.

    #     Args:
    #         declaration (str): all contents of declaration.

    #     Returns:
    #         ET.Element: _description_
    #     """
    #     dec_elem = ET.Element('declaration')
    #     dec_elem.text = declaration
    #     return dec_elem

    @staticmethod
    def location(location_id: int, pos_x: int, pos_y: int, inv: str = None, 
                 name: str = None, is_committed: bool = False) -> ET.Element:
        """
        Generate a location

        :param int id: the `id` of location
        :param int pos_x,pos_y: the position of location
        :param str inv: theinvariant of location, e.g., `gclk<=10` and `gclk<100`.
        :param str name: the name of location
        :param bool is_committed: determine whether it is committed or not


        >>> <location id="id37" x="-169" y="-59">
        >>>     <name x="90" y="166">pass</name>
        >>>     <label kind="invariant" x="-212" y="-42">gclk&lt;=122</label>
        >>>     <committed/>
        >>> </location>
        """
        location = ET.Element('location', {'id': f'id{location_id}',
                                           'x': str(pos_x),
                                           'y': str(pos_y)})
        # 添加名字
        if name is not None:
            location_name = ET.Element('name', {'x': str(pos_x),
                                                'y': str(pos_y - 20)})
            location_name.text = name
            location.append(location_name)
        # 添加inv
        if inv is not None:
            label = ET.Element('label', {'kind': 'invariant',
                                         'x': str(pos_x),
                                         'y': str(pos_y - 40)})
            label.text = inv
            location.append(label)
        # 添加committed
        if is_committed:
            location.append(ET.Element('committed'))
        return location

    @staticmethod
    def transition(sourceID: int, targetID: int, pos_x: int, pos_y: int, 
                   guard: str = None, sync: str = None, clock_reset: str = None, 
                   nail: bool = False) -> ET.Element:
        """
        :param int sourceID: the id of start
        :param int targetID: the id of end
        :param int post_x,post_y: the position of sign
        :param str guard: the guard of the edge, e.g., `t>=10`, `t>100`
        :param str sync: the signal of synchronisation, e.g., `!` and `?`
        :param str clock_reset: e.g., `t=0`
        :param bool nail: determine whether the edge is curved

        >>> <transition>
        >>>     <source ref="id7"/>
        >>>     <target ref="id6"/>
        >>>     <label kind="guard" x="139" y="90">t&gt;=tERPMin</label>
        >>>     <label kind="synchronisation" x="123" y="90">sync?</label>
        >>>     <label kind="assignment" x="156" y="107">t=0</label>
        >>> </transition>
        """
        transition = ET.Element('transition')
        # 构建并添加source
        source = ET.Element('source', {'ref': f'id{sourceID}'})
        transition.append(source)
        # 构建并添加target
        target = ET.Element('target', {'ref': f'id{targetID}'})
        transition.append(target)
        # 构建并添加guard
        if guard is not None:
            label_guard = ET.Element('label', {'kind': 'guard',
                                               'x': str(pos_x),
                                               'y': str(pos_y)})
            label_guard.text = guard
            transition.append(label_guard)
        # 构建并添加synchronisation
        if sync is not None:
            label_sync = ET.Element('label', {'kind': 'synchronisation',
                                              'x': str(pos_x),
                                              'y': str(pos_y - 30)})
            label_sync.text = sync
            transition.append(label_sync)
        # 构建并添加assignment
        if clock_reset is not None:
            label_assignment = ET.Element('label', {'kind': 'assignment',
                                                    'x': str(pos_x),
                                                    'y': str(pos_y - 60)})
            label_assignment.text = clock_reset
            transition.append(label_assignment)
        # 构建并添加nail (弯曲结点)
        if nail:
            nail_element = ET.Element('nail', {'x': str(pos_x),
                                               'y': str(pos_y)})
            transition.append(nail_element)
        return transition

    @staticmethod
    def template(name: str, locations: List[ET.Element], init_id: int, transitions: List[ET.Element],
                 parameter: str = None, declaration: str = None) -> ET.Element:
        """
        :param str name: the name of template
        :param List[ET.Element] locations: series of locations generated by UFactory.construct_location()
        :param int init_id: the id of initial location
        :param List[ET.Element] transitions: series of transitions generated by UFactory.construct_location()
        :param str parameter: parameter instruction, e.g., <parameter>broadcast chan &amp;actNode, actPath,int tERPMin, int tERPMax</parameter>
        :param str declaration: declaration instruction, e.g., <declaration>clock t;</declaration>

        >>> <template>
        >>>     <name>NodeN</name>
        >>>     <parameter>broadcast chan &amp;actNode, int tERPMin, int tERPMax</parameter>
        >>>     <declaration>clock t;</declaration>
        >>>     <location> </location>
        >>>     <location> </location>
        >>>     <location> </location>
        >>>     <init ref="id47"/>
        >>>     <transition> </transition>
        >>>     <transition> </transition>
        >>>     <transition></transition>
        >>> </template>
        """
        template = ET.Element('template')
        # 创建并加入name
        name_elem = ET.Element('name')
        name_elem.text = name
        template.append(name_elem)

        # 创建并加入parameter
        if parameter is not None:
            parameter_elem = ET.Element('parameter')
            parameter_elem.text = parameter
            template.append(parameter_elem)

        # 创建并加入declaration
        if declaration is not None:
            declaration_elem = ET.Element('declaration')
            declaration_elem.text = declaration
            template.append(declaration_elem)

        # 加入locations
        for location in locations:
            template.append(location)

        # 创建并加入init
        init_elem = ET.Element('init', {'ref': f'id{init_id}'})
        template.append(init_elem)

        # 加入 transitions
        for transition in transitions:
            template.append(transition)
        return template

    @staticmethod
    def input(input_name: str, signals: List[Tuple[str, str, str]], init_id: int) -> ET.Element:
        """
        Generate a linear model of input.

        :param str input_name: the name of input
        :parama List[Tuple[str, int, int]] signals: this data type is updated in `umodel.TymedActions`
        :param int init_id: int, set the minimum `<init ref='xxx'/>` of monitor
        """
        # 创建locations
        locations = []
        for i in range(len(signals)):
            # [signal, guard, inv, name]
            location = UFactory.location(init_id + i, 300 * i, 200, signals[i][2])
            locations.append(location)
        # 需要多一个尾巴location
        location = UFactory.location(init_id + len(signals), 300 * len(signals), 200, name='pass')
        locations.append(location)
        # 创建transitions
        transitions = []
        for i in range(len(signals)):
            # [signal, guard, inv]
            transition = UFactory.transition(init_id + i, init_id + i + 1, i * 300 + 100, 200,
                                                  signals[i][1], signals[i][0]+'!')
            transitions.append(transition)
        # 获得clock name并创建declaration
        clk_name = signals[0][1].split('>')[0]
        declaration = f'clock {clk_name};'
        monitor_elem = UFactory.template(input_name, locations, init_id, transitions,declaration=declaration)
        return monitor_elem

    @staticmethod
    def monitor(monitor_name: str, signals: List[Tuple[str, str, str]], observe_action: List[str], 
                init_id: int, strict: bool = False, allpattern: bool=False) -> ET.Element:
        """
        Generate a new linear model of.

        :param str monitor_name: the name of monitor
        :param List[Tuple[str, int, int]] signals: this data type is updated in `umodel.TimedActions`
        :param int init_id: set the minimum `<init ref='xxx'/>` of monitor
        :param bool strict: determine whethe the observation is strict, which indicates other observations will be forbidden

        >>> <template>
        >>>     <name>Monitor</name>
        >>>     <location> </location>
        >>>     <location>init ref="id47"/>
        >>>     <transition> </transition>
        >>> </template>
        """
        # 创建locations
        locations = []
        for i in range(len(signals)):
            # [signal, guard, inv]
            inv = None if allpattern else signals[i][2]
            location = UFactory.location(init_id + i, 300 * i, 200, inv=inv)
            locations.append(location)
        # 需要多一个尾巴location
        location = UFactory.location(init_id + len(signals), 300 * len(signals), 200, name='pass')
        locations.append(location)

        # 创建transitions
        transitions = []
        for i in range(len(signals)):
            # [signal, guard, inv]
            guard = None if allpattern else signals[i][1]
            transition = UFactory.transition(init_id + i, init_id + i + 1, i * 300 + 100, 200,
                                                  guard=guard, sync=signals[i][0]+'?')
            transitions.append(transition)

        # 如果是strict，需要给每个location创建fail location，并且构建对应transitions边指向对应的fail location
        if strict:
            pruned_observation_action = list(set(observe_action))

            # 构建指向fail的transitions
            for i in range(len(signals)):
                # 构建一个fail location
                fail_location_id = init_id + len(signals) + i + 1
                # check allpattern
                inv = None if allpattern else signals[i][2].replace('<=', '<')
                location = UFactory.location(fail_location_id, 300 * i, -200, inv=inv,
                                                  name='fail' + str(i))
                locations.append(location)
                actions_length = 200 // len(pruned_observation_action)
                # 需要对每一个observe action指向fail transitions
                for j in range(len(pruned_observation_action)):
                    # 指向fail，注意guard是大于
                    guard = None if allpattern else signals[i - 1][1].replace('>=', '>')
                    if allpattern and (pruned_observation_action[j] == signals[i][0]):
                        continue
                    if i == 0:
                        transition = UFactory.transition(init_id + i, fail_location_id, i * 300 + (j-len(pruned_observation_action)//2) * actions_length, -100,
                                                         guard=None, sync=pruned_observation_action[j]+'?',nail=True)
                    else:
                        transition = UFactory.transition(init_id + i, fail_location_id, i * 300 + (j-len(pruned_observation_action)//2) * actions_length, -100,
                                                         guard=guard, sync=pruned_observation_action[j]+'?',nail=True)

                    transitions.append(transition)
        # 获得clock name并创建declaration
        clk_name = signals[0][1].split('>')[0]
        declaration = None if allpattern else f'clock {clk_name};'
        monitor_elem = UFactory.template(monitor_name, locations, init_id, transitions, declaration=declaration)
        return monitor_elem
