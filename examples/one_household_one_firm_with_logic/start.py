""" 1. declared the timeline
    2. build one Household and one Firm follow_agent
    3. For every labor_endowment an agent has he gets one trade or usable labor
    per round. If it is not used at the end of the round it disapears.
    4. Firms' and Households' possesions are monitored ot the points marked in
    timeline.
"""

from abce import Simulation
from firm import Firm
from household import Household


num_firms = 20

simulation = Simulation(processes=1)
simulation.declare_round_endowment(resource='adult',
                                   units=1,
                                   product='labor')
simulation.declare_perishable(good='labor')

firms = simulation.build_agents(Firm, 'firm', number=num_firms)
households = simulation.build_agents(Household, 'household', number=1, num_firms=num_firms)

try:
    for rnd in range(50):
        simulation.advance_round(rnd)
        households.sell_labor()
        firms.buy_labor()
        firms.production()
        firms.panel_log(possessions=['money', 'GOOD'],
                        variables=['price', 'inventory'])
        firms.quotes()
        households.buy_goods()
        firms.sell_goods()
        households.agg_log(possessions=['money', 'GOOD'],
                           variables=['current_utiliy'])
        households.consumption()
        firms.adjust_price()
finally:
    simulation.graphs()


