import abce
epsilon = 1 / 10000


class Household(abce.Agent, abce.Household):
    def init(self, num_firms, wage_stickiness, **_):
        self.num_firms = num_firms
        self.wage_stickiness = wage_stickiness
        self.uf = self.create_cobb_douglas_utility_function({'g%i' % i: 1 / num_firms for i in range(num_firms)})
        self.create('money', 1)
        self.create('labor_endowment', 1)
        self.utility = 0
        self.wage = 0.5


    def send_demand(self):
        for i in range(self.num_firms):
            self.send(('firm', i), 'nominal_demand', 1 / self.num_firms * self.not_reserved("money"))

    def selling(self):
        """ receive demand from neighbors and consumer;
            calculate market_clearing_price, adaped the price slowly
            and sell the good to the neighbors, the quantity might
            be rationed.
        """
        messages = self.get_messages('nominal_demand')
        nominal_demand = [msg.content for msg in messages]
        assert self.not_reserved('labor') >= 0, self.not_reserved('labor')
        market_clearing_price = sum(nominal_demand) / self.not_reserved('labor')
        self.wage = (1 - self.wage_stickiness) * market_clearing_price + self.wage_stickiness * self.wage
        demand = sum([msg.content / self.wage for msg in messages])
        if demand <= self.not_reserved('labor'):
            self.rationing = rationing = 1 - epsilon
        else:
            self.rationing = rationing = max(0, self.not_reserved('labor') / demand - epsilon)

        for msg in messages:
            self.make_offer(msg.sender,  good='labor', quantity=msg.content / self.wage * rationing, price=self.wage)

    def buying(self):
        for neighbor in range(self.num_firms):
            for offer in self.get_offers('g%i' % neighbor):
                self.accept(offer)

    def consuming(self):
        self.utility = self.consume(self.uf, {good: self[good] for good in self.possessions() if good not in ['money', 'labor']})
