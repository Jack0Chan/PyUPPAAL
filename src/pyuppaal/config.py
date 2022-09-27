import os
import platform

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
# TRACER_CUSTOM_WINDOWS = os.path.join(ROOT_DIR, 'trace_custom.exe')
# TRACER_CUSTOM_LINUX = os.path.join(ROOT_DIR, 'trace_custom')
TRACER_CUSTOM_PATH = os.path.join(ROOT_DIR, 'tracer_custom.exe') if platform.system() == 'Windows' \
    else os.path.join(ROOT_DIR, 'tracer_custom')
