"""author: Yining She
"""
from __future__ import annotations
import re
from typing import List, Dict

# region mermaid class

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
            List[List[str]]: List of `[source, edge_name, target]`.
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
            str: raw mermaid string.
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

        elif target_file.endswith('.svg') or target_file.endswith('.jpg') or target_file.endswith('.png'):
            # 这里使用mermaid.ink 的API，需要联网
            import base64
            import requests

            graph_bytes = self.mermaid_str.replace("```","").replace("mermaid","graph").encode("utf8")
            base64_bytes = base64.b64encode(graph_bytes)
            base64_string = base64_bytes.decode("ascii")

            if target_file.endswith('.svg'):
                respose = requests.get(f"https://mermaid.ink/svg/{base64_string}")
            else:
                respose = requests.get(f"https://mermaid.ink/img/{base64_string}?type={target_file[-3:]}")

            if respose.status_code == 200:
                with open(target_file, "wb") as f:
                    f.write(respose.content)
            else:
                raise Exception("Failed to retrieve graph from mermaid.ink. Save image functions require internet connection.")

        elif target_file.endswith('.pdf'):
            raise NotImplementedError("pdf function not implemented. Please generate svg and convert manually.")

        else:
            raise ValueError(f'Invalid target_file: {target_file}. Only support `.svg`, `.jpg`, `.png` and `.md`.')
        return target_file
# endregion

# region ==== build CG by author: Yining She ====


def get_str_before(string: str, label: str):
    """
    :return: the substring of 'string' before the first occurrence of 'label'.

    If 'label' doesn't exist in 'string', raise error.
    """
    index = string.find(label)
    assert (index != -1)
    return string[:index]


def get_str_after(string, label):
    """
    :return: the substring of 'string' after the first occurence of 'label'.

    If 'label' doesn't exist in 'string', raise error.
    """
    index = string.find(label)
    assert (index != -1)
    return string[index + len(label):]


class Node:
    """
    A instance of a Xml Template.

    :param strname: the name of the instance
    :param str temp_name: the name of the template
    :param list sig_in: a list of names of signals enter the node
    :param list sig_out: a list of names of signals sent by the node
    """

    def __init__(self, name, temp_name, sig_in, sig_out):
        self.name = name
        self.temp_name = temp_name
        self.sig_in = sig_in
        self.sig_out = sig_out


class XmlTemplate:
    """
    Used to define a template in the xml.
    Input is the corresponding code in the xml.
    :param str name: name of the template
    :param list sig_in: a list of signals enter the template
    :param list sig_out: a list of signals sent by the template
    :param dict params: relate input signal variable with its index in the input arguments
    """

    def __init__(self, code):
        self.name = None
        self.signal_in = None
        self.signal_out = None
        self.paras = None
        self.code = code
        self.init_name()
        self.get_all_sync()
        self.get_param()

    def init_name(self):
        """
        Get the name from self.code
        """
        paragraphs = self.code.split('</name>')
        line = paragraphs[0]
        self.name = get_str_after(line, '>')
        # name_start_i = line.index('>')
        # self.name = line[name_start_i+1:]

    def get_all_sync(self):
        """
        Using label "synchronisation" to find all signal names used in the template.
        """
        lines = [i for i in re.findall(r'<label[^<]+</label>', self.code) if "<label kind=\"synchronisation\"" in i]
        self.signal_in = []
        self.signal_out = []
        for line in lines:
            sub = get_str_after(line, '>')
            sub = get_str_before(sub, '</label>')
            if sub[-1] == '?':
                if sub[:-1] not in self.signal_in:
                    self.signal_in.append(sub[:-1])
            else:
                if sub[:-1] not in self.signal_out:
                    self.signal_out.append(sub[:-1])

    def get_param(self):
        """
        Find the signal variables that come in through input.

        And store the name of them with their index in the input arguments, which can be used to find the actual signal variable when give input argument.
        """
        self.paras = {}
        if self.code.find("</parameter>") != -1:
            para_code = get_str_before(self.code, "</parameter>")
            para_code = get_str_after(para_code, "<parameter>")
            para_code = para_code.split(',')
            for i, para_code_i in enumerate(para_code):
                if 'broadcast chan' in para_code_i:
                    signal_name = get_str_after(para_code_i, 'broadcast chan &amp;')
                    self.paras[signal_name] = i

    def get_instance(self, name, para_string):
        """
        Return and initialize an instance of the template using the input argument.

        :param str name: name of the new instance
        :param str para_string: code of the input argument
        """
        sig_in = []
        sig_out = []
        paras = para_string.split(',')
        for i in self.signal_in:
            if i in self.paras.keys():
                sig_in.append(paras[self.paras[i]].strip())
            else:
                sig_in.append(i)
        for i in self.signal_out:
            if i in self.paras.keys():
                sig_out.append(paras[self.paras[i]].strip())
            else:
                sig_out.append(i)
        return Node(name, self.name, sig_in, sig_out)


class XmlReader:
    """
    Used to read the xml file and take advantage of classes defined above.
    """

    def __init__(self, filename):
        """
        Read the file and init all templates in it.
        """
        self.templates = None
        self.nodes = None
        self.filename = filename
        self.code = None
        with open(filename, 'rt', encoding='utf-8') as f:
            self.code = f.read()
        self.init_template()

    def init_template(self):
        """
        Find all templates in the code and init a 'XmlTemplate' for each of them.
        """
        self.templates = {}
        paragraphs = self.code.split('<template>')
        if len(paragraphs) == 1:
            # print("  No template in file.")
            return
        paragraphs[-1] = get_str_before(paragraphs[-1], '</template>')
        # paragraphs[-1] = paragraphs[-1][:paragraphs[-1].index('</template>')]
        paragraphs = paragraphs[1:]
        for para in paragraphs:
            temp = XmlTemplate(para)
            temp_name = temp.name
            self.templates[temp_name] = temp

    def get_notes(self):
        """
        By reading the 'system' part in the xml to init all time-automata instances.
        :return: a list fo 'Node'.
        """
        self.nodes = {}
        system_code = get_str_after(self.code, '<system>')
        system_code = get_str_before(system_code, '</system>')
        lines = system_code.split('\n')
        for line in lines:
            if line[:7] == 'system ':
                variables = get_str_before(line[7:], ';').split(',')
                for var_name in variables:
                    var_name = var_name.strip()
                    assert (len(var_name) > 0)

                    if var_name in self.templates.keys():
                        self.nodes[var_name] = self.templates[var_name].get_instance(var_name, '')
                    else:
                        l = ''
                        for lines_i in lines:
                            if lines_i[:len(var_name)] == var_name:
                                l = get_str_after(lines_i, '=')
                                break
                        assert (l != '')
                        temp_name = get_str_before(l, '(').strip()
                        para_string = get_str_before(l, ')')
                        para_string = get_str_after(para_string, '(')
                        self.nodes[var_name] = self.templates[temp_name].get_instance(var_name, para_string)
        return self.nodes


def add_edge(a, b, label=''):
    code = a + '--' + label + '-->' + b
    return code


def build_cg_code(nodes):
    """
    Given a list of 'Node', build the CG graph and print the markdown code.
    """
    codes = ['graph TD']
    node_names = list(nodes.keys())
    codes = codes + node_names

    n = len(node_names)
    for i in range(n):
        for j in range(i + 1, n):
            if i == j:
                continue
            node1 = nodes[node_names[i]]
            node2 = nodes[node_names[j]]
            for signal in node1.sig_out:
                if signal in node2.sig_in:
                    codes.append(add_edge(node1.name, node2.name, signal))
            for signal in node2.sig_out:
                if signal in node1.sig_in:
                    codes.append(add_edge(node2.name, node1.name, signal))

    # Merge all lines of code
    code = '\n'.join(codes)
    return code


def build_cg(filename):
    reader = XmlReader(filename)
    nodes = reader.get_notes()
    code = build_cg_code(nodes)
    mermaid = f'```mermaid\n{code}```'
    return mermaid
# endregion
