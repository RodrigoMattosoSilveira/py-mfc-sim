# https://simpy.readthedocs.io/en/latest/simpy_intro/process_interaction.html

import simpy
import parameters


class Car(object):
    def __init__(self, env):
        self.env = env
        # Start the run process everytime an instance is created.
        self.action = env.process(self.run())

    def run(self):
        while True:
            print('Start parking at %d' % self.env.now)
            # We yield the process that process() returns to wait for it to finish
            yield self.env.process(self.charge(parameters.charge_duration))

            # The charge process has finished and # we can start driving again.
            print('Start driving at %d' % self.env.now)
            yield self.env.timeout(parameters.trip_duration)

    def charge(self, duration):
        print('Start charging at %d' % self.env.now)
        yield self.env.timeout(duration)


env = simpy.Environment()
car = Car(env)
env.run(until=parameters.simulation_duration)
