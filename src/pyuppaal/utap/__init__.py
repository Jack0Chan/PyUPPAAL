import platform
import subprocess
import sys
import os

# def utap_parser(if_str: str, xtr_file: str) -> str:
#     """接口函数来展示utap_parser的用法。

#     Args:
#         if_str (str): uppaal编译出来的if文件的内容
#         xtr_file (str): `.xtr`路径文件

#     Returns:
#         str: 返回解析好的raw trace
#     """
#     raise NotImplemented


def utap_parser(if_file: str, xtr_file: str) -> str:
#     """接口函数来展示utap_parser的用法。

#     Args:
#         if_file (str): uppaal编译出来的if文件
#         xtr_file (str): `.xtr`路径文件

#     Returns:
#         str: 返回解析好的raw trace
#     """
#     raise NotImplemented

    # use absolute path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # os.path.join(current_dir, 'tracer.exe')

    cmd = [os.path.join(current_dir, 'tracer.exe'), "--trace=string", "-t", xtr_file, "-i", if_file] \
    if platform.system() == "Windows" else [os.path.join(current_dir, 'tracer_linux'), "--trace=string", "-t", xtr_file, "-i", if_file]
    # print(cmd)

    __is_windows: bool = platform.system() == 'Windows'
    __is_linux: bool = platform.system() == 'Linux'
    __is_macos: bool = platform.system() == 'Darwin'
    
    try:
        cmd_res = subprocess.run(cmd, capture_output=True, shell=__is_windows, text=True) 
            
        if cmd_res.stderr:
            raise ValueError(f"Command error with: {''.join(cmd)}:\n {cmd_res.stderr} ")
        return cmd_res.stdout
    
    except:
        raise ValueError(f"Command error with: {''.join(cmd)}")

    finally:
        # Delete the temporary .if file after successful execution
        # os.remove(temp_if_file_path)
        pass