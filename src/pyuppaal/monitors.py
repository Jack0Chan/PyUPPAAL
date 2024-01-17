from typing import List, Tuple

from .nta import Template, Location, Edge


class Monitors:
    @staticmethod
    def fault_monitor(name: str, fault_name: str, init_ref: int) -> Template:
        """_summary_

        Args:
            name (str): the name of the returned `Template`.
            fault_name (str): the name of the fault.
            init_ref (int): the initial location id of the returned `Template`. You can set `init_ref` by `UModel.max_location_id + 1`.

        Returns:
            Template: _description_
        """
        init_location = Location(location_id=init_ref, location_pos=(0, 0))
        pass_location = Location(location_id=init_ref+1, location_pos=(200, 0), name='pass')

        fault_edge = Edge(source_location_id=init_location.location_id, target_location_id=pass_location.location_id,
                          source_location_pos=init_location.location_pos, target_location_pos=pass_location.location_pos,
                          sync=f'{fault_name}?', sync_pos=(init_location.location_pos[0]+20, init_location.location_pos[1]-20))

        res = Template(name=name,
                       locations=[init_location, pass_location],
                       init_ref=init_ref,
                       edges=[fault_edge])
        return res

    @staticmethod
    def observer_suffix_monitor(name: str, suffix_sequence: List[str], sigma_o: List[str], sigma_un: List[str], init_ref: int) -> Template:
        """ observer suffix monitor
        Creates an observer suffix monitor template.

        Args:
            name (str): The name of the returned `Template`.
            suffix_sequence (List[str]): The sequence of suffix events to be observed. These events will be monitored in sequence.
            sigma_o (List[str]): The set of observable events. This includes all events that the monitor could potentially observe.
            init_ref (int): the initial location id of the returned `Template`. You can set `init_ref` by `UModel.max_location_id + 1`.

        Returns:
            Template: The constructed monitor template. 
                This template contains a series of locations and transitions that describe how to transition states based on the given suffix sequence and the set of observable events.

        """
        # ==============================
        # 构造 locations
        # locations分为2部分，
        # 1. suffix locations，包含一个pass
        # 2. fail locations
        suffix_locations: List[Location] = []
        fail_locations: List[Location] = []

        # 实现location id的自增
        current_location_id = init_ref
        init_location = Location(location_id=current_location_id, location_pos=(0, 0), is_initial=True)
        current_location_id += 1
        suffix_locations.append(init_location)

        # 构造suffix序列，以及fail location
        suffix_length = len(suffix_sequence)
        for i in range(suffix_length):
            # 添加suffix locations
            suffix_location = Location(location_id=current_location_id, location_pos=(150*(i+1), 0), name=f'suffix_{i+1}')
            current_location_id += 1
            suffix_locations.append(suffix_location)
            # 添加fail locations
            if i < suffix_length-1:
                fail_location = Location(location_id=current_location_id, location_pos=(150*(i+1), 100), name=f'fail_{i+1}', name_pos=(150*(i+1)-15, 110))
                current_location_id += 1
                fail_locations.append(fail_location)

        # 构造suffix序列最后一个location
        suffix_locations[-1].name = 'pass'

        # ==============================
        # 构造edges
        edges: List[Edge] = []
        # 构造初始location的吸收边，需要吸收所有的event
        # all_events = sigma_o + sigma_un
        for i, event in enumerate(sigma_o):
            absorb_edge = Edge(source_location_id=init_ref, target_location_id=init_ref,
                               source_location_pos=init_location.location_pos, target_location_pos=init_location.location_pos,
                               sync=f'{event}?',  sync_pos=(init_location.location_pos[0]-20, init_location.location_pos[1]+20*(i+1)))
            edges.append(absorb_edge)

        # 添加suffix edges 以及 fail edges
        for i, event in enumerate(suffix_sequence):
            # suffix edge
            source_location = suffix_locations[i]
            target_location = suffix_locations[i+1]
            suffix_edge = Edge(source_location_id=source_location.location_id, target_location_id=target_location.location_id,
                               source_location_pos=source_location.location_pos, target_location_pos=target_location.location_pos,
                               sync=f'{event}?', sync_pos=(source_location.location_pos[0]+30, source_location.location_pos[1]-20))
            edges.append(suffix_edge)

            # fail edges
            # 对应的是pass location，需要fail所有的观测
            if i == suffix_length-1:
                continue
                # for j, fail_event in enumerate(sigma_o):
                #     fail_location = fail_locations[i]
                #     fail_edge = Edge(source_location_id=target_location.location_id, target_location_id=fail_location.location_id,
                #                     source_location_pos=target_location.location_pos, target_location_pos=fail_location.location_pos,
                #                     sync = f'{fail_event}?', sync_pos=(source_location.location_pos[0]+30, source_location.location_pos[1]+20*(j+1)))
                #     edges.append(fail_edge)
            else:
                # 需要添加fail
                for j, fail_event in enumerate(sigma_o):
                    fail_location = fail_locations[i]
                    if fail_event != suffix_sequence[i+1]:
                        fail_edge = Edge(source_location_id=target_location.location_id, target_location_id=fail_location.location_id,
                                         source_location_pos=target_location.location_pos, target_location_pos=fail_location.location_pos,
                                         sync=f'{fail_event}?', sync_pos=(fail_location.location_pos[0]+30, source_location.location_pos[1]+20*(j+1)))
                        edges.append(fail_edge)

        # 合并
        observer_suffix_template = Template(name=name,
                                            locations=suffix_locations+fail_locations,
                                            init_ref=init_ref,
                                            edges=edges)

        return observer_suffix_template

    @staticmethod
    def obs_after_fault_monitor(name: str, suffix_sequence: List[str], sigma_o: List[str], sigma_un: List[str], fault: str, init_ref: int) -> Template:
        """ obs_after_fault_monitor

        Args:
            name (str): the name of returend `Template`.
            suffix_sequence (List[str]): suffix sequence.
            sigma_o (List[str]): the set of observable events.
            sigma_un (List[str]): the set of unobservable events.
            fault (str): fault name.
            init_ref (int): the initial location id of the returned `Template`. You can set `init_ref` by `UModel.max_location_id + 1`.

        Returns:
            Template: monitor template
        """
        # ==============================
        # 构造 locations
        # locations分为2部分,
        # 1. suffix locations，包含一个pass
        # 2. fail locations
        suffix_locations: List[Location] = []
        fail_locations: List[Location] = []

        # 实现location id的自增
        current_location_id = init_ref

        init_location = Location(location_id=current_location_id, location_pos=(0, 0), is_initial=True)
        current_location_id += 1
        suffix_locations.append(init_location)

        # fault location
        fault_location = Location(location_id=current_location_id, location_pos=(200, 0))
        current_location_id += 1
        suffix_locations.append(fault_location)

        # 构造suffix序列，以及fail location
        suffix_length = len(suffix_sequence)
        for i in range(suffix_length):
            # 添加suffix locations
            suffix_location = Location(location_id=current_location_id, location_pos=(200*(i+2), 0), name=f'suffix_{i+1}')
            current_location_id += 1
            suffix_locations.append(suffix_location)
            # 添加fail locations
            fail_location = Location(location_id=current_location_id, location_pos=(200*(i+1), 100), name=f'fail_{i+1}', name_pos=(200*(i+1)-15, 110))
            current_location_id += 1
            fail_locations.append(fail_location)

        suffix_locations[-1].name = 'pass'

        # ==============================
        # 构造edges
        edges: List[Edge] = []
        # 构造初始location的吸收边，需要吸收所有的event
        all_events = sigma_o + sigma_un
        for i, event in enumerate(all_events):
            absorb_edge = Edge(source_location_id=init_ref, target_location_id=init_ref,
                               source_location_pos=init_location.location_pos, target_location_pos=init_location.location_pos,
                               sync=f'{event}?',  sync_pos=(init_location.location_pos[0]-20, init_location.location_pos[1]+20*(i+1)))
            edges.append(absorb_edge)

        # 添加fault edge
        fault_edge = Edge(source_location_id=init_location.location_id, target_location_id=fault_location.location_id,
                          source_location_pos=init_location.location_pos, target_location_pos=fault_location.location_pos,
                          sync=f'{fault}?', sync_pos=(init_location.location_pos[0]+30, init_location.location_pos[1]-20))
        edges.append(fault_edge)

        # 添加suffix edges 以及 fail edges

        for i, event in enumerate(suffix_sequence):
            # suffix edge
            source_location = suffix_locations[i+1]
            target_location = suffix_locations[i+2]
            suffix_edge = Edge(source_location_id=source_location.location_id, target_location_id=target_location.location_id,
                               source_location_pos=source_location.location_pos, target_location_pos=target_location.location_pos,
                               sync=f'{event}?', sync_pos=(source_location.location_pos[0]+30, source_location.location_pos[1]-20*(i+1)))
            edges.append(suffix_edge)

            # fail edges
            # 对应的是pass location，不需要fail
            # print(suffix_length, suffix_sequence)
            if i == suffix_length:
                break

            # 需要添加fail
            # prev_location = suffix_locations[i]
            for j, fail_event in enumerate(sigma_o):
                fail_location = fail_locations[i]
                if fail_event != suffix_sequence[i]:
                    fail_edge = Edge(source_location_id=source_location.location_id, target_location_id=fail_location.location_id,
                                     source_location_pos=source_location.location_pos, target_location_pos=fail_location.location_pos,
                                     sync=f'{fail_event}?', sync_pos=(fail_location.location_pos[0]+30, source_location.location_pos[1]+20*(j+1)))
                    edges.append(fail_edge)

        # 合并
        res = Template(name=name,
                       locations=suffix_locations+fail_locations,
                       init_ref=init_ref,
                       edges=edges)

        return res

    @staticmethod
    def input_after_fault_monitor(
            name: str,
            identified_faults: List[str],
            protecting_events: List[str],
            sigma_fault: List[str],
            sigma_control: List[str],
            control_length: int,
            init_ref: int) -> Template:
        """ input_after_fault_monitor

        Args:
            name (str): the name of returend `Template`.
            identified_faults (List[str]): identified faults.
            protecting_events (List[str]): sequence of evnets that should be immediately applied after the faults are identified.
            sigma_control (List[str]): the set of control events.
            control_length (int): the longest control limits.
            init_ref (int): the initial location id of the returned `Template`. You can set `init_ref` by `UModel.max_location_id + 1`.

        Returns:
            Template: monitor template
        """
        locations = []
        num_identified_faults = len(identified_faults)

        current_location_id = init_ref
        current_location_pos = (0, 0)
        init_location = Location(location_id=current_location_id, location_pos=(0, 0))
        current_location_id += 1
        current_location_pos = (current_location_pos[0] + 250, 0)
        locations.append(init_location)

        # faults locations
        for _ in range(len(identified_faults)):
            fault_location = Location(location_id=current_location_id, location_pos=current_location_pos)
            current_location_id += 1
            current_location_pos = (current_location_pos[0] + 250, 0)
            locations.append(fault_location)
        # fault 后立刻执行应急保护
        locations[-1].is_committed = True

        # protecting locations
        for _ in range(len(protecting_events)):
            protect_location = Location(location_id=current_location_id, location_pos=current_location_pos, is_committed=True)
            current_location_id += 1
            current_location_pos = (current_location_pos[0] + 250, 0)
            locations.append(protect_location)
        locations[-1].is_committed = False

        # control locations
        for i in range(control_length):
            control_location = Location(location_id=current_location_id, location_pos=current_location_pos, name=f"control_{i+1}")
            current_location_id += 1
            current_location_pos = (current_location_pos[0] + 250, 0)
            locations.append(control_location)
        locations[-1].name = 'pass'

        # fail locations
        fail_locations = []
        len_identified_faults = len(identified_faults)
        len_all_faults = len(sigma_fault)
        if len_identified_faults != len_all_faults:
            for i, l in enumerate(locations):
                location_pos = (l.location_pos[0], 200)
                name_pos = (l.location_pos[0]-15, 215)
                fail_location = Location(location_id=current_location_id, location_pos=location_pos, name=f"fail_{i}", name_pos=name_pos)
                current_location_id += 1
                fail_locations.append(fail_location)

        # edges
        edges = []

        # controls before faults are identified
        for loc in [locations[0]] + locations[1:num_identified_faults]:
            for i, c in enumerate(sigma_control):
                control_edge = Edge(source_location_id=loc.location_id, source_location_pos=loc.location_pos,
                                    target_location_id=loc.location_id, target_location_pos=loc.location_pos,
                                    sync=f'{c}?', sync_pos=(loc.location_pos[0]-25, loc.location_pos[1]-20*(i+3)))
                edges.append(control_edge)

        for i in range(num_identified_faults):
            source = locations[i]
            target = locations[i+1]
            for index, f in enumerate(identified_faults):
                fault_edge = Edge(source_location_id=source.location_id, source_location_pos=source.location_pos,
                                  target_location_id=target.location_id, target_location_pos=target.location_pos,
                                  sync=f'{f}?', sync_pos=(source.location_pos[0]+25, source.location_pos[1]-20*(index+1)))
                edges.append(fault_edge)

        # protected events
        for i, protect_event in enumerate(protecting_events):
            source = locations[num_identified_faults + i]
            target = locations[num_identified_faults + i + 1]
            protect_edge = Edge(source_location_id=source.location_id, source_location_pos=source.location_pos,
                                target_location_id=target.location_id, target_location_pos=target.location_pos,
                                sync=f'{protect_event}!', sync_pos=(source.location_pos[0]+25, source.location_pos[1]-20))
            edges.append(protect_edge)

        idx = num_identified_faults + len(protecting_events)
        for i in range(control_length):
            source = locations[idx + i]
            target = locations[idx + i + 1]
            # control events
            for j, control_event in enumerate(sigma_control):
                control_edge = Edge(source_location_id=source.location_id, source_location_pos=source.location_pos,
                                    target_location_id=target.location_id, target_location_pos=target.location_pos,
                                    sync=f'{control_event}!', sync_pos=(source.location_pos[0]+50, source.location_pos[1]-20*(j+1)))
                edges.append(control_edge)
            control_edge = Edge(source_location_id=source.location_id, source_location_pos=source.location_pos,
                                target_location_id=target.location_id, target_location_pos=target.location_pos)
            edges.append(control_edge)

        # fail edges
        if len_identified_faults != len_all_faults:
            excluded_faults = set(sigma_fault) - set(identified_faults)
            for i, fl in enumerate(fail_locations):
                source = locations[i]
                target = fl
                for j, f in enumerate(excluded_faults):
                    fail_edge = Edge(source_location_id=source.location_id, source_location_pos=source.location_pos,
                                     target_location_id=target.location_id, target_location_pos=target.location_pos,
                                     sync=f'{f}?', sync_pos=(source.location_pos[0]+20, source.location_pos[1]+20*(j+2)))
                    edges.append(fail_edge)

        res = Template(name=name,
                       locations=locations + fail_locations,
                       init_ref=init_ref,
                       edges=edges)
        return res

    @staticmethod
    def tolerance_checker_monitor(
            name: str,
            identified_faults: List[str],
            protecting_events: List[str],
            sigma_fault: List[str],
            sigma_control: List[str],
            control_sequence: List[str],
            init_ref: int) -> Template:
        """ tolerance_checker_monitor

        Args:
            name (str): the name of returned `Template`.
            identified_faults (List[str]): identified faults.
            protecting_events (List[str]): sequence of evnets that should be immediately applied after the faults are identified.
            sigma_control (List[str]): the set of control events.
            control_length (int): the longest control limits.
            init_ref (int): the initial location id of the returned `Template`. You can set `init_ref` by `UModel.max_location_id + 1`.

        Returns:
            Template: monitor template
        """
        locations = []
        num_identified_faults = len(identified_faults)

        current_location_id = init_ref
        current_location_pos = (0, 0)
        init_location = Location(location_id=current_location_id, location_pos=(0, 0))
        current_location_id += 1
        current_location_pos = (current_location_pos[0] + 250, 0)
        locations.append(init_location)

        # faults locations
        for _ in range(len(identified_faults)):
            fault_location = Location(location_id=current_location_id, location_pos=current_location_pos)
            current_location_id += 1
            current_location_pos = (current_location_pos[0] + 250, 0)
            locations.append(fault_location)
        # fault 后立刻执行应急保护
        locations[-1].is_committed = True

        # protecting locations
        for _ in range(len(protecting_events)):
            protect_location = Location(location_id=current_location_id, location_pos=current_location_pos, is_committed=True)
            current_location_id += 1
            current_location_pos = (current_location_pos[0] + 250, 0)
            locations.append(protect_location)
        locations[-1].is_committed = False

        # control locations
        control_length = len(control_sequence)
        for i in range(control_length):
            control_location = Location(location_id=current_location_id, location_pos=current_location_pos, name=f"control_{i+1}")
            current_location_id += 1
            current_location_pos = (current_location_pos[0] + 250, 0)
            locations.append(control_location)
        locations[-1].name = 'pass'

        # fail locations
        fail_locations = []
        len_identified_faults = len(identified_faults)
        len_all_faults = len(sigma_fault)
        if len_identified_faults != len_all_faults:
            for i, l in enumerate(locations):
                location_pos = (l.location_pos[0], 200)
                name_pos = (l.location_pos[0]-15, 215)
                fail_location = Location(location_id=current_location_id, location_pos=location_pos, name=f"fail_{i}", name_pos=name_pos)
                current_location_id += 1
                fail_locations.append(fail_location)

        # edges
        edges = []
        for i in range(num_identified_faults):
            source = locations[i]
            target = locations[i+1]
            for index, f in enumerate(identified_faults):
                fault_edge = Edge(source_location_id=source.location_id, source_location_pos=source.location_pos,
                                  target_location_id=target.location_id, target_location_pos=target.location_pos,
                                  sync=f'{f}?', sync_pos=(source.location_pos[0]+20, source.location_pos[1] - 20 * (index+1)))
                edges.append(fault_edge)

        for i, protect_event in enumerate(protecting_events):
            source = locations[num_identified_faults + i]
            target = locations[num_identified_faults + i + 1]
            protect_edge = Edge(source_location_id=source.location_id, source_location_pos=source.location_pos,
                                target_location_id=target.location_id, target_location_pos=target.location_pos,
                                sync=f'{protect_event}!', sync_pos=(source.location_pos[0]+20, source.location_pos[1]-20))
            edges.append(protect_edge)

        idx = num_identified_faults + len(protecting_events)
        for i in range(control_length):
            source = locations[idx + i]
            target = locations[idx + i + 1]
            control_event = control_sequence[i]
            control_edge = Edge(source_location_id=source.location_id, source_location_pos=source.location_pos,
                                target_location_id=target.location_id, target_location_pos=target.location_pos,
                                sync=f'{control_event}!', sync_pos=(source.location_pos[0]+20, source.location_pos[1]-20))
            edges.append(control_edge)

        # controls before faults are identified
        for loc in [locations[0]] + locations[1:num_identified_faults]:
            for index, control in enumerate(sigma_control):
                control_edge = Edge(source_location_id=loc.location_id, source_location_pos=loc.location_pos,
                                    target_location_id=loc.location_id, target_location_pos=loc.location_pos,
                                    sync=f'{control}!', sync_pos=(loc.location_pos[0]-20, loc.location_pos[1]-20*(index+3)))
                edges.append(control_edge)

        # fail edges
        if len_identified_faults != len_all_faults:
            excluded_faults = set(sigma_fault) - set(identified_faults)
            for i, fl in enumerate(fail_locations):
                source = locations[i]
                target = fl
                for j, f in enumerate(excluded_faults):
                    fail_edge = Edge(source_location_id=source.location_id, source_location_pos=source.location_pos,
                                     target_location_id=target.location_id, target_location_pos=target.location_pos,
                                     sync=f'{f}?', sync_pos=(source.location_pos[0]+20, source.location_pos[1]+20*(j+1)))
                    edges.append(fail_edge)

        # 合并
        res = Template(name=name,
                       locations=locations + fail_locations,
                       init_ref=init_ref,
                       edges=edges)
        return res

    @staticmethod
    def input_template(name: str, signals: List[str] | List[Tuple[str, str, str]], init_ref: int) -> Template:
        """ input_template

        >>> monitor = Template.construct_input_template(xxx)
        >>> umodel = UModel(xxx)
        >>> umodel.add_template(monitor: Tempalte)
        >>> umodel.add_template_to_system(str: template_name)

        Args:
            name (str): 
            signals (List[str] | List[Tuple[str, str, str]]): input signals, can accept discrete event sequence (List[str]), or timed event sequence (List[Tuple[str, str, str]])
                List[str] xxxx discrete event sequence, example: ['a', 'b', 'c']
                List[Tuple[str, str, str]] xxxx timed event sequence, stands for `List[(action_name, guard, invariant)]`
                    example: `[('a', 't>=10', 't<=10'), ('b', 't>=20', 't<=20'), ('c', 't>=30', 't<=30')]`
                    `[('a', 't1>=10', 't1<=10'), ('b', 't2>=20', 't2<=20'), ('c', 't3>=30', 't3<=30')]` you can use any guard and invariant expression
            init_ref (int): the initial location id of the returned `Template`. You can set `init_ref` by `UModel.max_location_id + 1`.

        Returns:
            Template: monitor template
        """
        if isinstance(signals[0], str):
            signals = [(signal, '', '') for signal in signals]

        # 创建locations
        locations = []
        edges = []
        for i, signal_i in enumerate(signals):
            # [signal, guard, inv, name]
            location_pos = (300 * i, 200)
            location = Location(location_id=init_ref + i, location_pos=location_pos, invariant=signal_i[2])
            locations.append(location)
            # [signal, guard, inv]
            edge = Edge(source_location_id=init_ref + i,
                        target_location_id=init_ref + i + 1,
                        source_location_pos=location_pos,
                        target_location_pos=(location_pos[0]+300, 200),
                        guard=signal_i[1], sync=signal_i[0]+'!')
            edges.append(edge)
        # 需要多一个尾巴location
        location = Location(location_id=init_ref + len(signals), location_pos=(300 * len(signals), 200), name='pass')
        locations.append(location)

        # 获得clock name并创建declaration
        clk_name = signals[0][1].split('>')[0]
        declaration = f'clock {clk_name};'
        input_temp = Template(name=name, locations=locations,
                              init_ref=init_ref, edges=edges, declaration=declaration)
        return input_temp

    @staticmethod
    def observer_template(name: str, signals: List[Tuple[str, str, str]], observe_action: List[str],
                          init_ref: int, strict: bool = False, allpattern: bool = False) -> Template:
        """ observer_template

        >>> monitor = Template.construct_observer_template(xxx)
        >>> umodel = UModel(xxx)
        >>> umodel.add_template(monitor: Tempalte)
        >>> umodel.add_template_to_system(str: template_name)
        <template>
            <name>Monitor</name>
            <location> </location>
            <location>init ref="id47"/>
            <transition> </transition>
        </template>
        """
        # 创建locations
        locations = []
        for i, signal_i in enumerate(signals):
            # [signal, guard, inv]
            inv = None if allpattern else signal_i[2]
            location = Location(location_id=init_ref + i, location_pos=(300 * i, 200), invariant=inv)
            locations.append(location)
        # 需要多一个尾巴location
        location = Location(location_id=init_ref + len(signals), location_pos=(300 * len(signals), 200), name='pass')
        locations.append(location)

        # 创建transitions
        edges = []

        # 构建指向pass的transitions
        for i, signal_i in enumerate(signals):
            # [signal, guard, inv]
            guard = None if allpattern else signal_i[1]
            edge = Edge(source_location_id=init_ref + i, target_location_id=init_ref + i + 1,
                        source_location_pos=(i * 300 + 100, 200),
                        target_location_pos=(i * 300 + 100, 260),
                        guard=guard, sync=signals[i][0]+'?')
            edges.append(edge)

        # 如果是strict，需要给每个location创建fail location，并且构建对应transitions边指向对应的fail location
        if strict:
            pruned_observation_action = list(set(observe_action))

            # 构建指向fail的transitions
            for i, signal_i in enumerate(signals):
                # 构建一个fail location
                fail_location_id = init_ref + len(signals) + i + 1
                # check allpattern
                inv = None if allpattern else signal_i[2].replace('<=', '<')
                location = Location(location_id=fail_location_id, location_pos=(300 * i, -200),
                                    name='fail' + str(i), invariant=inv)
                locations.append(location)
                actions_length = 200 // len(pruned_observation_action)
                # 需要对每一个observe action指向fail transitions
                for j, action_j in enumerate(pruned_observation_action):
                    # 指向fail，注意guard是大于
                    guard = None if allpattern else signals[i - 1][1].replace('>=', '>')
                    if allpattern and (pruned_observation_action[j] == signals[i][0]):
                        continue
                    if i == 0:
                        transition = Edge(source_location_id=init_ref + i, target_location_id=fail_location_id,
                                          source_location_pos=(i * 300 + (j-len(pruned_observation_action)//2) * actions_length, -100),
                                          target_location_pos=(i * 300 + (j-len(pruned_observation_action)//2) * actions_length, -60),
                                          guard=None, sync=action_j+'?', nails=[])
                    else:
                        transition = Edge(source_location_id=init_ref + i, target_location_id=fail_location_id,
                                          source_location_pos=(i * 300 + (j-len(pruned_observation_action)//2) * actions_length, -100),
                                          target_location_pos=(i * 300 + (j-len(pruned_observation_action)//2) * actions_length, -60),
                                          guard=guard, sync=action_j+'?', nails=[])

                    edges.append(transition)
        # 获得clock name并创建declaration
        clk_name = signals[0][1].split('>')[0]
        declaration = None if allpattern else f'clock {clk_name};'
        res = Template(name=name, locations=locations, init_ref=init_ref, edges=edges, declaration=declaration)
        return res
