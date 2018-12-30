from myagent import MyAgent
from youragent import YourAgent
from abcEconomics import Simulation


def main():
    s = Simulation(processes=1)

    myagents = s.build_agents(MyAgent, 'myagent', 50000)
    youragents = s.build_agents(YourAgent, 'youragent', 50000)

    for r in range(100):
        print('Round: %i' % r)
        s.advance_round(r)
        # (myagents+youragents).do('compute')
        youragents.s()
        myagents.g()
    s.finalize()


if __name__ == '__main__':
    main()
