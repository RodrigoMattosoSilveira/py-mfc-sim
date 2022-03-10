import simpy
import Modules.my_random_normal as mrn
import secrets
import string


RANDOM_SEED = 42
NUM_MACHINES = 2  # Number of machines in the carwash
WASHTIME = 5      # Minutes it takes to clean a car
T_INTER = 7       # Create a car every ~7 minutes
SIM_TIME = 20     # Simulation time in minutes
INTER_ARRIVAL_TIME_MEAN = 10
INTER_ARRIVAL_TIME_SIGMA = 2.6


class PPP(object):
    """
    The PPP process (each ppp has a name) arrives at the order station (order_station), requests an order, fulfills the
    order and yells hooray
    """
    def __init__(self, _env, _name):
        self.env = env
        self.name = _name
        # Start the run process everytime an instance is created.
        self.action = _env.process(self.checkin())

    def checkin(self):
        while True:
            """
            The ppp checked in and is ready to start fulfilling orders
            """
            print('%s Start fulfilling orders at %d', self.name, self.env.now)
            yield self.env.process(self.order_station(self))

    @staticmethod
    def order_station(self):
        """
        An order station has an inter arrival time based on distribution, with a mean of 10 and a sigma of 2.6.

        A ppp has to request an order, wait for its inter arrival time and then proceed with fulfilling the order

        """
        print('%s enters the order station at %s.' % (name, env.now))
        iat = mrn.get_random_normal(INTER_ARRIVAL_TIME_MEAN, INTER_ARRIVAL_TIME_SIGMA)
        yield env.timeout(iat)
        print('%s got a fulfillment order at %s.' % (self.name, env.now))
        # simulate the time to fulfill an order
        time_to_fulfill_order = mrn.get_random_normal(170, 3);
        yield env.timeout(time_to_fulfill_order)
        print('%s fulfilled order att %s.' % (self.name, env.now))

env = simpy.Environment()
# using secrets.choices() to generate a random name
name = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for i in range(8))

ppp = PPP(env, name)
env.run(until=1000)
