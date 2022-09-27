"""mermaid
"""
# support for str | List[str]
from __future__ import annotations
from typing import List,Dict


class Mermaid:
    """class Mermaid
    """
    def __init__(self, mermaid_str: str):
        self.__mermaid_str: str = mermaid_str
        # List of `[source, edge_name, target]`
        self.__mermaid_list: List[List[str]] = None

    def __str__(self) -> str:
        return self.__mermaid_str
    
    def __repr__(self) -> str:
        return self.__str__()

    @property
    def mermaid_str(self) -> str:
        """Raw mermaid string.

        Returns:
            str: raw mermaid string.
        """
        return self.__mermaid_str

    @property
    def mermaid_list(self) -> List[List[str]]:
        """List of `[source, edge_name, target]`

        Returns:
            List[List[str]]: _description_
        """
        if self.__mermaid_list is None:
            self.__mermaid_to_list()
        return self.__mermaid_list

    def __mermaid_to_list(self) -> List[List[str]]:
        """Transform `mermaid` into List of `[source, edge_name, target]`.

        FROM:
        ```mermaid
        graph TD
        TrafficLights--cGreen-->Cars
        TrafficLights--cYellow-->Cars
        LV1Pedestrian2--pCrss-->Cars```

        TO:
        [[TrafficLights, cGreen, Cars],
         [TrafficLights, cYellow, Cars],
         [LV1Pedestrian2, pCrss, Cars]]

        Returns:
            List[List[str]]: List of `[source, edge_name, target]`.
        """

        # 去掉开头和结尾的冗余
        mermaid_list = self.mermaid_str.replace('```', '').split('\n')
        # i TrafficLights--cYellow-->Cars 变成 [TrafficLights, cYellow, Cars]
        res = [i.replace('>', '').split('--') for i in mermaid_list if '--' in i]
        self.__mermaid_list = res
        return res

    def __list_to_mermaid(self) -> str:
        """Convert `self.__mermaid_list` to `self.__mermaid_str`.

        Returns:
            str: _description_
        """

        tmp = ''
        for source, edge, target in self.__mermaid_list:
            tmp += source + '--' + edge + '-->' + target + '\n'
        return f"```mermaid\ngraph TD\n{tmp}```"

    def beautify(self, join_str: str = ',') -> str:
        """Beautify Mermaid by merging edges with the same source and target.

        FROM:
        ```mermaid
        graph TD
        TrafficLights--cGreen-->Cars
        TrafficLights--cYellow-->Cars
        LV1Pedestrian2--pCrss-->Cars
        ```

        TO:
        ```mermaid
        graph TD
        TrafficLights--cGreen,cYellow-->Cars
        LV1Pedestrian2--pCrss-->Cars
        ```

        Args:
            join_str (str, optional): join flag. Defaults to ','.

        Returns:
            str: beautified mermaid string.
        """

        # ==== STEP1 构造合并后的边的字典 ====
        # FROM:
        # [['TrafficLights', 'cGreen', 'Cars'],
        #  ['TrafficLights', 'cYellow', 'Cars'],
        #  ['LV1Pedestrian2', 'pCrss', 'Cars']]
        # TO:
        # {"['TrafficLights', 'Cars']": ['cGreen', 'cYellow'],
        #  "['LV1Pedestrian2', 'Cars']": ['pCrss']}
        edges_dict: Dict[str, List[str]] = {}
        for i in self.mermaid_list:
            key = str([i[0], i[2]])
            value = i[1]
            if key in edges_dict:
                edges_dict[key].append(value)
            else:
                edges_dict[key] = [value]
        # remove duplicate
        for key in edges_dict:
            edges_dict[key] = sorted(list(set(edges_dict[key])))

        # ==== STEP2 从字典构造出 mermaid_str ====
        edges_str = ''
        for key, val in edges_dict.items():
            # str转list获取边的两端
            [source, target] = eval(key)
            edge_name = join_str.join(val)
            edges_str += f"{source}--{edge_name}-->{target}\n"
        res = f'''```mermaid\ngraph TD\n{edges_str}```'''
        self.__mermaid_str = res
        return res

    def remove(self, components: str | List[str]) -> str:
        """Remove mermaid lines that contains components.

        Args:
            excluded_components (str | List[str]): components to remove.

        Returns:
            str: mermaid string.
        """
        if isinstance(components, str):
            components = [components]
        for l in self.mermaid_list:
            if set(l) & set(components):
                self.__mermaid_list.remove(l)
        self.__mermaid_str = self.__list_to_mermaid()
        return self.mermaid_str

    def export(self, target_file: str) -> str:
        """Export mermaid to a `<.md | .svg | .pdf | .png>` file.

        Args:
            target_file (str): `<.md | .svg | .pdf | .png>`.

        Returns:
            str: path to the target file.
        """
        if target_file.endswith('.md'):
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(self.mermaid_str)
        elif target_file.endswith('.svg'):
            # 实现后别忘了去tests/test_mermaid.py里修改63行的测试 ['mermaid_test.md', 'mermaid_test.svg', 'mermaid_test.png']
            raise NotImplementedError
        elif target_file.endswith('.pdf'):
            # 实现后别忘了去tests/test_mermaid.py里修改63行的测试 ['mermaid_test.md', 'mermaid_test.svg', 'mermaid_test.png']
            raise NotImplementedError
        elif target_file.endswith('.png'):
            # 实现后别忘了去tests/test_mermaid.py里修改63行的测试 ['mermaid_test.md', 'mermaid_test.svg', 'mermaid_test.png']
            raise NotImplementedError
        else:
            raise ValueError(f'Invalid target_file: {target_file}.')
        return target_file
