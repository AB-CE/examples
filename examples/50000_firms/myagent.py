from abcEconomics.agent import Agent
from random import shuffle


class MyAgent(Agent):
    def init(self):
        # print("m", self.id)
        pass

    def compute(self):
        # print('here', self.id)
        lst = list(range(1))
        shuffle(lst)
        max(lst)

    def g(self):
        for offer in self.get_offers('cookie'):
            self.accept(offer)
        # print(self.possession('cookie'))
