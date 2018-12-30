from abcEconomics.agent import Agent
from random import shuffle, randint


class YourAgent(Agent):
    def init(self):
        pass

    def compute(self):
        lst = list(range(1))
        shuffle(lst)
        max(lst)

    def s(self):
        self.create('cookie', 1)
        self.sell(('myagent', randint(0, self.id)),
                  good='cookie', price=0, quantity=1)
        assert self['cookie'] == 1
