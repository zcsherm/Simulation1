"""
Creates a simple organism for prototyping purposes
"""

from utilities import *
import Chemicals
import random
import numpy as np

ORGAN_ENERGY_MULTIPLIER = .4
HEALTH_DEATH_THRESHOLD = .05

def energy_drain_function(val):
    """
    The function used to evaluate energy consumption during movement
    """
    return (1/50 * val) ** 3
    
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
        self._heading = [0,1]
        self._energy = 1
        self._max_energy = 1
        self._cell = None

    def set_world(self, world):
        """
        Sets the simulation that the creature is confined to
        """
        self._world = world

    def set_heading(self, heading):
        """
        Sets the current direction the creature is facing.
        :param direction: a list or tuple that represents the (x, y) facing
        """
        self._heading = heading

    def set_position(self, position):
        """
        Sets the current position of the organism in the simulation (should be coords instead?)
        """
        self._position = position

    def set_brain(self, brain):
        """
        Sets the brain for this creature
        """
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
                gene_count = len(organ.get_genes())
                fat_cells = organ.get_energy_capacity()
                self._remove_energy(energy_drain_function(gene_count+fat_cells))
        self.calc_concentrations()

    def get_max_energy(self):
        """
        Calculates the current maximum energy the organism can have.
        """
        tot = 1
        for organ in self._organs:
            if organ.get_health() > 0:
                tot += organ.get_energy_capacity()*ORGAN_ENERGY_MULTIPLIER
        self._max_energy = tot
        return tot

    def get_energy(self):
        """
        Gets the current energy of the organism
        """
        return self._energy

    def get_energy_percent(self):
        """
        Returns the current energy as a percent of maximum
        """
        return self._energy/self._max_energy

    def get_heading(self):
        """
        Returns the organisms current heading
        """
        return self._heading
        
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
        """
        Sets the dna linked list node for the body, is mostly noncoding
        """
        self._dna_head = node
        
    def get_genome(self):
        """
        Returns the entire genome of the organism
        """
        if self._dna_head is None:
            return self._genome
        return self._dna_head.get_entire_genome()

    def take_action(self):
        """
        Calls the brain to decide on an action
        """
        return self._brain.decide_action()
    
    def eat_food(self, food):
        """
        Eats a passed food item, incorporating the chemicals and energy into its body
        """
        chems = food.get_chems()
        for chem in chems:
            self.add_chemical(chem, chems[chem].get_quantity())
        energy = food.get_energy()
        self.add_energy(energy)

    def add_energy(self, amount):
        """
        Adds an amount of energy to the organism
        """
        self._energy = min(self._max_energy, self._energy + amount)

    def remove_energy(self, amount):
        """
        Removes a quantity of energy from the organism
        """
        self._energy = max(self._energy-amount,0)
        
    def get_organs(self):
        """
        Returns a list of all organs in the creature
        """
        return self._organs

    def get_brain(self):
        """
        Returns the creatures brain
        """
        return self._brain

    def check_alive(self):
        """
        Checks all organ healths and then sees if this organism is dead.
        """
        self.check_organ_health()
        if self._health < HEALTH_DEATH_THRESHOLD:
            return False
        if self._energy <= 0:
            return False
        return True
    
    def check_organ_health(self):
        """
        Checks the health of each organ and modifies the overall health of the creature accordingly. Also rechecks max energy
        """
        o_healths = 0

        # Check the health for each organ
        for organ in self._organs:
            o_health = organ.get_health()
            
            # Remove the organ if it died
            if o_health < HEALTH_DEATH_THRESHOLD:
                self._organs.remove(organ)
            
            # Calculate the 'overall' health and add that to the running total
            else:
                o_healths += health_function(o_health)

        # Overall creature health is the average of the running total
        self._health = o_healths/len(self._organs)
        self.get_max_energy()

    def get_health(self):
        """
        Returns the organisms current health
        """
        return self._health

    def set_cell(self, cell):
        """
        Set the gridpoint this creature exists on, specifically, the Cell object
        :param cell: The Cell object the creature currently occupies
        """
        self._cell = cell
        
    def get_food_at_space(self, space):
        """
        Return a food item located at a space relative to this creatures heading.
        """
        if self._cell is None:
            return None

        # Transform the space according to the creatures heading
        new_x = space[1]*self._heading[0]+space[0]*self._heading[1]
        new_y = space[1]*self._heading[1]-space[0]*self._heading[0]
        current_space = self._cell.get_coords()
        return self._cell.get_food_at([current_space[0]+new_x,current_space[1]+new_y])
        
    def describe(self):
        """
        Describes all organs, genes, and lobes inside the organism
        """
        print(f"Creature {self._id}:")
        for organ in self._organs:
            organ.describe()
        self._brain.describe()

    def status(self):
        """
        Gets a quick readout on the biological status of the organism.
        """
        print(f"Creature {self._id}:\n")
        print(f"Energy -- {self._energy}/{self._max_energy} = {self.get_energy_percent}}")
        print(f"Health -- {self._health}")
        for chemical in Chemicals.CHEMS:
            print(f"Chemical {chemical} -- units: {self._chems[chemical]}, concentrations: {self._concentrations[chemical]}\n")
        for organ in self._organs:
            organ.status()
