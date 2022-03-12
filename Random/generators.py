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


def get_random_poisson(a):
    # print('mu:', _mu)
    # print('sigma:', _sigma)
    s = np.random.poisson(a, 1000)
    j = random.randint(1, 100)
    random_number = trunc(s[j] + 0.5)
    return random_number


