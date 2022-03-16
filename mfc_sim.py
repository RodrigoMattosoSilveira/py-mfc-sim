import simpy
import random
import Random.generators as rng
import Random.app_numbers as app_numbers
import Modules.ppp_shift_tally as ppp_shift_tally
import Modules.order_tally as order_tally
from Constants import parameters as params
from Constants import OrderStatus as orderStatus
import Modules.csv_file_handler as csv
import os
import threading


class PPP(object):
    """
    The PPP process (each ppp has a name) arrives at the order station (order_station), requests an order, fulfills the
    order and yells hooray
    """

    def __init__(self, _env):
        self.__env = _env
        self.__pppShiftTally = None
        self.__pppOrderTally = None
        self.__packingLocationResource = None
        self.__labelPrintersResource = None
        self.__orderTallyLog = None

    @property
    def env(self):
        return self.__env

    @env.setter
    def env(self, value):
        self.__env = value

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

    @property
    def packingLocationResource(self):
        return self.__packingLocationResource

    @packingLocationResource.setter
    def packingLocationResource(self, value):
        self.__packingLocationResource = value

    @property
    def labelPrintersResource(self):
        return self.__labelPrintersResource

    @labelPrintersResource.setter
    def labelPrintersResource(self, value):
        self.__labelPrintersResource = value

    @property
    def orderTallyLog(self):
        return self.__orderTallyLog

    @orderTallyLog.setter
    def orderTallyLog(self, value):
        self.__orderTallyLog = value

    def checkin(self, _env):
        # order_simulation_status = True
        while self.env.now <= params.SHIFT_WORK_DURATION:
            order_simulation_status = True

            self.pppOrderTally = None
            self.pppOrderTally = order_tally.OrderTally(self.pppShiftTally.pppId)
            self.show_bread_crumbs('Order fulfillment started')

            # get the order
            if order_simulation_status:
                order_simulation_status = yield self.env.process(self.order_station())

            # pick the order
            if order_simulation_status:
                order_simulation_status = yield self.env.process(self.inventory_station())

            # pack the order
            if order_simulation_status:
                order_simulation_status = yield self.env.process(self.packing_station())

            # label the order
            if order_simulation_status:
                order_simulation_status = yield self.env.process(self.labeling_station())

            # place the order at the courier status
            if order_simulation_status:
                order_simulation_status = yield self.env.process(self.courier_station())

            # place the order at the courier status
            if order_simulation_status:
                self.pppOrderTally.status = orderStatus.OrderStatus.Fulfilled.name

            # log
            self.print_order_stats()

            # Before handling a new order, check whether the PPP worked a full shift, enough to take a shift break
            break_time = 0
            if self.pppShiftTally.nextShiftBreak < _env.now < params.SHIFT_WORK_DURATION:
                # PPP is due for a shift break
                self.show_bread_crumbs('taking a %s seconds shift break' % params.SHIFT_BREAK_DURATION)
                yield self.env.timeout(params.SHIFT_BREAK_DURATION)
                self.pppShiftTally.nextShiftBreak += self.pppShiftTally.nextShiftBreak
                self.pppShiftTally.nextHourBreak = self.env.now + (3600 - params.HOUR_BREAK_DURATION)
                break_time = params.SHIFT_BREAK_DURATION
            else:
                if self.env.now > self.pppShiftTally.nextHourBreak:
                    # PPP is due for a shift break
                    self.show_bread_crumbs('taking a %s seconds hourly break' % params.HOUR_BREAK_DURATION)
                    yield self.env.timeout(params.HOUR_BREAK_DURATION)
                    self.pppShiftTally.nextHourBreak = self.env.now + (3600 - params.HOUR_BREAK_DURATION)
                    break_time = params.HOUR_BREAK_DURATION

            if break_time > 0:
                # Add a break orderTally
                self.pppOrderTally = None
                self.pppOrderTally = order_tally.OrderTally(self.pppShiftTally.pppId)
                self.pppOrderTally.breakTime = break_time
                self.pppOrderTally.workTime += break_time
                self.pppOrderTally.status = orderStatus.OrderStatus.Break.name
                self.pppShiftTally.workTime += break_time
                self.print_order_stats()

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
        simulation_status = True
        station_start = self.env.now

        self.show_bread_crumbs('starts walking to the order station at')
        _min = params.TIME_TO_WALK_TO_ORDER_STATION_MIN
        _max = params.TIME_TO_WALK_TO_ORDER_STATION_MAX
        time = random.randrange(_min, _max)
        yield self.env.timeout(time)
        self.show_bread_crumbs('arrives the order station at')

        # wait for an order
        time = rng.get_random_normal(params.INTER_ARRIVAL_TIME_MEAN, params.INTER_ARRIVAL_TIME_SIGMA)
        yield self.env.timeout(time)
        self.show_bread_crumbs('got a fulfillment order')

        # accumulate order station time
        self.show_bread_crumbs('leaving order station')
        station_time = self.env.now - station_start
        self.pppOrderTally.orderTime = station_time
        self.pppOrderTally.workTime += station_time
        self.pppShiftTally.workTime += station_time

        return simulation_status

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
        simulation_status = True
        station_start = self.env.now

        self.show_bread_crumbs('starts walking to the inventory station at')
        _min = params.TIME_TO_WALK_TO_INVENTORY_STATION_MIN
        _max = params.TIME_TO_WALK_TO_INVENTORY_STATION_MAX
        time = random.randrange(_min, _max)
        yield self.env.timeout(time)
        self.show_bread_crumbs('arrives the inventory station')

        # pick the order
        #  TODO replace this with the full simulation logic
        for i in range(1, self.pppOrderTally.items + 1):
            self.show_bread_crumbs('Picking order item #%s' % i)
            if i > 0:
                # walk to pick the next item
                _min = params.TIME_TO_WALK_TO_PICK_NEXT_ITEM_MIN
                _max = params.TIME_TO_WALK_TO_PICK_NEXT_ITEM_MAX
                time = random.randrange(_min, _max)
                yield self.env.timeout(time)

            # Interrupt the process of we do not have inventory
            # TODO Review this with someone who understands this better than I do!
            if app_numbers.get_random_sku_qtd() == 0:
                self.show_bread_crumbs(orderStatus.OrderStatus.Out_Of_Stock.name)
                self.pppOrderTally.status = orderStatus.OrderStatus.Out_Of_Stock.name
                simulation_status = False
            else:
                _min = params.TIME_TO_PICK_ITEM_MIN
                _max = params.TIME_TO_PICK_ITEM_MAX
                time = random.randrange(_min, _max)
                yield self.env.timeout(time)
            if not simulation_status:
                break

        # accumulate inventory station time
        self.show_bread_crumbs('leaving pick station')
        station_time = self.env.now - station_start
        self.pppOrderTally.pickTime = station_time
        self.pppOrderTally.workTime += station_time
        self.pppShiftTally.workTime += station_time

        return simulation_status

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
        simulation_status = True
        station_start = self.env.now

        self.show_bread_crumbs('starts walking to the packing station')
        _min = params.TIME_TO_WALK_TO_PACKING_STATION_MIN
        _max = params.TIME_TO_WALK_TO_PACKING_STATION_MAX
        time = random.randrange(_min, _max)
        yield self.env.timeout(time)
        self.show_bread_crumbs('arrives the packing station')

        # pack the order
        with self.packingLocationResource.request() as req:
            yield req

            if app_numbers.get_random_packing_resources_qtd() == 0:
                self.show_bread_crumbs(orderStatus.OrderStatus.Out_Of_Packing_Resources.name)
                self.pppOrderTally.status = orderStatus.OrderStatus.Out_Of_Packing_Resources.name
                simulation_status = False
            else:
                _min = params.TIME_TO_PACK_ORDER_MIN
                _max = params.TIME_TO_PACK_ORDER_MAX
                time = random.randrange(_min, _max)
                yield self.env.timeout(time)
                self.show_bread_crumbs('packed the order items')

        # accumulate  packing station time
        self.show_bread_crumbs('leaving pack station')
        station_time = self.env.now - station_start
        self.pppOrderTally.packTime = station_time
        self.pppOrderTally.workTime += station_time
        self.pppShiftTally.workTime += station_time

        return simulation_status

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
        simulation_status = True
        station_start = self.env.now

        self.show_bread_crumbs('starts walking to the labeling station')
        _min = params.TIME_TO_WALK_TO_LABELING_STATION_MIN
        _max = params.TIME_TO_WALK_TO_LABELING_STATION_MAX
        time = random.randrange(_min, _max)
        yield self.env.timeout(time)
        self.show_bread_crumbs('arrived at the labeling station')

        # label the order
        with self.labelPrintersResource.request() as req:
            yield req
            if app_numbers.get_random_labeling_resources_qtd() == 0:
                self.show_bread_crumbs(orderStatus.OrderStatus.Out_Of_Labeling_Resources.name)
                self.pppOrderTally.status = orderStatus.OrderStatus.Out_Of_Labeling_Resources.name
                simulation_status = False
            else:
                _min = params.TIME_TO_LABEL_ORDER_MIN
                _max = params.TIME_TO_LABEL_ORDER_MAX
                time = random.randrange(_min, _max)
                yield self.env.timeout(time)
                self.show_bread_crumbs('labeled the order items')

        # accumulate  labeling station time
        self.show_bread_crumbs('leaving labeling station')
        station_time = self.env.now - station_start
        self.pppOrderTally.labelTime = station_time
        self.pppOrderTally.workTime += station_time
        self.pppShiftTally.workTime += station_time

        return simulation_status

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
        simulation_status = True
        station_start = self.env.now

        self.show_bread_crumbs('starts walking to the courier station')
        _min = params.TIME_TO_WALK_TO_COURIER_STATION_MIN
        _max = params.TIME_TO_WALK_TO_COURIER_STATION_MAX
        time = random.randrange(_min, _max)
        yield self.env.timeout(time)
        self.show_bread_crumbs('arrives the courier station')

        # label the order
        #  TODO replace this with the full simulation logic
        _min = params.TIME_TO_PLACE_ORDER_AT_COURIER_STATION_MIN
        _max = params.TIME_TO_PLACE_ORDER_AT_COURIER_STATION_MAX
        time = random.randrange(_min, _max)
        yield self.env.timeout(time)
        self.show_bread_crumbs('placed the order at the courier station')

        # accumulate  courier station time
        station_time = self.env.now - station_start
        self.pppOrderTally.courierTime = station_time
        self.pppOrderTally.workTime += station_time
        self.pppShiftTally.workTime += station_time
        self.pppShiftTally.orders += 1

        return simulation_status

    def show_bread_crumbs(self, detail):
        print('%s %s %s at %s' % (self.pppShiftTally.pppId, self.pppOrderTally.orderId, detail, self.env.now))

    def print_order_stats(self):
        # print
        print('%s, %s, %s, %s, %s, %s, %s, %s, %s %s %s %a\n' % (
            self.pppShiftTally.pppId,
            self.pppOrderTally.orderId,
            self.pppOrderTally.items,
            self.pppOrderTally.orderTime,
            self.pppOrderTally.pickTime,
            self.pppOrderTally.packTime,
            self.pppOrderTally.labelTime,
            self.pppOrderTally.courierTime,
            self.pppOrderTally.breakTime,
            self.pppOrderTally.workTime,
            self.pppShiftTally.workTime,
            self.pppOrderTally.status))
        # log
        list_array = [self.pppShiftTally.pppId, self.pppOrderTally.orderId, self.pppOrderTally.items,
                      self.pppOrderTally.orderTime, self.pppOrderTally.pickTime, self.pppOrderTally.packTime,
                      self.pppOrderTally.labelTime, self.pppOrderTally.courierTime,  self.pppOrderTally.breakTime,
                      self.pppOrderTally.workTime,
                      self.pppOrderTally.status]
        self.orderTallyLog.write(list_array)


"""
See https://simpy.readthedocs.io/en/latest/simpy_intro/shared_resources.html
We will use one environment to simulate a MFC shift's work
    Will will create the resources required to run the simulation
        Inventory pick slots
        Inventory skus
        Packing boxes
        Shipping labels
        Label printer
        Couriers' delivery slots
    We will simulate one or more PPP order fulfillment work
        We will use a OrderSimulator to simulate a PPP order fulfillment for a PPPs whole shift
            PppShiftTally - The OrderSimulator uses it to collect the each PPP's shift data
            OrderTally - The OrderSimulator uses it to collect each order's fulfillment data
"""

# Set up the simulation
simulation_environment = simpy.Environment()
# one for the whole simulation
packingLocationResource = simpy.Resource(simulation_environment, capacity=params.PACKING_LOCATIONS)
# one for the whole simulation
labelPrintersResource = simpy.Resource(simulation_environment, capacity=params.LABEL_PRINTERS)

# TODO move this to its own orderTallyLog package / class
if os.path.isfile(params.ORDER_TALLY_LOG):
    os.remove(params.ORDER_TALLY_LOG)
orderTallyLogLock = threading.Lock()
orderTallyLog = csv.CSV(params.ORDER_TALLY_LOG, orderTallyLogLock)
orderTallyLog.open()
header = ['pppId', 'orderId', 'items', 'orderTime', 'pickTime', 'packTime', 'labelTime', 'courierTime', 'breakTime',
          'totalOrderTime', 'status']
orderTallyLog.write(header)

for i in range(params.NUMBER_OF_PPP):
    ppp = PPP(simulation_environment)
    ppp.pppShiftTally = ppp_shift_tally.PppShiftTally()  # set PPP's tally
    ppp.orderTallyLog = orderTallyLog  # set simulation CSV file
    ppp.packingLocationResource = packingLocationResource  # set simulation Packing Location Resource
    ppp.labelPrintersResource = labelPrintersResource  # set simulation Label Printer Resource
    ppp_process = simulation_environment.process(ppp.checkin(simulation_environment))

# Run the simulation
simulation_environment.run()
orderTallyLog.close()
