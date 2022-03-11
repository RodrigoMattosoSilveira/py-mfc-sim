import numpy as np
import random
from math import trunc


def get_random_normal(mu, sigma):
    i = random.randint(0, 99)
    s = np.random.normal(mu, sigma, 100)
    return trunc(s[i] + 0.5)


def get_random_pareto(a, m):
    s = (np.random.pareto(a, 1000) + 1) * m
    j = random.randint(1, 100)
    random_number = trunc(s[j] + 0.5)
    return random_number


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
