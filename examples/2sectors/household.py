import abcEconomics as abce


class Household(abce.Agent, abce.Household):
    def init(self):
        """ self.employer is the _number_ of the agent that receives his
        labor offer.
        """
        self.labor_endowment = 1
        self.utility_function = self.create_cobb_douglas_utility_function({"consumption_good": 1})
        self.accumulated_utility = 0
        self.employer = self.id
        self._inventory._perishable.append('labor')  # TODO simplify this

    def sell_labor(self):
        """ offers one unit of labor to firm self.employer, for the price of 1 "money" """
        self.sell(('firm', self.employer), "labor", quantity=1, price=1)

    def buy_intermediary_goods(self):
        """ recieves the offers and accepts them one by one """
        for offer in self.get_offers("consumption_good"):
            self.accept(offer)

    def consumption(self):
        """ consumes_everything and logs the aggregate utility. current_utiliy
        """
        current_utiliy = self.consume(self.utility_function, ['consumption_good'])
        self.accumulated_utility += current_utiliy
        self.log('HH', {'': self.accumulated_utility})
