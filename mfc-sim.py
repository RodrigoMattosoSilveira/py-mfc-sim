# https://simpy.readthedocs.io/en/latest/simpy_intro/process_interaction.html

import simpy
import parameters


def car(obj_env):
    while True:
        print('Start parking at %d' % obj_env.now)
        # parking_duration = 5
        yield obj_env.timeout(parameters.parking_duration)

        print('Start driving at %d' % obj_env.now)
        # trip_duration = 2
        yield obj_env.timeout(parameters.trip_duration)


# The first thing we need to do is to create an instance of Environment.
# A simulation environment manages the simulation time as well as the scheduling and processing of events. It also
# provides means to step through or execute the simulation.
env = simpy.Environment()
env.process(car(env))
env.run(until=15)
