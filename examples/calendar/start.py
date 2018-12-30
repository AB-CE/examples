from agent import Agent
from abcEconomics import Simulation

def main():
    """ Demonstration of the simulation.advance_round function, which can
    take arbitrary values """
    simulation = Simulation()
    agents = simulation.build_agents(Agent, 'agent', number=1)

    weekday = 0
    for year in range(2000, 2010):
        for month in range(12):
            for day in range(30):
                simulation.advance_round((year, month, day))
                weekday = (weekday + 1) % 7
                print(weekday)
                if weekday == 3:
                    agents.wednessday()
                if day == 1:
                    agents.first()
                if month == 12 and day == 31:
                    agents.newyearseve()
                if day <= 7 and weekday == 5:
                    agents.firstfriday()
                if day == 15:
                    agents.fiveteens()
        agents.panel_log(goods=['money'])
        agents.agg_log(goods=['labor'])
    simulation.finalize()


if __name__ == '__main__':
    main()
