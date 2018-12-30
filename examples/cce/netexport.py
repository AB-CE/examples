import abce
from abce import NotEnoughGoods


class NetExport(abce.Agent):
    def init(self):
        self.create('money', 0)

    def invest(self):
        offers_grouped = list(self.get_all_offers().values()) + list(self.get_all_bids().values())
        offers = []
        for os in offers_grouped:
            offers.extend(os)
        demand = sum([offer.quantity * offer.price for offer in offers if offer.sell])
        if demand < self['money']:
            self.rationing = rationing = 1
        else:
            self.rationing = rationing = self['money'] / demand

        for offer in offers:
            if not offer.sell:
                self.create(offer.good, offer.quantity)
                self.accept(offer)
            else:
                self.accept(offer, offer.quantity * rationing)

        self.give(('household', 0), quantity=self['money'], good='money')


