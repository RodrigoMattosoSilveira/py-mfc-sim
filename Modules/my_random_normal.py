import numpy as np
import random
from math import trunc


def get_random_normal(mu, sigma):
    i = random.randint(0, 99)
    s = np.random.normal(mu, sigma, 100)
    return trunc(s[i] + 0.5)
