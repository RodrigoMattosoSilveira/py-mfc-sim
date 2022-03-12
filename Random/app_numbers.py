import parameters as params
from Random.generators import get_random_pareto, get_random_poisson


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