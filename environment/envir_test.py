import unittest
from world import *
from actions import *
from food import *
from utilities import *
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
        Test adding in a critter?
        """
        pass
        
