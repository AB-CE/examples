from firm import Firm
from household import Household
from centralbank import CentralBank
from abcEconomics import Simulation
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


def main():
    simulation_parameters = {'name': 'direct_optimization',
                             'random_seed': None,
                             'rounds': 500,
                             'trade_logging': 'off',
                             'num_firms': 250,
                             'alpha': 0.3,
                             'gamma': 0.8,
                             'price_stickiness': 0.0,
                             'network_weight_stickiness': 0.0,
                             'wage_stickiness': 0.0,
                             'dividends_percent': 0.0,
                             'percentage_beneficiaries': 0.25,
                             'percentage_injection': 0.25,
                             'time_of_intervention': 250}
    s = Simulation(name=simulation_parameters['name'])

    network = create_network(simulation_parameters['num_firms'])
    network = [{'neighbors': network.neighbors(neighbor)} for neighbor in range(simulation_parameters['num_firms'])]
    firms = s.build_agents(Firm, 'firm', **simulation_parameters,
                           agent_parameters=[n for n in network])
    household = s.build_agents(Household, 'household', 1,
                               num_firms=simulation_parameters['num_firms'],
                               wage_stickiness=simulation_parameters['wage_stickiness'])
    centralbank = s.build_agents(CentralBank, 'centralbank', 1,
                                 time_of_intervention=simulation_parameters['time_of_intervention'],
                                 percentage_injection=simulation_parameters['percentage_injection'],
                                 percentage_beneficiaries=simulation_parameters['percentage_beneficiaries'])

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
        household.agg_log(goods=['money'],
                          variables=['utility', 'rationing'])
        firms.agg_log(goods=['money'],
                      variables=['produced', 'profit', 'price', 'dead', 'inventory', 'rationing'])
        (household + firms).refresh_services('labor', 'labor_endowment', units=1)

    s.finalize()


if __name__ == '__main__':
    main()
