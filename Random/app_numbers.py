from Constants import parameters as params
from Random.generators import get_random_pareto, get_random_poisson, rng_apd


def get_random_order_items():
    new_order_items = get_random_pareto(1, 1.160964)
    if new_order_items > 12:
        new_order_items = 12
    else:
        if 3 < new_order_items < 12:
            new_order_items = 6
        else:
            new_order_items = 1
    return new_order_items


def get_random_sku_qtd():
    return get_random_poisson(params.RANDOM_SKU_QTD_A)


def get_random_pack_resources_qtd():
    return get_random_poisson(params.RANDOM_PACKING_RESOURCES_QTD_A)


def have_label_resources():
    got_them = False
    arr = [0, 1]
    freq = [100-params.LABEL_AVAILABILITY_PROBABILITY, params.LABEL_AVAILABILITY_PROBABILITY]
    n = len(arr)
    if rng_apd(arr, freq, n):
        got_them = True

    return got_them


def is_order_rush_next_day():
    order_type = params.ORDER_TYPE_RUSH
    arr = [0, 1]
    freq = [params.ORDER_TYPE_RUSH_PROB, 100-params.ORDER_TYPE_RUSH_PROB]
    n = len(arr)
    if rng_apd(arr, freq, n):
        order_type = params.ORDER_TYPE_NATIONAL

    return order_type


def got_package_containers():
    got_them = False
    arr = [0, 1]
    freq = [100-params.BOX_AVAILABILITY_PROBABILITY, params.BOX_AVAILABILITY_PROBABILITY]
    n = len(arr)
    if rng_apd(arr, freq, n):
        got_them = True

    return got_them


