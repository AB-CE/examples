#pylint: disable=W0201
import abcEconomics as abce


class Government(abce.Agent):
    def init(self, simulation_parameters, _):
        self.num_households = simulation_parameters['num_household']

    def taxes_to_household(self):
        self.money = self.possession('money')
        share = self.money / self.num_households
        for i in range(self.num_households):
            self.give(('household', i), good='money', quantity=share)
