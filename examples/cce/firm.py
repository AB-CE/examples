#pylint: disable=W0201
import random
from copy import copy
from collections import OrderedDict
import itertools

import numpy as np
import abcEconomics as abce
from optimization_functions import optimization

def normalized_random(length):
    random_values = [random.uniform(0.1, 0.9) for _ in range(length)]
    sum_values = sum(random_values)
    return np.array([v / sum_values for v in random_values])

class GoodDetails:
    def __init__(self, betas, capital_types, num_firms):
        self.entities = OrderedDict()
        self.ids = OrderedDict()
        self.goods = OrderedDict()
        self.prices = OrderedDict()
        self.weights = OrderedDict()
        self.betas = []
        for good, value in betas.items():
            if value > 0:
                self.betas.append(value)
                if good in capital_types:
                    self.entities[good] = ['household']
                    self.ids[good] = [0]
                    self.goods[good] = [good]
                    self.prices[good] = [None]
                    self.weights[good] = [None]
                else:
                    self.entities[good] = [good for id in range(num_firms)]
                    self.ids[good] = [id for id in range(num_firms)]
                    self.goods[good] = [good for id in range(num_firms)]
                    self.prices[good] = [None for id in range(num_firms)]
                    self.weights[good] = [None for id in range(num_firms)]

    def list_of_cheapest_offers(self):
        cheapest_offers = []
        for good in self.goods:
            cheapest_offers.append(min(self.prices[good]))
        return np.array(cheapest_offers, dtype=float)

    def update_weights_optimal_from_partial_list(self, weights):
        for good in self.goods:
            for i in range(len(self.weights[good])):
                self.weights[good][i] = 0

        for i, good in enumerate(self.goods):
            index = np.argmax(self.prices[good])
            self.weights[good][index] = weights[i]

    def weights_as_list(self):
        weights = [w for w in self.weights.values()]
        return np.array(list(itertools.chain.from_iterable(weights)))

    def set_weights_from_full_list(self, weights):
        i = 0
        for sublist in self.weights.values():
            for s in range(len(sublist)):
                sublist[s] = weights[i]
                i += 1

    def set_prices_from_list(self, prices):
        i = 0
        for sublist in self.prices.values():
            for s in range(len(sublist)):
                sublist[s] = prices[i]
                i += 1

    def set_price(self, good, nr, price):
        self.prices[good][nr] = price

    def __len__(self):
        return sum([len(entry) for entry in self.entities.values()])

    def num_goods(self):
        return len(self.entities)

    def __iter__(self):
        for good in self.entities:
            for x in zip(self.entities[good], self.ids[good], self.goods[good], self.prices[good], self.weights[good]):
                yield x


class Firm(abce.Agent, abce.Firm):
    def init(self, num_firms, price_stickiness, network_weight_stickiness, dividends_percent, capital_types,
             output_tax_shares, production_functions, outputs, money, sam, tax_change_time, carbon_prod, carbon_tax,
             tax, **trash):
        self.num_firms = num_firms
        self.price_stickiness = price_stickiness
        self.dividends_percent = dividends_percent
        self.network_weight_stickiness = network_weight_stickiness
        self.capital_types = capital_types
        self.output_tax_share = output_tax_shares[self.group]
        production_function = production_functions[self.group]
        money = money / 2 / (self.num_firms * len(outputs))
        betas = production_function[1]
        self.sbtax = sam.entries['tax'][self.group]
        self.value_of_international_sales = sam.endowment_vector('nx')[self.group]
        self.value_of_investment = sam.endowment_vector('inv')[self.group]
        self.tax_change_time = tax_change_time
        self.carbon_prod = carbon_prod[self.group] / (sam.column_sum[self.group] - sam.entries[self.group]['nx'])
        self.carbon_tax_after = carbon_tax * 12 / 44
        self.carbon_tax = 0

        self.after_policy_change_output_tax_share = tax[self.group] / 100

        self.goods_details = GoodDetails(betas, self.capital_types, self.num_firms)
        self.goods_details.set_prices_from_list(normalized_random(len(self.goods_details)))

        self.seed_weights = normalized_random(self.goods_details.num_goods())
        self.goods_details.set_weights_from_full_list(normalized_random(len(self.goods_details)))

        self.create(self.group, sam.column_sum[self.group])
        # initial endowment of own good and price must be consistent (=the same)
        self.create('money', money)
        self.money_1 = self.possession('money')

        self.price = 1
        self.profit = 0

        self.b = production_function[0]
        self.beta = {good: value for good, value in production_function[1].items() if value > 0}

        self.set_cobb_douglas(self.group, self.b, self.beta)
        self.sales = []
        self.nx = 0

    def taxes_intervention(self):
        if self.round == self.tax_change_time:
            self.carbon_tax = self.carbon_tax_after
            self.output_tax_share = self.after_policy_change_output_tax_share

    def international_trade(self):
        if self.value_of_international_sales > 0:
            value = min(self.value_of_international_sales, self.possession(self.group))
            sale = self.sell(('netexport', 0), good=self.group, quantity=value, price=self.price)
            self.sales.append(sale)
        else:
            value = min(- self.value_of_international_sales, self.possession('money') / self.price)
            self.buy(('netexport', 0), good=self.group, quantity=value, price=self.price)
            self.nx = value

    def invest(self):
        if self.value_of_investment > 0:
            value = min(self.value_of_investment, self.possession(self.group))
            sale = self.sell(('netexport', 0), good=self.group, quantity=value, price=self.price)
            self.sales.append(sale)

    def send_demand(self):
        """ send nominal demand, according to weights to neighbor """
        for entity, id, good, _, weight in self.goods_details:
            self.send((entity, id),
                      good,
                      weight * self.possession('money'))

    def selling(self):
        """ receive demand from neighbors and consumer;
            calculate market_clearing_price, adaped the price slowly
            and sell the good to the neighbors, the quantity might
            be rationed.
        """
        messages = self.get_messages(self.group)
        nominal_demand = [msg.content for msg in messages]
        self.nominal_demand = sum(nominal_demand)
        if self.possession(self.group) > 0:
            market_clearing_price = (sum(nominal_demand) / self.possession(self.group))
            self.price = (1 - self.price_stickiness) * market_clearing_price + self.price_stickiness * self.price
            demand = sum([msg.content / self.price for msg in messages])
            if demand < self.possession(self.group):
                self.rationing = rationing = 1
            else:
                self.rationing = rationing = max(0, self.possession(self.group) / demand)

            for msg in messages:
                quantity = msg.content / self.price * rationing
                assert not np.isnan(quantity), (msg.content, self.price, rationing)
                sale = self.sell(msg.sender, good=self.group, quantity=quantity, price=self.price)
                self.sales.append(sale)
        else:
            for msg in messages:
                sale = self.sell((msg.sender_group, msg.sender_id), good=self.group, quantity=0, price=self.price)
                self.sales.append(sale)

    def sales_tax(self):
        total_sales_quantity = sum([sale.final_quantity for sale in self.sales]) - self.nx
        tax = (total_sales_quantity * self.price) * self.output_tax_share
        self.give(('government', 0), good='money', quantity=min(self.possession('money'), tax))
        self.sales = []

    def carbon_taxes(self):
        carbon_tax = self.produced * self.carbon_prod * self.carbon_tax * (1 - self.output_tax_share)
        self.give(('government', 0), good='money', quantity=min(self.possession('money'), carbon_tax))

    def buying(self):
        """ get offers from each neighbor, accept it and update
            neighbor_prices and neighbors_goods """
        for offers in self.get_offers_all().values():
            for offer in offers:
                self.accept(offer)
                self.goods_details.set_price(offer.good, offer.sender_id, offer.price)

    def production(self):
        """ produce using all goods and labor """
        input_goods = {input: self.possession(input) for input in self.beta.keys()}
        self.input_goods = copy(input_goods)
        p = self.produce(input_goods)
        self.produced = p[self.group]

    def dividends(self):
        """ pay dividends to household if profit is positive, calculate profits """
        self.profit = self.possession('money') - self.money_1
        earnings = max(0, self.profit)
        self.give(('household', 0), good='money', quantity=self.dividends_percent * earnings)
        self.money_1 = self.possession('money')

    def change_weights(self):
        opt = optimization(seed_weights=self.seed_weights,
                           input_prices=self.goods_details.list_of_cheapest_offers(),
                           b=self.b,
                           beta=self.goods_details.betas,
                           method='SLSQP')
        if not opt.success:
            print(self.round, self.name, opt.message)
            print(zip(self.goods_details.goods.keys(), self.goods_details.list_of_cheapest_offers().tolist()))
            raise Exception('Optimization error')

        self.seed_weights = opt.x

        old_weighs = self.goods_details.weights_as_list()
        self.goods_details.update_weights_optimal_from_partial_list(opt.x)
        optimal_weights = self.goods_details.weights_as_list()

        weights = (self.network_weight_stickiness * old_weighs +
                   (1 - self.network_weight_stickiness) * optimal_weights)

        weights = weights / sum(weights)

        self.goods_details.set_weights_from_full_list(weights)

    def stats(self):
        """ helper for statistics """
        self.co2 = self.produced * self.carbon_prod
