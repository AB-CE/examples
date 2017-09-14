import abce
import random
import numpy as np
from optimization_functions import optimization
from copy import copy
from collections import defaultdict


class CentralBank(abce.Agent):
    def init(self, simulation_parameters, _):
        self.time_of_intervention = simulation_parameters['time_of_intervention']
        self.percentage_injection = simulation_parameters['percentage_injection']
        self.percentage_beneficiaries = simulation_parameters['percentage_beneficiaries']

    def intervention(self):
        if self.round == self.time_of_intervention:
            print('intervention', self.percentage_injection)
            messages = self.get_messages('grant')
            money_in_the_economy = sum([msg.content['money'] for msg in messages])
            injection = money_in_the_economy * self.percentage_injection
            beneficiaries = random.sample(messages, int(len(messages) * self.percentage_beneficiaries))
            money_beneficiaries = sum([beneficiary.content['money'] for beneficiary in beneficiaries])

            for msg in beneficiaries:
                self.create('money', injection)
                self.give(msg.sender,
                          good='money',
                          quantity=msg.content['money'] / money_beneficiaries * injection)

