# import os
# import time
import pyuppaal as pyu
# import iTools/buildCG as cg // fault



p1_model_path =r'C:\Users\22215\OneDrive\Coding\PlayGround\Github\pyuppaal\src\tests\Pedestrian.xml'
# method1
# pyu.get_communication_graph(model_path = p1_model_path)

# method2
m = pyu.UModel(p1_model_path)
m.get_communication_graph(r'C:\Users\22215\OneDrive\Coding\PlayGround\Github\pyuppaal\src\tests\Pedestrian.md')