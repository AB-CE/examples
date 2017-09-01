import abce
from abce import NotEnoughGoods


class NetExport(abce.Agent):
    def init(self, _, __):
        self.create('money', 0)

    def invest(self):
        offers_grouped = self.get_offers_all().values()
        offers = []
        for os in offers_grouped:
            offers.extend(os)
        demand = sum([offer.quantity * offer.price for offer in offers if offer.buysell != 98])
        if demand < self.possession('money'):
            self.rationing = rationing = 1
        else:
            self.rationing = rationing = self.possession('money') / demand

        for offer in offers:
            if offer.buysell == 98:
                self.create(offer.good, offer.quantity)
                self.accept(offer)
            else:
                self.accept(offer, offer.quantity * rationing)

        self.give('household', 0, quantity=self.possession('money'), good='money')


