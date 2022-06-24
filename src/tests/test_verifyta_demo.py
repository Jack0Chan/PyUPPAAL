from pyuppaal import Verifyta
import time

if __name__ == '__main__':
    v = Verifyta()
    # You MUST set the verifyta path firstly!
    v.set_verifyta_path('/Users/chenguangyao/Downloads/uppaal64-4.1.26/bin-Darwin/verifyta')

    # verify P1 (verifyta_demo1.xml) and print result
    res = v.simple_verify(model_path='verifyta_demo1.xml', trace_path='verifyta_demo1_trace.xml')
    print(res)
