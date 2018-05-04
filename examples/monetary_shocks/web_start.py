from firm import Firm
from household import Household
from centralbank import CentralBank
from abce import Simulation, gui
from random import shuffle
import networkx
from random import randrange


def create_network(num_firms):
    """ the firms are placed on a "scale-free network";
    generated through the barabasi-albert algorithm """
    G = networkx.scale_free_graph(num_firms)
    for i in range(num_firms):
        if len(G.out_edges(i)) == 0:
            G.add_edge(i, randrange(num_firms))
        if len(G.in_edges(i)) == 0:
            G.add_edge(randrange(num_firms), i)

    mapping = list(range(num_firms))
    shuffle(mapping)
    mapping = dict(enumerate(mapping))
    return G


simulation_parameters = {'name': 'test',
                         'random_seed': None,
                         'rounds': 100,
                         'trade_logging': 'off',
                         'num_firms': 100,
                         'alpha': 0.7,
                         'gamma': 0.5,
                         'price_stickiness': (0.0, 0.0, 1.0),
                         'network_weight_stickiness': (0.0, 0.0, 1.0),
                         'wage_stickiness': (0.0, 0.0, 1.0),
                         'dividends_percent': (0.0, 0.0, 1.0),
                         'percentage_beneficiaries': 0.25,
                         'percentage_injection': 0.25,
                         'time_of_intervention': 500}


@gui(simulation_parameters)
def main(simulation_parameters):

    s = Simulation(name=simulation_parameters['name'])

    s.declare_service('labor_endowment', 1, 'labor')

    network = create_network(simulation_parameters['num_firms'])
    network = [network.neighbors(neighbor) for neighbor in range(simulation_parameters['num_firms'])]
    firms = s.build_agents(Firm, 'firm', parameters=simulation_parameters,
                           agent_parameters=network)
    household = s.build_agents(Household, 'household', 1, parameters=simulation_parameters)
    centralbank = s.build_agents(CentralBank, 'centralbank', 1, parameters=simulation_parameters)

    for rnd in range(simulation_parameters['rounds']):
        s.advance_round(rnd)
        (firms + household).send_demand()
        (firms + household).selling()
        (firms + household).buying()
        firms.production()
        firms.dividends()
        household.consuming()
        firms.change_weights()
        firms.stats()
        centralbank.intervention()
        household.agg_log(possessions=['money'],
                          variables=['utility', 'rationing'])
        firms.agg_log(possessions=['money'],
                      variables=['produced', 'profit', 'price', 'dead', 'inventory', 'rationing'])
    s.finalize()

if __name__ == '__main__':
    main(simulation_parameters)

