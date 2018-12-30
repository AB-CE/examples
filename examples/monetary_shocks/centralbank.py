import abcEconomics as abce
import random
from optimization_functions import optimization


class CentralBank(abce.Agent):
    def init(self, time_of_intervention, percentage_injection, percentage_beneficiaries):
        self.time_of_intervention = time_of_intervention
        self.percentage_injection = percentage_injection
        self.percentage_beneficiaries = percentage_beneficiaries

    def intervention(self):
        if self.time == self.time_of_intervention:
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
