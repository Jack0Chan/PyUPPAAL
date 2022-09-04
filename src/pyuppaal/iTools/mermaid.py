from typing import List,Dict

class Mermaid:
    def cg_mermaid_to_list(self, mermaid_str: str) -> List[List[str]]:
        """
        Transform `mermaid` into `List[source, edge_name, target]`

        # FROM:
        # ```mermaid
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
        #  ```
        """

        # 去掉开头和结尾的冗余
        mermaid_list = mermaid_str.replace('```', '').split('\n')
        res = []
        for i in mermaid_list:
            if '--' in i:
                # i TrafficLights--cYellow-->Cars 变成 [TrafficLights, cYellow, Cars]
                res.append(i.replace('>', '').split('--'))

        return res

    def merge_edges(self, mermaid_list: List[List[str]]) -> Dict:
        """
        Transform `List[source, edge_name, target]` into `dict`

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

    def dict_to_mermaid(self, edges_dict: Dict, join_str: str = ',') -> str:
        """
        Transform `dict` into `mermaid`

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

    def merge_mermaid(self,mermaid_str: str) -> str:
        mermaid_list = self.cg_mermaid_to_list(mermaid_str)
        edges_dict = self.merge_edges(mermaid_list)
        res = self.dict_to_mermaid(edges_dict)
        return res

    def filter_mermaid(self, mermaid_str: str, excluded_component: List[str]) -> str:
        res = ''
        for i in mermaid_str.split('\n'):
            for j in excluded_component:
                if j not in i:
                    res += f'{i}\n'
        return res
