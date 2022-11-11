import platform
import sys
import os

# FILE_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(FILE_ROOT_DIR.join('utap_39.pyd'))
# sys.path.append(FILE_ROOT_DIR.join('utap_39.lib'))
python_version = platform.python_version()

utap_parser = None

if '3.6' in python_version:
    from .utap_36 import parse
elif '3.7' in python_version:
    from .utap_37 import parse
elif '3.8' in python_version:
    from .utap_38 import parse
elif '3.9' in python_version:
    from .utap_39 import parse
elif '3.10' in python_version:
    from .utap_310 import parse
else:
    raise ValueError(f'Only support python 3.6-3.10, current version: {python_version}.')

utap_parser = parse


# def utap_parser(if_str: str, xtr_file: str) -> str:
#     """接口函数来展示utap_parser的用法。

#     Args:
#         if_str (str): uppaal编译出来的if文件的内容
#         xtr_file (str): `.xtr`路径文件

#     Returns:
#         str: 返回解析好的raw trace
#     """
#     raise NotImplemented