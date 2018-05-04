""" A simulation of the first Model of Ernesto Carrella's paper:
Sticky Prices Microfoundations in a Agent Based Supply Chain
Section 4 Firms and Production

Here we have one firm and one market agent. The market agent
has the demand function q = 102 - p

"""
from firm import Firm
from market import Market
from abce import Simulation


s = Simulation()

firms = s.build_agents(Firm, 'firm', number=1)
market = s.build_agents(Market, 'market', number=1)
for r in range(3000):
    s.advance_round(r)
    firms.my_production()
    firms.selling()
    market.buying()
    firms.adjust_price()
    firms.adjust_quantity()
    market.consumption()
s.finalize()
