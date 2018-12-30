import abcEconomics as abce


class Victim(abce.Agent, abce.Household):
    def init(self):
        # your agent initialization goes here, not in __init__
        self.count = 1
        self.idn = self.id

    def am_I_dead(self):
        if self.id < self.time:
            raise Exception("should be dead %i" % self.id)
