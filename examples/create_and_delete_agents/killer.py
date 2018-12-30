import abcEconomics as abce


class Killer(abce.Agent, abce.Household):
    def init(self):
        # your agent initialization goes here, not in __init__
        pass

    def kill_silent(self):
        agent_to_kill = ('victim', self.time)
        return agent_to_kill

    def kill_loud(self):
        agent_to_kill = ('loudvictim', self.time)
        return agent_to_kill
