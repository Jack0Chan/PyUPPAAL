from typing import List
from collections import namedtuple


# timedtuple
class TimedActions:
    def __init__(self, actions: List[str], lb: List[int] = None, ub: List[str] = None):
        self.actions = actions
        self.lb = lb
        self.ub = ub
        if self.lb is None:
            self.lb = [-1 for i in range(len(self.actions))]
        if self.ub is None:
            self.ub = [-1 for i in range(len(self.actions))]
    
    @property
    def is_patterns(self):
        return all(self.lb) == -1 and all(self.ub) == -1

    def convert_to_list_tuple(self, clk_name='monitor_clk'):
        self.clk_name = clk_name
        res = []
        for i in range(len(self.actions)):
            res.append((self.actions[i], f'{clk_name}>={self.lb[i]}', f'{clk_name}<={self.ub[i]}'))
        return res
    
    def convert_to_patterns(self):
        return self.actions
