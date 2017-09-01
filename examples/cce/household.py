import abce
from abce import NotEnoughGoods
from pprint import pprint
from sys import float_info
from collections import defaultdict

class Household(abce.Agent, abce.Household):
    def init(self, simulation_parameters, _):
        self.num_firms = num_firms = simulation_parameters['num_firms']
        self.wage_stickiness = simulation_parameters['wage_stickiness']
        money = simulation_parameters['money'] / 2

        self.create('money', money )
        self.utility = 0

        self.final_goods = simulation_parameters['final_goods']
        self.alpha = simulation_parameters['consumption_functions']['hoh']
        self.create('endowment_FFcap', simulation_parameters['endowment_FFcap'])
        self.create('endowment_FFlab', simulation_parameters['endowment_FFlab'])

        self.set_cobb_douglas_utility_function(self.alpha)
        self.sells = []
        self.welfare = 0

    def send_demand(self):
        for final_good in self.final_goods:
            for i in range(self.num_firms):
                demand = self.alpha[final_good] / self.num_firms * self.possession("money")
                if demand > 0:
                    self.message(final_good, i, final_good, demand)


    def selling(self):
        """ receive demand from neighbors and consumer;
            calculate market_clearing_price, adapted the price slowly
            and sell the good to the neighbors, the quantity might
            be rationed.
        """
        messages = self.get_messages_all()
        for capital_type, ct_messages in messages.items():
            nominal_demand = [msg.content for msg in ct_messages]
            market_clearing_price = sum(nominal_demand) / self.possession(capital_type)
            if self.round > 5:
                self.price = price = (1 - self.wage_stickiness) * market_clearing_price + self.wage_stickiness * self.price
            else:
                self.price = price = market_clearing_price
            demand = sum([msg.content / price for msg in ct_messages])
            if demand < self.possession(capital_type):
                self.rationing = rationing = 1
            else:
                self.rationing = rationing = self.possession(capital_type) / demand
            for msg in ct_messages:
                sell = self.sell(receiver_group=msg.sender_group,
                                 receiver_id=msg.sender_id,
                                 good=capital_type,
                                 quantity=msg.content / price * rationing,
                                 price=price)
                self.sells.append(sell)

    def buying(self):
        for final_good in self.final_goods:
            for offer in self.get_offers(final_good):
                self.accept(offer)

    def money_to_nx(self):
        self.give('netexport', 0, quantity=self.possession('money'), good='money')

    def sales_accounting(self):
        self.sales_earning = sum([sell.final_quantity * sell.price for sell in self.sells])
        self.sells = []

    def consuming(self):
        self.welfare = self.consume_everything()

