import abce


class Government(abce.Agent):
    def init(self, num_households):
        self.num_households = num_households

    def taxes_to_household(self):
        self.money = self.possession('money')
        share = self.money / self.num_households
        for i in range(self.num_households):
            self.give(('household', i), good='money', quantity=share)
