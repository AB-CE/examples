"""
Sugarscape ({G1}, {M, T}) -- Epstein Chapter 4
Heavily use Mesa for space.
"""

import matplotlib
matplotlib.use('TkAgg')

from agents import SugarPatch, SpicePatch, SsAgent
from abcEconomics import Simulation
from mesa.space import MultiGrid
import pylab


def main():
    s = Simulation(processes=1)
    grid = MultiGrid(50, 50, True)

    # build sugar and spice
    sugar_distribution = pylab.genfromtxt("sugar-map.txt")
    spice_distribution = sugar_distribution.T
    sugars = []
    spices = []
    for _, x, y in grid.coord_iter():
        max_sugar = sugar_distribution[x, y]
        max_spice = spice_distribution[x, y]
        sugar = SugarPatch((x, y), max_sugar)
        spice = SpicePatch((x, y), max_spice)
        sugars.append(sugar)
        spices.append(spice)
        grid.place_agent(sugar, (x, y))
        grid.place_agent(spice, (x, y))

    # build agents
    agents = s.build_agents(SsAgent, 'SsAgent', 100,
                            parameters={'grid': grid})

    # prices = []
    for r in range(100):
        s.advance_round(r)
        for sugar in sugars:
            sugar.step()
        for spice in spices:
            spice.step()
        agents.move()
        agents.eat()
        print(',', len(agents.trade_with_neighbors()))

        agents.trade()
        agents.agg_log(possessions=['sugar', 'spice'])

    s.finalize()


if __name__ == '__main__':
    main()
