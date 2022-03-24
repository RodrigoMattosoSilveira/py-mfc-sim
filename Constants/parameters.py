# Overall simulation parameters
NUMBER_OF_PPP = 3

# PPP break control parameters
SHIFT_WORK_DURATION = 32400
SHIFT_BREAKS_PER_SHIFT = 2
SHIFT_BREAK_DURATION = 3600
HOUR_BREAK_DURATION = 300

# Cleaning and receiving parameters
CLEANING_RECEIVING_SHIFT_PERCENT_ALLOCATION = 0.15

# Cycle count parameters
CYCLE_COUNT_SHIFT_PERCENT_ALLOCATION = 0.05

# Cycle count parameters
PARCEL_LEVEL_SCANNING_SHIFT_PERCENT_ALLOCATION = 0.05

# Pick parameters
TIME_TO_WALK_TO_PICK_STATION_MIN = 45
TIME_TO_WALK_TO_PICK_STATION_MAX = 60
TIME_TO_WALK_TO_PICK_NEXT_ITEM_MIN = 10
TIME_TO_WALK_TO_PICK_NEXT_ITEM_MAX = 15
KIT_ITEMS_PER_PICK = 2
TIME_TO_PICK_ITEM_MIN = 5
TIME_TO_PICK_ITEM_MAX = 15
RANDOM_SKU_QTD_A = 4
INVENTORY_AVAILABILITY_PROBABILITY = 95
TIME_TO_WALK_TO_OUTBOUND_SHELF_AREA_MIN = 45
TIME_TO_WALK_TO_OUTBOUND_SHELF_AREA_MAX = 60
TIME_TO_PLACE_ITEM_IN_CONTAINER_MIN = 10
TIME_TO_PLACE_ITEM_IN_CONTAINER_MAX = 15
TIME_TO_PLACE_CONTAINER_ON_OUTBOUND_SHELF_MIN = 45
TIME_TO_PLACE_CONTAINER_ON_OUTBOUND_SHELF_MAX = 60
TIME_TO_RESTOCK_ITEMS_MIN = 180
TIME_TO_RESTOCK_ITEMS_MAX = 300


# Pack parameters
TIME_TO_WALK_TO_PACK_STATION_MIN = 15
TIME_TO_WALK_TO_PACK_STATION_MAX = 20
TIME_TO_SELECT_PACK_RESOURCES_MIN = 10
TIME_TO_SELECT_PACK_RESOURCES_MAX = 15
TIME_TO_PACK_ORDER_MIN = 10
TIME_TO_PACK_ORDER_MAX = 20
RANDOM_PACKING_RESOURCES_QTD_A = 2.5
STAGE_AREAS = 2
BAG_AVAILABILITY_PROBABILITY = 99
BOX_AVAILABILITY_PROBABILITY = 95
PACKING_LOCATIONS = 2
EACHES_PER_BOX = 6
EACHES_PER_BAG = 1

# Label area parameters
TIME_TO_WALK_TO_LABEL_STATION_MIN = 15
TIME_TO_WALK_TO_LABEL_STATION_MAX = 20
TIME_TO_PRINT_LABEL_MIN = 20
TIME_TO_PRINT_LABEL_MAX = 30
TIME_TO_LABEL_ORDER_MIN = 10
TIME_TO_LABEL_ORDER_MAX = 15
LABEL_PRINTERS = 1
RANDOM_LABELING_RESOURCES_QTD_A = 2.5
LABEL_AVAILABILITY_PROBABILITY = 95

# Deliver area parameters
TIME_TO_WALK_TO_COURIER_STATION_MIN = 15
TIME_TO_WALK_TO_COURIER_STATION_MAX = 25
DELIVERY_FRIDGE_AVAILABILITY_PROBABILITY = 95

# Order area parameters
ORDER_TYPE_RUSH = 'RUSH'
ORDER_TYPE_NATIONAL = 'NATIONAL'
ORDER_TYPE_RUSH_PROB = 25
TIME_TO_PLACE_ORDER_AT_COURIER_STATION_MIN = 15
TIME_TO_PLACE_ORDER_AT_COURIER_STATION_MAX = 20
TIME_TO_WALK_TO_ORDER_STATION_MIN = 15
TIME_TO_WALK_TO_ORDER_STATION_MAX = 20
ORDER_TABLETS = 1
TIME_TO_RECORD_ORDER_STATS_MIN = 45
TIME_TO_RECORD_ORDER_STATS_MAX = 60
TIME_TO_WAIT_BETWEEN_ORDERS_MIN = 10
TIME_TO_WAIT_BETWEEN_ORDERS_MAX = 15
TIME_TO_READ_ORDER_MIN = 45
TIME_TO_READ_ORDER_MAX = 60
ORDER_ITEMS_MIN = 1
ORDER_ITEMS_MAX = 12
ORDER_INTER_ARRIVAL_TIME_MEAN = 10
ORDER_INTER_ARRIVAL_TIME_SIGMA = 2.6

# Other
PPP_SHIFT_NOT_STARTED = -1
PPP_SHIFT_STARTED = 0
PPP_SHIFT_ENDED = 1

# Log files parameters
SHIFT_TALLY_LOG = './IO/shift_tally.csv'
ORDER_TALLY_LOG = './IO/order_tally.csv'
PPP_ACTIVITY_LOG = './IO/ppp_activity_log.csv'



