# author: Yining She

import re

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
            for i in range(len(para_code)):
                if 'broadcast chan' in para_code[i]:
                    signal_name = get_str_after(para_code[i], 'broadcast chan &amp;')
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
        # print("Open file:", filename)
        f = open(filename,'rt',encoding='utf-8')
        self.code = f.read()

        # print("Initiate all templates:")
        self.init_template()
        # print("Finish Init Templates.")

        # self.get_notes()

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
            # print("  Add template: ", temp_name)
            # print("    signal in : ", temp.signal_in)
            # print("    signal out: ", temp.signal_out)
            # print("    all paras : ", list(temp.paras.keys()))

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
                        for i in range(len(lines)):
                            if lines[i][:len(var_name)] == var_name:
                                l = get_str_after(lines[i], '=')
                                break
                        assert (l != '')
                        temp_name = get_str_before(l, '(').strip()
                        para_string = get_str_before(l, ')')
                        para_string = get_str_after(para_string, '(')
                        self.nodes[var_name] = self.templates[temp_name].get_instance(var_name, para_string)
                    # print('  Add Node: ', var_name, ' --- template: ', self.nodes[var_name].temp_name)
                    # print('    in:', self.nodes[var_name].sig_in, '  out:', self.nodes[var_name].sig_out)
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
    mermaid = """```mermaid\n{}```""".format(code)
    return mermaid
