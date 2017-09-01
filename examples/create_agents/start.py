from __future__ import division
from firm import Firm
from household import Household
from messenger import Messenger
from abce import Simulation, gui


def main():
    simulation = Simulation()

    simulation.declare_round_endowment(resource='labor_endowment',
                                       units=1,
                                       product='labor',
                                       groups='household')

    simulation.declare_perishable(good='labor')

    firms = simulation.build_agents(Firm, 'firm', number=1)

    households = simulation.build_agents(Household, 'household', number=1)

    messengers = simulation.build_agents(Messenger, 'messenger', 1)

    for r in range(50):
        simulation.advance_round(r)
        messengers.do('messaging')
        (firms + households).do('receive_message')
        firms.do('add_household')
        firms.do('add_firm')
        firms.do('print_id')
        households.do('print_id')
        # this instructs ABCE to save panel data as declared below
        (firms + households).agg_log(variables=['count'])
    simulation.graphs()


if __name__ == '__main__':
    main()
