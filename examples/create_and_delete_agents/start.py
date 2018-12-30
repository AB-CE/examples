import abcEconomics as abce
from ball import Ball
from killer import Killer
from victim import Victim


rounds = num_victims = 30

simulation = abce.Simulation(processes=1)

print('build Killer')
killer = simulation.build_agents(Killer, 'killer', 1)
print('build Victim')
victims = simulation.build_agents(Victim, 'victim', num_victims)
print('build Victim loudvictim')
loudvictims = simulation.build_agents(Victim, 'loudvictim', num_victims)
print('build AddAgent')
balls = simulation.build_agents(Ball, 'ball', 0)

for time in range(rounds):
    simulation.advance_round(time)
    deads = killer.kill_silent()
    victims.delete_agents(deads)
    deads = killer.kill_loud()
    loudvictims.delete_agents(deads)
    victims.am_I_dead()
    loudvictims.am_I_dead()

    balls.create_agents(Ball, 1)

simulation.finalize()
