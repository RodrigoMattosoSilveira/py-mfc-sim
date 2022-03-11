import secrets
import string


class OrderTally(object):
    """
    Used to collect order fulfillment data
    """
    def __init__(self, ppp_id):
        self.pppId = ppp_id
        self.orderId = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        self.orderTime = 0
        self.pickTime = 0
        self.packTime = 0
        self.labelTime = 0
        self.deliveryTime = 0
        self.readyTime = 0
        self.workTime = 0
        self.items = 0
