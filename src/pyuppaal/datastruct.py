"""_summary_
"""
from typing import List


class TimedActions:
    """ A serie of actions with lower bounds and upper bounds.
    """

    def __init__(self, actions: List[str], lb: List[str] = None, ub: List[str] = None):
        """_summary_

        Args:
            actions (List[str]): a list of actions.
            lb (List[str], optional): a list of lowerbounds. Defaults to None.
            ub (List[str], optional): a list of upperbounds. Defaults to None.

        Examples:
            >>> timed_actions = TimedActions(['sigOut!', 'sigOut!'], 
            >>>     ['gclk>=20', 'x>=30'], ['gclk<=20', 'x<=30'])
        """
        self.__actions: List[str] = actions
        self.lb = lb
        self.ub = ub
        if self.lb is None:
            self.lb = [-1 for i in range(len(self.actions))]
        if self.ub is None:
            self.ub = [-1 for i in range(len(self.actions))]

    @property
    def actions(self) -> List[str]:
        """A serie of actions 

        Examples:
            >>> timed_actions = TimedActions(['sigOut!', 'sigOut!'], 
            >>>     ['gclk>=20', 'x>=30'], ['gclk<=20', 'x<=30'])
            >>> timed_actions.actions
            ['sigOut!', 'sigOut!']

        Returns:
            List[str]: a list of actions.
        """
        return self.__actions

    @property
    def is_patterns(self) -> bool:
        """Whether the timed actions are patterns.

        Examples:
            >>> timed_actions = TimedActions(['sigOut!', 'sigOut!'], 
            >>>     ['gclk>=20', 'x>=30'], ['gclk<=20', 'x<=30'])
            >>> timed_actions.is_patterns
            False

        Returns:
            bool: True if the timed actions are patterns.
        """
        return all(self.lb) == -1 and all(self.ub) == -1

    def convert_to_list_tuple(self, clk_name='monitor_clk'):
        """Convert to a list of tuple, each tuple is a timed action.

        Examples:
            >>> timed_actions = TimedActions(['sigOut!', 'sigOut!'], 
            >>>     ['gclk>=20', 'x>=30'], ['gclk<=20', 'x<=30'])
            >>> timed_actions.convert_to_list_tuple()
            [('sigOut!', 'gclk>=20', 'gclk<=20'), ('sigOut!', 'x>=30', 'x<=30')]

        Returns:
            List[Tuple[str, str, str]]: a list of tuple, each tuple is a timed action.
        """

        self.clk_name = clk_name
        res = []
        for i in range(len(self.actions)):
            res.append(
                (self.actions[i], f'{clk_name}>={self.lb[i]}', f'{clk_name}<={self.ub[i]}'))
        return res

    def convert_to_patterns(self):
        """Convert to patterns.

        Examples:
            >>> timed_actions = TimedActions(['sigOut!', 'sigOut!'],
            >>>     ['gclk>=20', 'x>=30'], ['gclk<=20', 'x<=30'])
            >>> timed_actions.convert_to_patterns()
            ['sigOut!', 'sigOut!']

        Returns:
            List[str]: a list of actions.
        """
        return self.actions

    def __len__(self):
        return len(self.actions)
