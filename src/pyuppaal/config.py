import os
import platform

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

TRACER_CUSTOM_PATH = ''
platform_system = platform.system()
if platform_system == 'Windows':
    TRACER_CUSTOM_PATH = os.path.join(ROOT_DIR, 'tracer_custom.exe')
elif platform_system == 'Darwin':
    # Darwin / MacOS
    TRACER_CUSTOM_PATH = os.path.join(ROOT_DIR, 'tracer_custom_darwin')
else:
    # Linux
    TRACER_CUSTOM_PATH = os.path.join(ROOT_DIR, 'tracer_custom')
