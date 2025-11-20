"""
Creates a simple organism for prototyping purposes
"""

from utilities import *
import Chemicals
import random
import numpy as np

ORGAN_ENERGY_MULTIPLIER = .4
HEALTH_DEATH_THRESHOLD = .05

def health_function(val):
    """
    Maps organ health to overall creature health. Low health organs are very detrimental.
    """
    return 1/(1+(100*(np.e** (-10 * val))))

class Body:
    """
    An organism, a container for organs and chemicals
    """
    def __init__(self, genome=None):
        """
        Setup a generic organism
        :param genome: A bit string genome, deprecated method of construction
        """
        self._id = generate_id()
        self._chems = {chem: 0 for chem in Chemicals.CHEMS}
        self._concentrations = {chem: 0 for chem in Chemicals.CHEMS}
        self._organs = []
        self._health = 1
        self._alive = True
        self._brain = None
        self._genome = genome
        self._dna_head = None
        self._heading = [1,0]
        self._energy = 1
        self._max_energy = 1

    def set_grid(self, grid):
        self._grid = grid

    def set_heading(self, heading):
        self._heading = heading

    def set_position(self, position):
        self._position = position

    def set_brain(self, brain):
        self._brain = brain
        
    def add_organ(self, organ):
        """
        Adds a new organ to the creature
        """
        self._max_energy += organ.get_energy_capacity()*ORGAN_ENERGY_MULTIPLIER
        self._organs.append(organ)

    def activate_organs(self):
        """
        Activates each organ based on the activation rate of that organ
        """
        for organ in self._organs:
            roll = random.random()
            if roll <= organ.get_act_rate():
                organ.activate_organ()
        self.calc_concentrations()

    def get_max_energy(self):
        tot = 1
        for organ in organs:
            if organ.get_health() > 0:
                tot += organ.get_energy_capacity()*ORGAN_ENERGY_MULTIPLIER
        self._max_energy = tot
        return tot

    def get_energy(self):
        return self._energy
        
    def calc_concentrations(self):
        """
        Rechecks the concentrations of chemicals in the body
        """
        total = 0
        for key, val in self._chems.items():
            total += val
        if total == 0:
            total = 1
        self._concentrations = {chem: val/total for chem, val in self._chems.items()}

    def get_concentration(self, chemical):
        """
        Try to get the chemical concentration of a particular chemical
        :param chemical: The chemical to check
        :return: The concentration of that chemical, a float between 0-1
        """
        try:
            return self._concentrations[chemical]
        except:
            print("\n!!!!!! An error occured !!!! An invalid chemical was requested!\n")
            return 0

    def get_chemical(self,chemical):
        """
        Gets the number of units of a chemical in the body
        :param chemical: The chemical to check
        """
        return self._chems[chemical]

    def add_chemical(self, chemical, amount):
        """
        Adds an amount of a chemical to the body
        :param chemical: The checmicla
        :param amount: The amount to add
        """
        try:
            self._chems[chemical] += amount
        except:
            print("\n!!!!!! An error occured !!!! An invalid chemical was added to the body\n")
            return

    def rem_chemical(self, chemical, amount):
        try:
            self._chems[chemical] -= amount
            if self._chems[chemical] < 0:
                self._chems[chemical] = 0
        except:
            print("\n!!!!!! An error occured !!!! An invalid chemical was removed from the body\n")
            return

    def set_dna_head(self, node):
        self._dna_head = node
        
    def get_genome(self):
        if self._dna_head is None:
            return self._genome
        return self._dna_head.get_entire_genome()

    def take_action(self):
        """
        Calls the brain to decide on an action
        """
        return self._brain.decide_action()
    
    def eat_food(self, food):
        chems = food.get_chems()
        for chem in chems:
            self.add_chemical(chem, chems[chem].get_quantity())
        energy = food.get_energy()
        self.add_energy(energy)

    def add_energy(self, amount):
        self._energy = min(self._max_energy, self._energy + amount)

    def remove_energy(self, amount):
        self._energy -= amount
        
    def get_organs(self):
        return self._organs
    
    def check_alive(self):
        self.check_organ_health()
        if self._health < HEALTH_DEATH_THRESHOLD:
            return False
        if self._energy <= 0:
            return False
        return True
    
    def check_organ_health(self):
        o_healths = 0
        for organ in self._organs:
            o_health = organ.get_health()
            if o_health < HEALTH_DEATH_THRESHOLD:
                self._organs.remove(organ)
            else:
                o_healths += health_function(o_health)
        self._health = o_healths/len(self._organs)
        
    def describe(self):
        print(f"Creature {self._id}:")
        for organ in self._organs:
            organ.describe()

    def status(self):
        print(f"Creature {self._id}:\n")
        for chemical in Chemicals.CHEMS:
            print(f"Chemical {chemical} -- units: {self._chems[chemical]}, concentrations: {self._concentrations[chemical]}\n")
        for organ in self._organs:
            organ.status()
