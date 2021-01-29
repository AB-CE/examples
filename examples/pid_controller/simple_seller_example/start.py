""" A simulation of the first Model of Ernesto Carrella's paper: Zero-Knowledge Traders,
journal of artificial societies and social simulation, december 2013

This is a partial 'equilibrium' model. A firm has a fixed production of 4 it offers
this to a fixed population of 10 household. The household willingness to pay is
household id * 10 (10, 20, 30 ... 90).
The firms sets the prices using a PID controller.
"""
from __future__ import division
from firm import Firm
from household import Household
from abcEconomics import Simulation


simulation_parameters = {'random_seed': None,
                         'rounds': 300}


def main(simulation_parameters):
    s = Simulation()

    firms = s.build_agents(Firm, 'firm', 10)
    households = s.build_agents(Household, 'household', 10)
    for r in range(int(simulation_parameters['rounds'])):
        s.advance_round(r)
        firms.panel_log(possessions=['cookies'])
        firms.quote()
        households.buying()
        firms.selling()
        households.panel_log(possessions=['cookies'])
        households.consumption()
    s.finalize()


if __name__ == '__main__':
    main(simulation_parameters)
