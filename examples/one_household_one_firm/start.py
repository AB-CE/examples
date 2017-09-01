""" 1. declared the timeline
    2. build one Household and one Firm follow_agent
    3. For every labor_endowment an agent has he gets one trade or usable labor
    per round. If it is not used at the end of the round it disapears.
    4. Firms' and Households' possesions are monitored ot the points marked in
    timeline.
"""

from abce import Simulation, gui
from firm import Firm
from household import Household

parameters = {'name': '2x2',
              'random_seed': None,
              'rounds': 10}


@gui(parameters)
def main(parameters):
    w = Simulation()
    w.declare_round_endowment(resource='adult', units=1, product='labor')
    w.declare_perishable(good='labor')


    firms = w.build_agents(Firm, 'firm', 1)
    households = w.build_agents(Household, 'household', 1)
    for rnd in range(parameters['rounds']):
        w.advance_round(rnd)
        households.sell_labor()
        firms.buy_labor()
        firms.production()
        firms.panel_log(possessions=['money', 'GOOD'])
        firms.sell_goods()
        households.buy_goods()
        households.panel_log(possessions=['money', 'GOOD'],
            variables=['current_utiliy'])
        households.consumption()
    w.finalize()


if __name__ == '__main__':
    main(parameters)
