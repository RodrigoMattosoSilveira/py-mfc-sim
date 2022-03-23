import enum


class OrderStatus(enum.Enum):
    Unfulfilled = 0
    OOS = 1  # Out of stock
    OOP = 2  # Out of parcels
    OOL = 3  # out of labels
    Fulfilled = 4
    Break = 5
    CR = 6   # Cleaning and receiving
    CC = 7   # Cycle Count
    PLS = 8  # Parcel Level Scanning

