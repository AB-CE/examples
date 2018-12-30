#pylint: disable=W0201
import random
from copy import copy
import numpy as np
import abcEconomics as abce
from abcEconomics import NotEnoughGoods
from optimization_functions import optimization


epsilon = 1 / 10000


def good_from_id(idn):
    return 'g%i' % idn

def normalized_random(length):
    random_values = [random.uniform(0.1, 0.9) for _ in range(length)]
    sum_values = sum(random_values)
    return np.array([v / sum_values for v in random_values])

class Firm(abce.Agent, abce.Firm):
    def init(self, num_firms, alpha, gamma, price_stickiness, dividends_percent, network_weight_stickiness, time_of_intervention,
             neighbors, **trash):
        self.num_firms = num_firms
        self.alpha = alpha
        self.gamma = gamma
        self.price_stickiness = price_stickiness
        self.dividends_percent = dividends_percent
        self.network_weight_stickiness = network_weight_stickiness
        self.time_of_intervention = time_of_intervention

        self.neighbors = neighbors
        self.neighbors_goods = [good_from_id(idn) for idn in self.neighbors]
        self.mygood = good_from_id(self.id)
        prices = [1.0 for _ in self.neighbors]
        prices.append(1.0)
        prices = np.array(prices, dtype=float)
        self.neighbor_prices = prices[:-1]
        self.wage = prices[-1]

        weigth_and_labor_weight = normalized_random(len(prices))
        self.seed_weights = weigth_and_labor_weight
        self.weights = weigth_and_labor_weight[:-1]
        self.labor_weight = weigth_and_labor_weight[-1]

        self.create(self.mygood, 1)
        self.create('money', 1)
        self.money_1 = self.not_reserved('money')

        self.price = 1
        self.profit = 0
        self.profit_1 = 0
        self.labor_endowment = 0

    def produce(self, input_goods):
        """ Produce according to CES production function """
        for good in input_goods:
            if self.not_reserved(good) < input_goods[good]:
                raise NotEnoughGoods(self.name, good, (input_goods[good] - self[good]))

        for good in input_goods:
            self.destroy(good, input_goods[good])

        production = input_goods['labor'] ** self.alpha * sum([input_goods[good] ** self.gamma
                                                               for good in input_goods
                                                               if good not in ['labor', self.mygood]]) ** ((1 - self.alpha) / self.gamma)
        self.create(self.mygood, production)
        self.produced = production

    def send_demand(self):
        """ send nominal demand, according to weights to neighbor """
        for neighbor, weight in zip(self.neighbors, self.weights):
            self.send_envelope(('firm', neighbor), 'nominal_demand', weight * self.not_reserved("money"))

        self.send_envelope(('household', 0), 'nominal_demand', self.labor_weight * self.not_reserved('money'))

    def selling(self):
        """ receive demand from neighbors and consumer;
            calculate market_clearing_price, adaped the price slowly
            and sell the good to the neighbors, the quantity might
            be rationed.
        """
        messages = self.get_messages('nominal_demand')
        nominal_demand = [msg.content for msg in messages]
        assert sum(nominal_demand) > 0
        assert self.not_reserved(self.mygood) > 0
        market_clearing_price = sum(nominal_demand) / self.not_reserved(self.mygood)
        self.price = (1 - self.price_stickiness) * market_clearing_price + self.price_stickiness * self.price
        print(messages[0].content)
        demand = sum([msg.content / self.price for msg in messages])
        if demand <= self.not_reserved(self.mygood):
            self.rationing = rationing = 1 - epsilon
        else:
            self.rationing = rationing = self.not_reserved(self.mygood) / demand - epsilon

        for msg in messages:
            self.sell(msg.sender, good=self.mygood, quantity=msg.content / self.price * rationing, price=self.price)

    def buying(self):
        """ get offers from each neighbor, accept it and update
            neighbor_prices and neighbors_goods """
        for offers in self.get_offers_all().values():
            for offer in offers:
                self.accept(offer)
                if offer.good == 'labor':
                    self.wage = offer.price
                else:
                    index = self.neighbors.index(offer.sender_id)
                    self.neighbor_prices[index] = offer.price
                    self.neighbors_goods[index] = offer.good

    def production(self):
        """ produce using all goods and labor """
        input_goods = {good: self.not_reserved(good) for good in self.neighbors_goods + ['labor']}
        self.input_goods = copy(input_goods)
        self.produce(input_goods)

    def dividends(self):
        """ pay dividends to household if profit is positive, calculate profits """
        self.profit = self.not_reserved('money') - self.money_1
        earnings = max(0, self.profit)
        self.give(('household', 0), good='money', quantity=self.dividends_percent * earnings)
        self.money_1 = self.not_reserved('money')

    def _change_weights(self, neighbor_prices, seed_weights):
        for _ in range(10):
            opt = optimization(seed_weights=seed_weights,
                               input_prices=np.array(neighbor_prices),
                               wage=self.wage,
                               gamma=self.gamma,
                               one_by_gamma=1 / self.gamma,
                               l=self.alpha,
                               one_minus_l=1 - self.alpha)
            if not opt.success:
                print(self.name, opt.message, (len(seed_weights)))  # , self.neighbor_prices, self.seed_weights)
                seed_weights = normalized_random(len(seed_weights))
            else:
                break

        optimal_weights_non_labor, optimal_weights_labor = opt.x[:-1], opt.x[-1]
        return opt.x, optimal_weights_non_labor, optimal_weights_labor

    def change_weights(self):
        optx, optimal_weights_non_labor, optimal_weights_labor = self._change_weights(self.neighbor_prices,
                                                                                      self.seed_weights)
        self.seed_weights = optx
        if any(self.seed_weights <= 0):
            self.seed_weights = normalized_random(len(self.seed_weights))
        self.weights = (self.network_weight_stickiness * self.weights +
                        (1 - self.network_weight_stickiness) * optimal_weights_non_labor)
        self.labor_weight = (self.network_weight_stickiness * self.labor_weight +
                             (1 - self.network_weight_stickiness) * optimal_weights_labor)
        summe = np.nextafter(sum(self.weights) + self.labor_weight, 2)
        self.weights = np.nextafter(self.weights / summe, 0)
        self.labor_weight = np.nextafter(self.labor_weight / summe, 0)

        assert all(self.weights) >= 0, self.weights
        assert self.labor_weight > 0
        assert 0.99999 < sum(self.weights) + self.labor_weight < 1.00001, (self.weights, self.labor_weight)

    def stats(self):
        """ helper for statistics """
        if self.not_reserved('money') > epsilon:
            self.dead = 0
        else:
            self.dead = 1
        self.inventory = self.not_reserved(self.mygood)
        if self.time == self.time_of_intervention:
            self.send_envelope(('centralbank', 0), 'grant', {'money': self.not_reserved('money')})
