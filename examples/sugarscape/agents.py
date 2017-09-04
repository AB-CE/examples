import random
import pylab
from abce import Agent, NotEnoughGoods


def get_distance(pos_1, pos_2):
    x1, y1 = pos_1
    x2, y2 = pos_2
    dx = x1 - x2
    dy = y1 - y2
    return pylab.sqrt(dx ** 2 + dy ** 2)


class Sugar(Agent):
    def __init__(self, pos, max_sugar):
        self.pos = pos
        self.amount = max_sugar
        self.max_sugar = max_sugar

    def step(self):
        self.amount = min([self.max_sugar, self.amount + 1])


class Spice(Agent):
    def __init__(self, pos, max_spice):
        self.pos = pos
        self.amount = max_spice
        self.max_spice = max_spice

    def step(self):
        self.amount = min([self.max_spice, self.amount + 1])


class SsAgent(Agent):
    def init(self, parameters, agent_parameters):
        self.moore = False
        self.grid = parameters["grid"]
        self.set_at_random_unoccupied_pos()
        self.grid.place_agent(self, self.pos)
        self.create('sugar', random.randrange(25, 50))
        self.create('spice', random.randrange(25, 50))
        self.metabolism = random.randrange(1, 5)
        self.metabolism_spice = random.randrange(1, 5)
        self.vision = random.randrange(1, 6)
        self.prices = []
        self.dead = False

    def set_at_random_unoccupied_pos(self):
        x = random.randrange(self.grid.width)
        y = random.randrange(self.grid.height)
        if not self.is_occupied((x, y)):
            self.pos = (x, y)
            return
        self.set_at_random_unoccupied_pos()

    def get_sugar(self, pos):
        this_cell = self.grid.get_cell_list_contents([pos])
        for agent in this_cell:
            if type(agent) is Sugar:
                return agent

    def get_spice(self, pos):
        this_cell = self.grid.get_cell_list_contents([pos])
        for agent in this_cell:
            if type(agent) is Spice:
                return agent

    def get_ssagent(self, pos):
        this_cell = self.grid.get_cell_list_contents([pos])
        for agent in this_cell:
            if isinstance(agent, SsAgent):
                return agent

    def is_occupied(self, pos):
        this_cell = self.grid.get_cell_list_contents([pos])
        return len(this_cell) > 2

    def move(self):
        if self.dead:
            return
        # hack this checkalive shouldn't be here
        # Epstein rule M
        # Get neighborhood within vision
        neighbors = [i for i in self.grid.get_neighborhood(self.pos, self.moore,
                     False, radius=self.vision) if not self.is_occupied(i)]
        neighbors.append(self.pos)
        eps = 0.0000001
        # Find the patch which produces maximum welfare
        welfares = [self.welfare(self['sugar'] + self.get_sugar(pos).amount,
                    self['spice'] + self.get_spice(pos).amount) for pos in neighbors]
        max_welfare = max(welfares)
        candidate_indices = [i for i in range(len(welfares)) if abs(welfares[i] -
                             max_welfare) < eps]
        candidates = [neighbors[i] for i in candidate_indices]
        # Find the nearest patch among the candidate
        try:
            min_dist = min([get_distance(self.pos, pos) for pos in candidates])
        except:
            print(welfares)
            print(self.welfare())
            print(self['sugar'])
            print(self['spice'])
            print(neighbors)
            exit()
        final_candidates = [pos for pos in candidates if abs(get_distance(self.pos,
                            pos) - min_dist) < eps]
        random.shuffle(final_candidates)
        self.grid.move_agent(self, final_candidates[0])

    def eat(self):
        sugar_patch = self.get_sugar(self.pos)
        spice_patch = self.get_spice(self.pos)
        try:
            self.destroy('sugar', self.metabolism + sugar_patch.amount)
            self.destroy('spice', self.metabolism_spice + spice_patch.amount)
        except NotEnoughGoods:
            self.delete_agent('SsAgent', self.id, quite=False)
            self.grid.remove_agent(self)
            self.dead = True

        sugar_patch.amount = 0
        spice_patch.amount = 0


    def sell_spice(self, other):
        mrs_self = self.calculate_MRS()
        mrs_other = other.calculate_MRS()

        price = pylab.sqrt(mrs_self * mrs_other)
        price = max(0.000000000001, price)
        if self['spice'] >= 1:
            self.sell(other.name, 'spice', quantity=1, price=price, currency='sugar')
        if self['sugar'] >= 1:
            quantity = min(1, self['sugar'] * price)
            self.buy(other.name, 'spice', quantity=quantity, price=1 / price, currency='sugar')

    def trade_with_neighbors(self):
        if self.dead:
            return
        # von Neumann neighbors
        neighbor_agents = [self.get_ssagent(pos) for pos in self.grid.get_neighborhood(self.pos, self.moore,
                           False, radius=self.vision) if self.is_occupied(pos)]
        if neighbor_agents:
            random.shuffle(neighbor_agents)
            count = 0
            for a in neighbor_agents:
                if a:
                    self.sell_spice(a)
                    count += 1
            if count > 0:
                prices = [p for p in self.prices if p]
                self.prices = []
                #print("%d Traded with %d out of %d neighbors" % (self.id, count, len(neighbor_agents)))
                return prices
        return []

    def trade(self):
        # Epstein rule T for a pair of agents, page 105
        for offer in self.get_offers('spice'):
            baseline = self.welfare()
            if offer.buysell == 115:
                welfare = self.welfare(spice=self['spice'] + 1, sugar=self['sugar'] - 1)
            elif offer.buysell == 98:
                welfare = self.welfare(spice=self['spice'] - 1, sugar=self['sugar'] + 1)
            if welfare > baseline:
                try:
                    self.accept(offer)
                except (NotEnoughGoods, KeyError):
                    self.reject(offer)

    def welfare(self, sugar=None, spice=None):
        if sugar is None:
            sugar = self['sugar']
        if spice is None:
            spice = self['spice']
        m_total = self.metabolism + self.metabolism_spice
        return sugar ** (self.metabolism / m_total) * spice ** (self.metabolism_spice / m_total)

    def calculate_MRS(self):
        return (self['spice'] / self.metabolism_spice) / (self['sugar'] / self.metabolism)

    def compare_MRS(self, agent):
        return self.calculate_MRS() == agent.calculate_MRS()
