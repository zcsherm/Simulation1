import unittest
from world import *
from actions import *
from food import *
from utilities import *
from decoder import Decoder
from sample import *

class FirstTest(unittest.TestCase):
    """
    Test methods of world.py
    """
    @classmethod
    def setUpClass(cls):
        """
        Initialize the constructor and read the test genome
        """
        print("==================== World.py testing ===================")
        cls._world = World()
        cls._grid = cls._world.get_grid()

    def setUp(self):
        print(f"\n==================== {self._testMethodName} ====================\n")


    def test01(self):
        """
        Test print grid (visual inspection)
        """
        self._world.print_grid()

    def test02(self):
        """
        Test that food decays properly on a forward step
        """
        food = self._grid[0][0].get_food()
        if food is None:
            food = Food()
            self._grid[0][0].set_food()
        val = food.get_size()
        self._world.progress_sim()
        self.assertTrue(food.get_size()<val)

    def test03(self):
        """
        Test sim progression, verify new food is made and flow works. Test over 100 steps, pausing every 10
        """
        self._world.run_sim(pause_interval = 10, max = 100)

    def test04(self):
        """
        Breaking my own rules and setting multiple asserts into this one. Testing basic actions of critter in environ
        """
        # Create the organism
        d = Decoder()
        d.set_genome(TEST_GENOME)
        d.set_brain_genome(TEST_BRAIN_GENOME)
        org = d.read_genome()
        energy = org.get_energy()
        print(f"Current Energy {energy}")

        # Place the organism in the world and test turning left
        self._world.place_organism(org,0,0)
        self._world.print_grid()
        self._world.handle_action(org, 0)
        energy = org.get_energy()
        print(f"Current Energy {energy}")
        new_heading = org.get_heading()
        self.assertTrue(new_heading == [-1,0])

        # Test turning right twice
        self._world.handle_action(org,1)
        self._world.handle_action(org,1)
        energy = org.get_energy()
        print(f"Current Energy {energy}")
        new_heading = org.get_heading()
        self.assertEqual(new_heading, [1,0])
        self._world.print_grid()

        # Test moving forward
        self._world.handle_action(org,2)
        energy = org.get_energy()
        self._world.print_grid()
        print(f"Current Energy {energy}")
        new_pos = org.get_coords()
        print(f"New coordinates: {new_pos}")

        # Test letting the organism eat food
        food = Food()
        org.get_cell().set_food(food)
        org.eat_food(org.get_cell().get_food())
        print(org.chems)
        self.assertTrue(org.get_cell().get_food() is None)

        # Test the organism going off the edge of the board
        self._world.handle_action(org,0)
        self._world.handle_action(org,2)
        self._world.print_grid()
        new_pos = org.get_coords()
        print(f"New coordinates: {new_pos}")
        
