""" A simulation of the first Model of Ernesto Carrella's paper:
Sticky Prices Microfoundations in a Agent Based Supply Chain
Section 4 Firms and Production

Here we have one firm and one market agent. The market agent
has the demand function q = 102 - p

"""
from __future__ import division
from multiprocessing import freeze_support
from firm import Firm
from market import Market
from abcEconomics import Simulation


simulation_parameters = {'name': "analytical",
                         'random_seed': None,
                         'rounds': 3000}


def main(simulation_parameters):
    s = Simulation()

    firms = s.build_agents(
        Firm, 'firm', parameters=simulation_parameters, number=1)
    market = s.build_agents(
        Market, 'market', parameters=simulation_parameters, number=1)
    for r in range(simulation_parameters['rounds']):
        s.advance_round(r)
        firms.my_production()
        firms.selling()
        market.buying()
        firms.adjust_price()
        firms.adjust_quantity()
        market.consumption()
    s.finalize()


if __name__ == '__main__':
    main(simulation_parameters)
