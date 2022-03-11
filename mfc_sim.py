import simpy
import random
import random_numbers.my_random_calculators as mrn
import Modules.ppp_shift_tally as ppp_shift_tally
import Modules.order_tally as order_tally
import secrets
import string
import parameters as params


class PPP(object):
    """
    The PPP process (each ppp has a name) arrives at the order station (order_station), requests an order, fulfills the
    order and yells hooray
    """

    def __init__(self, _env, _ppp_shift_tally):
        self.env = env
        self.__pppShiftTally = _ppp_shift_tally
        self.__pppOrderTally = None

        # Start the run process everytime an instance is created.
        self.action = _env.process(self.checkin())

    @property
    def pppShiftTally(self):
        return self.__pppShiftTally

    @pppShiftTally.setter
    def pppShiftTally(self, value):
        self.__pppShiftTally = value

    @property
    def pppOrderTally(self):
        return self.__pppOrderTally

    @pppOrderTally.setter
    def pppOrderTally(self, value):
        self.__pppOrderTally = value

    def checkin(self):
        while True:
            """
            The ppp checked in and is ready to start fulfilling orders
            """
            print('%s Start fulfilling orders at %d' % (self.pppShiftTally.pppId, self.env.now))

            # save the existing order tally, and create a new one
            if self.pppOrderTally is not None:
                # fulfilled the order
                print('%s fulfilled order at %s' % (self.pppShiftTally.pppId, env.now))
                print('%s, %s, %s, %s, %s, %s, %s' % (self.pppOrderTally.items,
                                                        self.pppOrderTally.orderTime,
                                                        self.pppOrderTally.pickTime,
                                                        self.pppOrderTally.packTime,
                                                        self.pppOrderTally.labelTime,
                                                        self.pppOrderTally.courierTime,
                                                        self.pppOrderTally.workTime))
                print('Accumulated work time: %s\n' % self.pppShiftTally.workTime)
                self.pppOrderTally = None

            self.pppOrderTally = order_tally.OrderTally(pppShiftTally.pppId)
            yield self.env.process(self.order_station(self))

    @staticmethod
    def order_station(self):
        """
        An order station has an inter arrival time based on distribution, with a mean of 10 and a sigma of 2.6.

        A ppp has to request an order, wait for its inter arrival time and then proceed with fulfilling the order

        - Travel to - We will model travel to the order station by selecting from an uniform distribution, based on the
        average time to travel to the inventory station;
        - Shift End - We will end the iteration simulation after the PPP works a configurable number shift hours;
        - Shift Break - We will insert a 1 hour shift break after a PPP works 4 hours; in this case we will not have the
        hourly break;
        - Hourly Break - We will insert a 5 minutes hourly break after a PPP works 55 minutes;
        - Order Inter Arrival Time - This varies based on the time of the day, day of the month, and season. We will
        start with a simple model, by selecting from uniform distribution, based on on the average order interarrival
        time;
        """
        # start counting order station time
        station_start = env.now

        print('%s starts walking to the order station at %s.' % (name, env.now))
        _min = params.TIME_TO_WALK_TO_ORDER_STATION_MIN
        _max = params.TIME_TO_WALK_TO_ORDER_STATION_MAX
        time = random.randrange(_min, _max)
        yield env.timeout(time)
        print('%s arrives the order station at %s.' % (name, env.now))

        # wait for an order
        time = mrn.get_random_normal(params.INTER_ARRIVAL_TIME_MEAN, params.INTER_ARRIVAL_TIME_SIGMA)
        yield env.timeout(time)
        print('%s got a fulfillment order at %s.' % (self.pppShiftTally.pppId, env.now))

        # accumulate order station time
        station_time = env.now - station_start
        self.pppOrderTally.orderTime = station_time
        self.pppOrderTally.workTime += station_time
        self.pppShiftTally.workTime += station_time

        # go pick, pack, label, and set the order
        yield self.env.process(self.inventory_station(self))

    @staticmethod
    def inventory_station(self):
        """
        - Travel to - We will model travel to the inventory station by selecting from an uniform distribution, based on
        the average time to travel to the inventory station;
        - Inventory Pick Location Utilization - Our model will ensure that two PPPs do not attempt to pick at the same
        inventory pick location simultaneously; we will model inventory location utilization by: i) using a Resource
        object modeling the 1,500 MFC pick locations, ii) selecting the order line pick location from a from a poisson
        distribution that favors the first 150 of the MFCs 1,500 pick locations;
            - When two PPPs , attempt to pick from the same pick location simultaneously, our model will wait until the
            first PPP finishes picking;
        - Inventory Availability - We will model SKU availability by selecting a random value from a distribution that
        yields a very high probability that the SKU is available;
            - when an SKU is not available, the model will transition the PPP back to the order station, count the time
            until that point in time, without incrementing the number of fulfilled orders;
        - Picking Time - We will model the PPP order line item pick time by selecting a random value from an uniform
        distributions based on the average pick time;
        """
        # start counting inventory station time
        station_start = env.now

        print('%s starts walking to the inventory station at %s' % (name, env.now))
        _min = params.TIME_TO_WALK_TO_INVENTORY_STATION_MIN
        _max = params.TIME_TO_WALK_TO_INVENTORY_STATION_MAX
        time = random.randrange(_min, _max)
        yield env.timeout(time)
        print('%s arrives the inventory station at %s.' % (name, env.now))

        # pick the order
        #  TODO replace this with the full simulation logic
        _min = params.TIME_TO_PICK_ITEM_MIN
        _max = params.TIME_TO_PICK_ITEM_MAX
        time = random.randrange(_min, _max)
        yield env.timeout(time)
        print('%s picked the order inventory items %s' % (self.pppShiftTally.pppId, env.now))

        # accumulate inventory station time
        station_time = env.now - station_start
        self.pppOrderTally.pickTime = station_time
        self.pppOrderTally.workTime += station_time
        self.pppShiftTally.workTime += station_time

        # go pack, label, and set the order
        yield self.env.process(self.packing_station(self))

    @staticmethod
    def packing_station(self):
        """
            - Travel to - We will model travel to the packing station by selecting from an uniform distribution, based
            on the average time to travel to the pack station;
            - Packing Resources Location Availability - Our model will ensure that two PPP do not attempt to retrieve
            the packing resources for the same SKU simultaneously; we will model packing resource location availability
            by selecting a random value from an uniform distributions that yields  a very high packing resource location
            availability probability;
                - When two PPPs , attempt to retrieve packing resources for the same SKU simultaneously, our model will
                wait until the first PPP finishes retrieving;
            - Packing Resources Availability - we will model Packing Resources availability by selecting a random value
            from a distribution that yields  a very high probability that the packing resources are available;
                - The model will transition the PPP back to the order station when an order's packing resources are not
                available, count the time, but not the number of fulfilled orders;
            - Packing Resources Retrieval Time - We will model it by selecting from an uniform distribution, based on
            the average time to retrieve package resources;
            - Packing - We will model the time for the PPPs to pack their orders by selecting from an uniform
            distribution, based on the average time to pack an order;
        """
        # start counting packing station time
        station_start = env.now

        print('%s starts walking to the packing station at %s.' % (name, env.now))
        _min = params.TIME_TO_WALK_TO_PACKING_STATION_MIN
        _max = params.TIME_TO_WALK_TO_PACKING_STATION_MAX
        time = random.randrange(_min, _max)
        yield env.timeout(time)
        print('%s arrives the packing station at %s' % (name, env.now))

        # pack the order
        #  TODO replace this with the full simulation logic
        _min = params.TIME_TO_PACK_ORDER_MIN
        _max = params.TIME_TO_PACK_ORDER_MAX
        time = random.randrange(_min, _max)
        yield env.timeout(time)
        print('%s picked the order items %s' % (self.pppShiftTally.pppId, env.now))

        # accumulate  packing station time
        station_time = env.now - station_start
        self.pppOrderTally.packTime = station_time
        self.pppOrderTally.workTime += station_time
        self.pppShiftTally.workTime += station_time

        # go pack, label, and set the order
        yield self.env.process(self.labeling_station(self))

    @staticmethod
    def labeling_station(self):
        """
            - Travel to - We will model travel to the labeling station by selecting from an uniform distribution, based
            on the average time to travel to the labeling station;
            - Print Label Location Availability - Our model will ensure that two PPP do not attempt to print their
            orders' labels simultaneously; we will model print label location availability by selecting a random value
            from a distributions that yields a very high print label location availability probability;
                - When two PPPs , attempt to print labels simultaneously, our model will wait until the first PPP
                finishes printing;
            - Print Label  Resources Availability - we will model Print Label Resources availability by selecting a
            random value from a distribution that yields a very high probability that the print label resources are
            available;
                - The model will transition the PPP back to the order station when an order's print labels are not
                available, count the time, but not the number of fulfilled orders;
            - Print Label Time - We will model it by selecting from an uniform distribution, based on the average time
            to print a label;
            - Labeling - We will model the PPPs labeling time by selecting from an uniform distribution, based on the
            average time to label an order;
        """
        # start counting labeling station time
        station_start = env.now

        print('%s starts walking to the labeling station at %s.' % (name, env.now))
        _min = params.TIME_TO_WALK_TO_LABELING_STATION_MIN
        _max = params.TIME_TO_WALK_TO_LABELING_STATION_MAX
        time = random.randrange(_min, _max)
        yield env.timeout(time)
        print('%s arrives the labeling station at %s' % (name, env.now))

        # label the order
        #  TODO replace this with the full simulation logic
        _min = params.TIME_TO_LABEL_ORDER_MIN
        _max = params.TIME_TO_LABEL_ORDER_MAX
        time = random.randrange(_min, _max)
        yield env.timeout(time)
        print('%s labeled the order items %s' % (self.pppShiftTally.pppId, env.now))

        # accumulate  labeling station time
        station_time = env.now - station_start
        self.pppOrderTally.labelTime = station_time
        self.pppOrderTally.workTime += station_time
        self.pppShiftTally.workTime += station_time

        # go pack, label, and set the order
        yield self.env.process(self.courier_station(self))

    @staticmethod
    def courier_station(self):
        """
            - Travel to - We will model travel to the courier station by selecting from an uniform distribution, based
            on the average time to travel to the courier station;
            - Courier Station Location Availability - Our model will ensure that two PPPs do not attempt to place their
            orders' at the courier station simultaneously; we will model courier location availability by selecting a
            random value from a distributions that yields a very high courier location availability probability;
                - When two PPPs attempt place their orders' at the courier station simultaneously, our model will
                wait until the first PPP finishes tp place their order;
            - Placing Order - We will model the PPPs placing their orders' at the courier station by selecting from an
            uniform distribution, based on the average time to place an order;
        """
        # start counting courier station time
        station_start = env.now

        print('%s starts walking to the courier station at %s.' % (name, env.now))
        _min = params.TIME_TO_WALK_TO_COURIER_STATION_MIN
        _max = params.TIME_TO_WALK_TO_COURIER_STATION_MAX
        time = random.randrange(_min, _max)
        yield env.timeout(time)
        print('%s arrives the courier station at %s.' % (name, env.now))

        # label the order
        #  TODO replace this with the full simulation logic
        _min = params.TIME_TO_PLACE_ORDER_AT_COURIER_STATION_MIN
        _max = params.TIME_TO_PLACE_ORDER_AT_COURIER_STATION_MAX
        time = random.randrange(_min, _max)
        yield env.timeout(time)
        print('%s placed the order at the courier station %s' % (self.pppShiftTally.pppId, env.now))

        # accumulate  courier station time
        station_time = env.now - station_start
        self.pppOrderTally.courierTime = station_time
        self.pppOrderTally.workTime += station_time
        self.pppShiftTally.workTime += station_time

        # Done with this order, go handle the next order


"""
See https://simpy.readthedocs.io/en/latest/simpy_intro/shared_resources.html
We will use one environment to simulate a MFC shift's work
    Will will create the resources required to run the simulation
        Inventory pick slots
        Inventory skus
        Packing boxes
        Shipping labels
        Label printer
        Couries delivery slots
    We will simulate one or more PPP order fulfillment work
        We will use a OrderSimulator to simulate a PPP order fulfillment for a PPPs whole shift
            PppShiftTally - The OrderSimulator uses it to collect the each PPP's shift data
            OrderTally - The OrderSimulator uses it to collect each order's fulfillment data
"""

env = simpy.Environment()
# using secrets.choices() to generate a random name
name = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for i in range(8))

# get the tracking objects and simulate our process
pppShiftTally = ppp_shift_tally.PppShiftTally()
orderTally = order_tally.OrderTally(pppShiftTally.pppId)
ppp = PPP(env, pppShiftTally)
# TODO end with an event, triggered after the PPP fulfill an order and the ppp work time exceeds the shift work time
env.run(until=1000)
