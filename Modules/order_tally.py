import secrets
import string
from Random.app_numbers import get_random_order_items


class OrderTally(object):
    """
    Used to collect order fulfillment data
    See https://www.tutorialsteacher.com/python/property-decorator for info on property decorators
    """
    def __init__(self, ppp_id):
        self.__pppId = ppp_id
        self.__orderId = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        self.__items = 0
        self.__orderType = None
        self.__numberOfBoxes = 0
        self.__checkInTime = 0
        self.__cleaningReceivingTime = 0
        self.__parcelLevelScanningTime = 0
        self.__cycleCountTime = 0
        self.__orderTime = 0
        self.__pickTime = 0
        self.__packTime = 0
        self.__labelTime = 0
        self.__deliveryTime = 0
        self.__courierTime = 0
        self.__breakTime = 0
        self.__workTime = 0
        self.__status = 'Unfulfilled'

    @property
    def pppId(self):
        return self.__pppId

    @pppId.setter
    def pppId(self, value):
        self.__pppId = value

    @property
    def orderId(self):
        return self.__orderId

    @orderId.setter
    def orderId(self, value):
        self.__orderId = value

    @property
    def items(self):
        return self.__items

    @items.setter
    def items(self, value):
        self.__items = value

    @property
    def orderType(self):
        return self.__orderType

    @orderType.setter
    def orderType(self, value):
        self.__orderType = value

    @property
    def kitItems(self):
        return self.__kitItems

    @kitItems.setter
    def kitItems(self, value):
        self.__kitItems = value

    @property
    def checkInTime(self):
        return self.checkInTime

    @checkInTime.setter
    def checkInTime(self, value):
        self.__checkInTime = value

    @property
    def cleaningReceivingTime(self):
        return self.__cleaningReceivingTime

    @cleaningReceivingTime.setter
    def cleaningReceivingTime(self, value):
        self.__cleaningReceivingTime = value

    @property
    def cycleCountTime(self):
        return self.__cycleCountTime

    @cycleCountTime.setter
    def cycleCountTime(self, value):
        self.__cycleCountTime = value

    @property
    def parcelLevelScanningTime(self):
        return self.__parcelLevelScanningTime

    @parcelLevelScanningTime.setter
    def parcelLevelScanningTime(self, value):
        self.__parcelLevelScanningTime = value

    @property
    def orderTime(self):
        return self.__orderTime

    @orderTime.setter
    def orderTime(self, value):
        self.__orderTime = value

    @property
    def pickTime(self):
        return self.__pickTime

    @pickTime.setter
    def pickTime(self, value):
        self.__pickTime = value

    @property
    def packTime(self):
        return self.__packTime

    @packTime.setter
    def packTime(self, value):
        self.__packTime = value

    @property
    def labelTime(self):
        return self.__labelTime

    @labelTime.setter
    def labelTime(self, value):
        self.__labelTime = value

    @property
    def deliveryTime(self):
        return self.__deliveryTime

    @deliveryTime.setter
    def deliveryTime(self, value):
        self.__deliveryTime = value

    @property
    def courierTime(self):
        return self.__courierTime

    @courierTime.setter
    def courierTime(self, value):
        self.__courierTime = value

    @property
    def breakTime(self):
        return self.__breakTime

    @breakTime.setter
    def breakTime(self, value):
        self.__breakTime = value

    @property
    def workTime(self):
        return self.__workTime

    @workTime.setter
    def workTime(self, value):
        self.__workTime = value

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, value):
        self.__status = value
