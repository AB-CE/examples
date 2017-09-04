from __future__ import division
from firm import Firm
from household import Household
from messenger import Messenger
from abce import Simulation, gui


def main():
    simulation = Simulation()

    simulation.declare_round_endowment(resource='labor_endowment',
                                       units=1,
                                       product='labor')

    simulation.declare_perishable(good='labor')

    firms = simulation.build_agents(Firm, 'firm', number=1)

    households = simulation.build_agents(Household, 'household', number=1)

    messengers = simulation.build_agents(Messenger, 'messenger', 1)

    for r in range(50):
        simulation.advance_round(r)
        messengers.messaging()
        (firms + households).receive_message()
        firms.add_household()
        firms.add_firm()
        firms.print_id()
        households.print_id()
        # this instructs ABCE to save panel data as declared below
        (firms + households).agg_log(variables=['count'])
    simulation.graphs()


if __name__ == '__main__':
    main()
