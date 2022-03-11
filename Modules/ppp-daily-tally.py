import secrets
import string
import parameters as params


class PppDailyTally(object):
    """
    Used to collect PPP shift data
    """
    def __init__(self):
        self.pppId = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        self.orders = 0
        self.workTime = 0
        self.hourBreakDuration = 0
        self.shiftBreakDuration = 0
        self.nextHourBreak = 3600 - params.HOUR_BREAK_DURATION
        self.nextShiftBreak = params.SHIFT_WORK_DURATION/params.SHIFT_BREAKS_PER_SHIFT
