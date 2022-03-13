import enum


class OrderStatus(enum.Enum):
    Unfulfilled = 0
    Out_Of_Stock = 1
    Out_Of_Packing_Resources = 2
    Out_Of_Labeling_Resources = 3
    Fulfilled = 4
    Break = 5

