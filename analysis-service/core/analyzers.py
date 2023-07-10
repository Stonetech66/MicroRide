import random

def get_random_fare():
    prices=(1000, 2000, 5000, 7000, 10000, 13000, 15000, 20000, 25000, 30000)
    return random.choice(prices)
    



def get_ride_eta():
    etas=[eta for eta in range(1, 11)]
    return random.choice(etas)
