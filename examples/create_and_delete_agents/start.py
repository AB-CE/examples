import abcEconomics as abce
from ball import Ball
from killer import Killer
from victim import Victim

rounds = 30

simulation = abce.Simulation(processes=4)

print('build Killer')
killer = simulation.build_agents(Killer, 'killer', 1, parameters={'rounds': rounds})
print('build Victim')
victims = simulation.build_agents(Victim, 'victim', rounds, parameters={'rounds': rounds})
print('build Victim loudvictim')
loudvictims = simulation.build_agents(Victim, 'loudvictim', rounds, parameters={'rounds': rounds})
print('build AddAgent')
balls = simulation.build_agents(Ball, 'ball', 0)


for time in range(rounds):
    simulation.advance_round(time)
    deads = killer.kill_silent()
    for dead in deads:
        simulation.delete_agent(*dead)
    deads = killer.kill_loud()
    for dead in deads:
        simulation.delete_agent(*dead)
    killer.send_message()
    victims.am_I_dead()
    loudvictims.am_I_dead()
    simulation.create_agent(Ball, 'ball')
    balls.boing()

simulation.finalize()
