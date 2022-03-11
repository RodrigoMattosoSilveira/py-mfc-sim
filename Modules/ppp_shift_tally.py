import secrets
import string
import parameters as params


class PppShiftTally(object):
    """
    Used to collect PPP shift data
    See https://www.tutorialsteacher.com/python/property-decorator for info on property decorators
    """

    def __init__(self):
        self.__pppId = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        self.__shiftStatus = params.PPP_SHIFT_NOT_STARTED
        self.__orders = 0
        self.__workTime = 0
        self.__hourBreakDuration = 0
        self.__shiftBreakDuration = 0
        self.__nextHourBreak = 3600 - params.HOUR_BREAK_DURATION
        self.__nextShiftBreak = params.SHIFT_WORK_DURATION / params.SHIFT_BREAKS_PER_SHIFT

    @property
    def pppId(self):
        return self.__pppId

    @pppId.setter
    def pppId(self, value):
        self.__pppId = value

    @property
    def shiftStatus(self):
        return self.shiftStatus

    @shiftStatus.setter
    def shiftStatus(self, value):
        self.shiftStatus = value

    @property
    def orders(self):
        return self.__orders

    @orders.setter
    def orders(self, value):
        self.__orders = value

    @property
    def workTime(self):
        return self.__workTime

    @workTime.setter
    def workTime(self, value):
        self.__workTime = value

    @property
    def hourBreakDuration(self):
        return self.__hourBreakDuration

    @hourBreakDuration.setter
    def hourBreakDuration(self, value):
        self.__hourBreakDuration = value

    @property
    def shiftBreakDuration(self):
        return self.__shiftBreakDuration

    @shiftBreakDuration.setter
    def shiftBreakDuration(self, value):
        self.__shiftBreakDuration = value

    @property
    def nextHourBreak(self):
        return self.__nextHourBreak

    @nextHourBreak.setter
    def nextHourBreak(self, value):
        self.__nextHourBreak = value

    @property
    def nextShiftBreak(self):
        return self.__nextShiftBreak

    @nextShiftBreak.setter
    def nextShiftBreak(self, value):
        self.__nextShiftBreak = value
