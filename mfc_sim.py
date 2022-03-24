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
from math import trunc


class PPP(object):
    """
    The PPP process (each ppp has a name) arrives at the order station (order_area), requests an order, fulfills the
    order and yells hooray
    """

    def __init__(self, _env):
        self.__env = _env
        self.__pppShiftTally = None
        self.__pppOrderTally = None
        self.__orderTabletResource = None
        self.__packingLocationResource = None
        self.__labelPrintersResource = None
        self.__orderTallyLog = None
        self.__pppActivityLog = None

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
    def orderTabletResource(self):
        return self.__orderTabletResource

    @orderTabletResource.setter
    def orderTabletResource(self, value):
        self.__orderTabletResource = value

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

    @property
    def pppActivityLog(self):
        return self.__pppActivityLog

    @pppActivityLog.setter
    def pppActivityLog(self, value):
        self.__pppActivityLog = value

    def checkin(self, _env):
        workflow = [
            self.order_area,
            self.pick_area,
            self.pack_area,
            self.label_area,
            self.deliver_area
        ]

        # do these only once
        yield self.env.process(self.cleaning_receiving())
        yield self.env.process(self.cycle_count())
        yield self.env.process(self.parcel_level_scanning())

        # Now fulfill orders
        while self.env.now <= params.SHIFT_WORK_DURATION:
            self.show_bread_crumbs('Order fulfillment started')

            #  Refactored based on Eric's "code review"
            for step in workflow:
                if not (yield self.env.process(step())):
                    break

            # record the order fulfillment stats at the end of the journey
            yield self.env.process(self.record_order_fulfillment_stats())

            # log results
            self.print_order_stats()

            # # Before handling a new order, check whether the PPP worked a full shift, enough to take a shift break
            yield self.env.process(self.break_time())

    def record_order_fulfillment_stats(self):
        # record the order fulfillment stats at the end of the journey
        station_start = self.env.now
        with self.orderTabletResource.request() as _order_tablet:
            # request tablet
            self.show_bread_crumbs('start waiting for tablet')
            yield _order_tablet
            self.show_bread_crumbs('done waiting for tablet')

        # got tablet, record the order stats
        self.show_bread_crumbs('start recording the order stats')
        _min = params.TIME_TO_RECORD_ORDER_STATS_MIN
        _max = params.TIME_TO_RECORD_ORDER_STATS_MAX
        time = random.randrange(_min, _max)
        yield self.env.timeout(time)
        self.show_bread_crumbs(' done recording the order stats')

        station_time = self.env.now - station_start
        self.pppOrderTally.orderTime = station_time
        self.pppOrderTally.workTime += station_time
        self.pppShiftTally.workTime += station_time

    def break_time(self):
        # Before handling a new order, check whether the PPP worked a full shift, enough to take a shift break
        # start counting  cleaning receiving area time
        break_duration = 0
        if self.pppShiftTally.nextShiftBreak < self.env.now < params.SHIFT_WORK_DURATION:
            # PPP is due for a shift break
            self.show_bread_crumbs('taking a %s seconds shift break' % params.SHIFT_BREAK_DURATION)
            yield self.env.timeout(params.SHIFT_BREAK_DURATION)
            self.pppShiftTally.nextShiftBreak += self.pppShiftTally.nextShiftBreak
            self.pppShiftTally.nextHourBreak = self.env.now + (3600 - params.HOUR_BREAK_DURATION)
            break_duration = params.SHIFT_BREAK_DURATION
        else:
            if self.env.now > self.pppShiftTally.nextHourBreak:
                # PPP is due for a shift break
                self.show_bread_crumbs('taking a %s seconds hourly break' % params.HOUR_BREAK_DURATION)
                yield self.env.timeout(params.HOUR_BREAK_DURATION)
                self.pppShiftTally.nextHourBreak = self.env.now + (3600 - params.HOUR_BREAK_DURATION)
                break_duration = params.HOUR_BREAK_DURATION

        if break_duration > 0:
            # Add a break orderTally
            self.pppOrderTally = None
            self.pppOrderTally = order_tally.OrderTally(self.pppShiftTally.pppId)
            self.pppOrderTally.breakTime = break_duration
            self.pppOrderTally.workTime += break_duration
            self.pppOrderTally.status = orderStatus.OrderStatus.Break.name
            self.pppShiftTally.workTime += break_duration
            self.print_order_stats()

        return True

    def cleaning_receiving(self):
        # start counting  cleaning receiving area time
        simulation_status = True
        station_start = self.env.now

        self.pppOrderTally = None
        self.pppOrderTally = order_tally.OrderTally(self.pppShiftTally.pppId)

        # Simulate cleaning receiving
        self.show_bread_crumbs('Starting cleaning receiving')
        area_time = trunc(params.SHIFT_WORK_DURATION * params.CLEANING_RECEIVING_SHIFT_PERCENT_ALLOCATION)
        yield self.env.timeout(area_time)
        self.show_bread_crumbs('Stop cleaning receiving')
        station_time = self.env.now - station_start

        self.pppOrderTally.cleaningReceivingTime = station_time
        self.pppOrderTally.workTime += station_time
        self.pppOrderTally.status = orderStatus.OrderStatus.CR.name
        self.pppShiftTally.workTime += station_time
        self.print_order_stats()

        return simulation_status

    def cycle_count(self):
        # start counting  cycle count time
        simulation_status = True
        station_start = self.env.now

        self.pppOrderTally = None
        self.pppOrderTally = order_tally.OrderTally(self.pppShiftTally.pppId)

        # Simulate cycle counting
        self.show_bread_crumbs('Starting cycle counting')
        area_time = trunc(params.SHIFT_WORK_DURATION * params.CYCLE_COUNT_SHIFT_PERCENT_ALLOCATION)
        yield self.env.timeout(area_time)
        self.show_bread_crumbs('Stop cycle counting')
        station_time = self.env.now - station_start

        self.pppOrderTally.cleaningReceivingTime = station_time
        self.pppOrderTally.workTime += station_time
        self.pppOrderTally.status = orderStatus.OrderStatus.CC.name
        self.pppShiftTally.workTime += station_time
        self.print_order_stats()

        return simulation_status

    def parcel_level_scanning(self):
        # start counting  parcel level scanning time
        simulation_status = True
        station_start = self.env.now

        self.pppOrderTally = None
        self.pppOrderTally = order_tally.OrderTally(self.pppShiftTally.pppId)

        # Simulate cycle counting
        self.show_bread_crumbs('Starting parcel level scanning')
        area_time = trunc(params.SHIFT_WORK_DURATION * params.CYCLE_COUNT_SHIFT_PERCENT_ALLOCATION)
        yield self.env.timeout(area_time)
        self.show_bread_crumbs('Stop parcel level scanning')
        station_time = self.env.now - station_start

        self.pppOrderTally.parcelLevelScanningTime = station_time
        self.pppOrderTally.workTime += station_time
        self.pppOrderTally.status = orderStatus.OrderStatus.PLS.name
        self.pppShiftTally.workTime += station_time
        self.print_order_stats()

        return simulation_status

    def order_area(self):
        # start counting order area time
        simulation_status = True
        station_start = self.env.now

        self.show_bread_crumbs('starts walking to the order station at')
        _min = params.TIME_TO_WALK_TO_ORDER_STATION_MIN
        _max = params.TIME_TO_WALK_TO_ORDER_STATION_MAX
        time = random.randrange(_min, _max)
        yield self.env.timeout(time)
        self.show_bread_crumbs('arrives the order station at')

        # got tablet, read and memorize the order
        with self.orderTabletResource.request() as _order_tablet_1:
            # request tablet
            self.show_bread_crumbs('start waiting for tablet')
            yield _order_tablet_1
            self.show_bread_crumbs('done waiting for tablet')

        # wait for an order
        self.show_bread_crumbs('start waiting for an order')
        time = rng.get_random_normal(params.ORDER_INTER_ARRIVAL_TIME_MEAN, params.ORDER_INTER_ARRIVAL_TIME_SIGMA)
        yield self.env.timeout(time)
        self.show_bread_crumbs('done waiting for an order')

        self.show_bread_crumbs('start memorizing the order')
        _min = params.TIME_TO_RECORD_ORDER_STATS_MIN
        _max = params.TIME_TO_RECORD_ORDER_STATS_MAX
        time = random.randrange(_min, _max)
        yield self.env.timeout(time)
        self.show_bread_crumbs('done memorizing the order')

        # get an order tally
        self.pppOrderTally = None
        self.pppOrderTally = order_tally.OrderTally(self.pppShiftTally.pppId)

        # Randomize Rush/SameDay or NextDay/National and number og items
        self.pppOrderTally.orderType = app_numbers.is_order_rush_next_day()
        if self.pppOrderTally.orderType == params.ORDER_TYPE_RUSH:
            # Rush and same day orders have 1 item
            # TODO Really?
            self.pppOrderTally.items = 1
            self.pppOrderTally.numberOfBoxes = 1
        else:
            self.pppOrderTally.items = app_numbers.get_random_order_items()
            self.pppOrderTally.numberOfBoxes = 1
            if self.pppOrderTally.items > 6:
                self.pppOrderTally.numberOfBoxes = 2

        # get the package containers
        self.show_bread_crumbs('starts walking to retrieve package containers')
        _min = params.TIME_TO_WALK_TO_PACK_STATION_MIN
        _max = params.TIME_TO_WALK_TO_PACK_STATION_MAX
        time = random.randrange(_min, _max)
        yield self.env.timeout(time)
        self.show_bread_crumbs('done walking to retrieve package containers')

        if self.pppOrderTally.orderType == params.ORDER_TYPE_NATIONAL:
            if not app_numbers.got_package_containers():
                # did not find a package container, abort this order fulfillment
                self.show_bread_crumbs(orderStatus.OrderStatus.OOP.name)
                self.pppOrderTally.status = orderStatus.OrderStatus.OOP.name
                simulation_status = False

        # accumulate order station time
        self.show_bread_crumbs('leaving order station')
        station_time = self.env.now - station_start
        self.pppOrderTally.orderTime = station_time
        self.pppOrderTally.workTime += station_time
        self.pppShiftTally.workTime += station_time

        return simulation_status

    def pick_area(self):
        # start counting packing station time
        simulation_status = True
        station_start = self.env.now

        items_on_hand = 0
        max_items_in_container = 1
        if self.pppOrderTally.orderType == params.ORDER_TYPE_NATIONAL:
            max_items_in_container = 1
        total_parcels = 0
        for k in range(self.pppOrderTally.items):
            # go to pick slot location
            self.show_bread_crumbs('picking item #%s' % k)
            self.show_bread_crumbs('walk to the pick slot location')
            _min = params.TIME_TO_WALK_TO_PICK_STATION_MIN
            _max = params.TIME_TO_WALK_TO_PICK_STATION_MAX
            time = random.randrange(_min, _max)
            yield self.env.timeout(time)
            self.show_bread_crumbs('arrives the the pick slot location')
            if app_numbers.get_random_sku_qtd() == 0:
                self.show_bread_crumbs('item is OOS')
                self.show_bread_crumbs(orderStatus.OrderStatus.OOS.name)
                self.pppOrderTally.status = orderStatus.OrderStatus.OOS.name
                simulation_status = False
                break
            else:
                # pick the item
                self.show_bread_crumbs('starts picking item')
                _min = params.TIME_TO_PICK_ITEM_MIN
                _max = params.TIME_TO_PICK_ITEM_MAX
                time = random.randrange(_min, _max)
                yield self.env.timeout(time)
                self.show_bread_crumbs('done picking item')
                # return to the table
                self.show_bread_crumbs('walk to the table')
                _min = params.TIME_TO_WALK_TO_PICK_STATION_MIN
                _max = params.TIME_TO_WALK_TO_PICK_STATION_MAX
                time = random.randrange(_min, _max)
                yield self.env.timeout(time)
                self.show_bread_crumbs('arrives at the table')
                # place item in container
                self.show_bread_crumbs('place item in container')
                _min = params.TIME_TO_PLACE_ITEM_IN_CONTAINER_MIN
                _max = params.TIME_TO_PLACE_ITEM_IN_CONTAINER_MAX
                time = random.randrange(_min, _max)
                yield self.env.timeout(time)
                self.show_bread_crumbs('placed item in container')
                items_on_hand += 1
                # take container to the outbound box shelf area, if full
                if items_on_hand == max_items_in_container:
                    total_parcels += 1
                    # take container to the outbound box shelf area
                    self.show_bread_crumbs('container is full')
                    self.show_bread_crumbs('walk to outbound box shelf area')
                    _min = params.TIME_TO_WALK_TO_OUTBOUND_SHELF_AREA_MIN
                    _max = params.TIME_TO_WALK_TO_OUTBOUND_SHELF_AREA_MAX
                    time = random.randrange(_min, _max)
                    yield self.env.timeout(time)
                    self.show_bread_crumbs('walked to outbound box shelf area')
                    # place container at outbound box shelf
                    self.show_bread_crumbs('place container on outbound box shelf area')
                    _min = params.TIME_TO_PLACE_CONTAINER_ON_OUTBOUND_SHELF_MIN
                    _max = params.TIME_TO_PLACE_CONTAINER_ON_OUTBOUND_SHELF_MAX
                    time = random.randrange(_min, _max)
                    yield self.env.timeout(time)
                    self.show_bread_crumbs('placed container on outbound box shelf area')
                    items_on_hand = 0
                    if k == self.pppOrderTally.items:
                        self.show_bread_crumbs('finished picking while at outbound box shelf area, stay there!')
                        break
        # If simulation_status = False, restock the items in hand, and the one in the outbound shelf containers
        if not simulation_status:
            yield self.env.process(self.restock_items())
        else:
            if items_on_hand > 0:
                # take container to the outbound box shelf area
                self.show_bread_crumbs('walk to outbound box shelf area')
                _min = params.TIME_TO_WALK_TO_OUTBOUND_SHELF_AREA_MIN
                _max = params.TIME_TO_WALK_TO_OUTBOUND_SHELF_AREA_MAX
                time = random.randrange(_min, _max)
                yield self.env.timeout(time)
                self.show_bread_crumbs('walked to outbound box shelf area')
                # place container at outbound box shelf
                self.show_bread_crumbs('placing container on outbound box shelf area')
                _min = params.TIME_TO_PLACE_CONTAINER_ON_OUTBOUND_SHELF_MIN
                _max = params.TIME_TO_PLACE_CONTAINER_ON_OUTBOUND_SHELF_MAX
                time = random.randrange(_min, _max)
                yield self.env.timeout(time)
                self.show_bread_crumbs('placed container on outbound box shelf area')

        # accumulate pick time
        self.show_bread_crumbs('leaving pack station')
        station_time = self.env.now - station_start
        self.pppOrderTally.pickTime = station_time
        self.pppOrderTally.workTime += station_time
        self.pppShiftTally.workTime += station_time

        return simulation_status

    def restock_items(self):
        # TODO using blunt force, refine later
        # take container to the outbound box shelf area
        self.show_bread_crumbs('restocking items')
        _min = params.TIME_TO_RESTOCK_ITEMS_MIN
        _max = params.TIME_TO_RESTOCK_ITEMS_MAX
        time = random.randrange(_min, _max)
        yield self.env.timeout(time)
        self.show_bread_crumbs('restocked items')

    def pack_area(self):
        # start counting packing station time
        simulation_status = True
        station_start = self.env.now

        self.show_bread_crumbs('starts walking to the packing station')
        _min = params.TIME_TO_WALK_TO_PACK_STATION_MIN
        _max = params.TIME_TO_WALK_TO_PACK_STATION_MAX
        time = random.randrange(_min, _max)
        yield self.env.timeout(time)
        self.show_bread_crumbs('arrives the packing station')

        # pack the order
        with self.packingLocationResource.request() as req:
            yield req

            if app_numbers.get_random_pack_resources_qtd() == 0:
                self.show_bread_crumbs(orderStatus.OrderStatus.OOP.name)
                self.pppOrderTally.status = orderStatus.OrderStatus.OOP.name
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

    def label_area(self):
        # start counting label area time
        simulation_status = True
        station_start = self.env.now

        self.show_bread_crumbs('starts walking to the label area')
        _min = params.TIME_TO_WALK_TO_LABEL_STATION_MIN
        _max = params.TIME_TO_WALK_TO_LABEL_STATION_MAX
        time = random.randrange(_min, _max)
        yield self.env.timeout(time)
        self.show_bread_crumbs('arrived at the label area')

        # label the order
        with self.labelPrintersResource.request() as req:
            yield req
            if app_numbers.get_random_label_resources_qtd() == 0:
                self.show_bread_crumbs(orderStatus.OrderStatus.OOL.name)
                self.pppOrderTally.status = orderStatus.OrderStatus.OOL.name
                simulation_status = False
            else:
                _min = params.TIME_TO_LABEL_ORDER_MIN
                _max = params.TIME_TO_LABEL_ORDER_MAX
                time = random.randrange(_min, _max)
                yield self.env.timeout(time)
                self.pppOrderTally.status = orderStatus.OrderStatus.Fulfilled.name
                self.show_bread_crumbs('labeled the order items')

        # accumulate  label area time
        self.show_bread_crumbs('leaving label area')
        station_time = self.env.now - station_start
        self.pppOrderTally.labelTime = station_time
        self.pppOrderTally.workTime += station_time
        self.pppShiftTally.workTime += station_time

        return simulation_status

    def deliver_area(self):
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
        msg = '%s %s %s at %s' % (str(self.env.now).zfill(5),
                                  self.pppShiftTally.pppId,
                                  self.pppOrderTally.orderId, detail)
        print(msg)
        list_array = [
            str(self.env.now).zfill(5),
            self.pppShiftTally.pppId,
            self.pppOrderTally.orderId, detail
        ]
        self.pppActivityLog.write(list_array)

    def print_order_stats(self):
        # print
        print('%s %s %s %s %s %s %s %s  %s %s %s %s %s %s %a' % (
            str(self.env.now).zfill(5),
            self.pppShiftTally.pppId,
            self.pppOrderTally.orderId,
            self.pppOrderTally.items,
            str(self.pppOrderTally.orderTime).zfill(3),
            str(self.pppOrderTally.pickTime).zfill(3),
            str(self.pppOrderTally.packTime).zfill(3),
            str(self.pppOrderTally.labelTime).zfill(3),
            str(self.pppOrderTally.courierTime).zfill(3),
            str(self.pppOrderTally.cleaningReceivingTime).zfill(3),
            str(self.pppOrderTally.cycleCountTime).zfill(3),
            str(self.pppOrderTally.parcelLevelScanningTime).zfill(3),
            str(self.pppOrderTally.breakTime).zfill(4),
            str(self.pppShiftTally.workTime).zfill(5),
            self.pppOrderTally.status))
        # log
        list_array = [str(self.env.now).zfill(5),
                      self.pppShiftTally.pppId,
                      self.pppOrderTally.orderId,
                      self.pppOrderTally.items,
                      self.pppOrderTally.orderTime,
                      self.pppOrderTally.pickTime,
                      self.pppOrderTally.packTime,
                      self.pppOrderTally.labelTime,
                      self.pppOrderTally.courierTime,
                      self.pppOrderTally.cleaningReceivingTime,
                      self.pppOrderTally.cycleCountTime,
                      self.pppOrderTally.parcelLevelScanningTime,
                      self.pppOrderTally.breakTime,
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
            PppShiftTally - The OrderSimulator uses it to collect the each PPP shift data
            OrderTally - The OrderSimulator uses it to collect each order's fulfillment data
"""

# Set up the simulation
simulation_environment = simpy.Environment()  # one environment for the whole simulation
orderTabletResource = simpy.Resource(simulation_environment, capacity=params.ORDER_TABLETS)
packingLocationResource = simpy.Resource(simulation_environment, capacity=params.PACKING_LOCATIONS)
labelPrintersResource = simpy.Resource(simulation_environment, capacity=params.LABEL_PRINTERS)

# TODO move these logs to their own package / class
if os.path.isfile(params.ORDER_TALLY_LOG):
    os.remove(params.ORDER_TALLY_LOG)
if os.path.isfile(params.PPP_ACTIVITY_LOG):
    os.remove(params.PPP_ACTIVITY_LOG)

orderTallyLogLock = threading.Lock()
orderTallyLog = csv.CSV(params.ORDER_TALLY_LOG, orderTallyLogLock)
orderTallyLog.open()
header = [
    'time',
    'pppId',
    'orderId',
    'items',
    'orderTime',
    'pickTime',
    'packTime',
    'labelTime',
    'courierTime',
    'c_rTime',
    'c_cTime',
    'plsTime',
    'breakTime',
    'totalOrderTime',
    'status']
orderTallyLog.write(header)

pppActivityLogLock = threading.Lock()
pppActivityLog = csv.CSV(params.PPP_ACTIVITY_LOG, pppActivityLogLock)
pppActivityLog.open()
header = ['time', 'pppId', 'orderId', 'activity']
pppActivityLog.write(header)

for i in range(params.NUMBER_OF_PPP):
    ppp = PPP(simulation_environment)
    ppp.pppShiftTally = ppp_shift_tally.PppShiftTally()  # set PPP tally
    ppp.orderTallyLog = orderTallyLog  # set simulation CSV file
    ppp.pppActivityLog = pppActivityLog  # set ppp activity log, it is too big for the screen only
    ppp.orderTabletResource = orderTabletResource  # set simulation Order Tablet Resource
    ppp.packingLocationResource = packingLocationResource  # set simulation Packing Location Resource
    ppp.labelPrintersResource = labelPrintersResource  # set simulation Label Printer Resource
    ppp_process = simulation_environment.process(ppp.checkin(simulation_environment))

# Run the simulation
simulation_environment.run()
orderTallyLog.close()
