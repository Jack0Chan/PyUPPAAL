import os
import pyuppaal
from pyuppaal import UModel

pyuppaal.DeveloperTools.set_verifyta_path_dev()


def bring_to_root(file_name: str):
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(ROOT_DIR, file_name)

def test_umodel_verify():
    umodel = UModel(bring_to_root('pedestrian.xml'))
    print(umodel.easy_verify())
    
if __name__ == '__main__':
    test_umodel_verify()
    