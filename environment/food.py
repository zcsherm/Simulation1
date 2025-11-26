import random
import numpy as np

FOOD_DECAY_LOWER_BOUND = .01
FOOD_DECAY_UPPER_BOUND = .1

def food_decay_rate(principal):
    """
    Possible function for decay rate as a function of time steps since object creation:
    f(t)=P(e+m)^-x
    P is initial loaded in amount
    and m is a value between 1.001 and 1.11
    """
    
    pass
    
class Chemical:
    """
    Generic class for a particular chemical. Arbitrary. Essentially will be a container in each individual and environment object
    """
    def __init__(self, id):
        self._id = id
        self._quantity = 0

    def drain(self, quant):
        self._quantity -= quant

    def increase(self,quant):
        self._quantity += quant

    def get_id(self):
        return self._id

    def get_quantity(self):
        return self._quantity

class Food:
    """
    Generic class for a food object. Will contain chemicals and/or energy in limited quantities that diminish with time.
    """
    def __init__(self):
        self._chems = {}
        self._energy = 0
        self._degrade_multiplier = 0
        self._size = 0
        self.random_food()
        self.get_size()
        
    def random_food(self):
        """
        Generate a random food that contains 1-3 chemicals with varying strengths.
        """
        self._degrade_multiplier = random.randint(FOOD_DECAY_LOWER_BOUND, FOOD_DECAY_UPPER_BOUND)
        chems = random.randint(1,3)
        for i in range(chems):
            chemical = random.randint(0,15)
            quant = min(np.random.binomial(100, .04), 15)
            self._chems[chemical]=(Chemical(bin(chemical)))
            self._chems[chemical].increase(quant)
        if chems <= 2:
            self._energy = random.uniform(1,10)
    
    def degrade(self):
        """
        Causes all chemicals to degrade by certain rate
        """
        for chemical in self._chems.keys():
            drain = self._degrade_multiplier/100 * self._chems[chemical].get_quantity() + .3
            self._chems[chemical].drain(drain)
        if self._energy > 0:
            self._energy -= self._degrade_multiplier/100 * self._size
        self.get_size()
        self.check_death()

    def get_chems(self):
        return self._chems

    def get_size(self):
        """
        Fetches the current size of a food item, which is simply the sum of how much of each chemical and energy there is in the item
        """
        size = 0
        for chemical in self._chems:
            size += chemical.get_quantity()
        size += self._energy
        self._size = size
        
    def check_death(self):
        """
        Checks if any chemicals in the food are degraded sufficiently to remove them or the entire food source
        """
        if self._size <= 1:
            self._size = 0
            self._chems = []
            return
        self._chems = [chemical for chemical in self._chems if chemical.get_quantity() > 1]
        if self._energy <= 1:
            self._energy = 0
