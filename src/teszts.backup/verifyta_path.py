import os
import platform

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

WINDOWS_VERIFYTA_PATH = os.path.join(ROOT_DIR, 'uppaal/Win_Linux-uppaal64-4.1.26/bin-Windows/verifyta.exe')
LINUX_VERIFYTA_PATH = os.path.join(ROOT_DIR, 'uppaal/Win_Linux-uppaal64-4.1.26/bin-Linux/verifyta')
MAC_VERIFYTA_PATH = os.path.join(ROOT_DIR, 'uppaal/macOS-uppaal64-4.1.26/bin-Darwin/verifyta')

path_dir = {
	'Windows': WINDOWS_VERIFYTA_PATH,
	'Linux': LINUX_VERIFYTA_PATH,
	'Darwin': MAC_VERIFYTA_PATH
}

VERIFYTA_PATH = path_dir[platform.system()]
