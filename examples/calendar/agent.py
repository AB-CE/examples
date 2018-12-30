import abcEconomics as abce


class Agent(abce.Agent):
    def init(self):
        # your agent initialization goes here, not in __init__
        pass

    def wednessday(self):
        print('wednessday')

    def first(self):
        print('first')
        self.create('money', 1000)

    def newyearseve(self):
        print('newyearseve')

    def firstfriday(self):
        print('drinks in museum')

    def fiveteens(self):
        print('fiveteens')

    def everythreedays(self):
        print(('            ', self.date(), self.date().weekday()))
