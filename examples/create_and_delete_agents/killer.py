from __future__ import division
import abce


class Killer(abce.Agent, abce.Household):
    def init(self):
        # your agent initialization goes here, not in __init__
        pass

    def kill_silent(self):
        agent_to_kill = self.round
        return agent_to_kill

    def kill_loud(self):
        agent_to_kill = self.round
        return agent_to_kill
