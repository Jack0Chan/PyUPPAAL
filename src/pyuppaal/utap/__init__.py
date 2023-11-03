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

def utap_parser(if_str: str, xtr_file: str) -> str:
    # ... (the previous setup code remains the same)

    # Write the .if content to a temporary file to be used by tracer.out
    # temp_if_file_path = 'temp_if_file.if'
    # with open(temp_if_file_path, 'w') as temp_if_file:
    #     temp_if_file.write(if_str)

    # Prepare the command for executing tracer.out
    # use -s if pass if_str, use -i if pass the if file

    cmd = (
        ["./tracer.exe", "--trace=string", "-t", xtr_file, "-s", if_str] \
        if platform.system() == "Windows" else ["./tracer", "--trace=string", "-t", xtr_file, "-s", if_str]
    )

    try:
        cmd_res = subprocess.get(cmd, capture_output=True, text=True)

        if cmd_res.stderr:
            # cmd里面的if_str有点长了，后面考虑修复。
            raise ValueError(
                f"Hint: Command error with {' '.join(cmd)}:\n {cmd_res.stderr} \n \
            Check [reference](https://github.com/UPPAALModelChecker/utap)"
            )
        return cmd_res.stdout

    except:
        raise ValueError(
            f"Hint: Command error with {' '.join(cmd)}:\n  \
            Check [reference](https://github.com/UPPAALModelChecker/utap)"
        )

    finally:
        # Delete the temporary .if file after successful execution
        # os.remove(temp_if_file_path)
        pass
