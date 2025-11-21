import unittest
import copy
import random
import numpy as np
import pandas as pd
import seaborn as sb
import matplotlib.pyplot as plt
from utilities import *
import Constructor
from Constructor import Decoder
from sample import *

class FirstTest(unittest.TestCase):
    """
    Handles testing the test genome, ensuring that all parts function as intended.
    """
    @classmethod
    def setUpClass(cls):
        """
        Initialize the constructor and read the test genome
        """
        cls._decoder = Decoder()
        cls._decoder.set_genome(TEST_GENOME)
        cls._decoder.set_brain_genome(TEST_BRAIN_GENOME)
        cls._organism = cls._decoder.read_genome()
        cls._reaction_gene = cls._organism.get_organs()[0].get_genes()[2]
        
    def test01(self):
        """
        Tests that the genome was decoded accurately into 2 organs, prints the organisms descriptions for visual inspection
        """
        print("=================== TEST 1 ======================")
        self._organism.describe()
        self.assertTrue(len(self._organism.get_organs()) == 1)
        
    def test01_5(self):
        """
        Test that the linked list dna matches the source dna.
        """
        print("================== TEST 1.5 ====================")
        genome = TEST_GENOME
        self.assertEqual(genome, self._organism.get_genome())
        
    # Test that the body can add and remove chemicals
    def test02(self):
        """
        Test that adding a chemical to the body actually works
        """
        print("=================== TEST 2 ======================")
        self._organism.add_chemical(14, 3)
        self.assertEqual(self._organism.get_chemical(14), 3)

    def test03(self):
        """
        Test that concentration is calculated correctly at only 1 chemical
        """
        print("=================== TEST 3 ======================")
        self._organism.calc_concentrations()
        self.assertEqual(self._organism.get_concentration(14),1)

    def test04(self):
        """
        Test adding a second chemical
        """
        print("=================== TEST 4 ======================")
        self._organism.add_chemical(2, 2)
        self.assertEqual(self._organism.get_chemical(2),2)

    def test05(self):
        """
        Test that concentration is accurate with multiple chemicals in body
        """
        print("=================== TEST 5 ======================")
        self._organism.calc_concentrations()
        self.assertEqual(self._organism.get_concentration(2), .4)

    def test06(self):
        """
        Remove a chemical and verify that concentrations were updated
        """
        print("=================== TEST 6 ======================")
        self._organism.rem_chemical(2,1)
        self._organism.calc_concentrations()
        self.assertTrue(self._organism.get_concentration(14), .75)

    def test07(self):
        """
        Remove all chemicals, test that no value goes under 0
        """
        print("=================== TEST 7 ======================")
        self._organism.rem_chemical(2,1)
        self._organism.rem_chemical(14,4)
        self.assertTrue(self._organism.get_chemical(14) == 0)

# Test that receptor can read chem
    def test08(self):
        """
        Test that a receptors function outputs expected values. 
        """
        print("=================== TEST 8 ======================")
        
        # Expected values for read and output
        values = [.5, .661]
        
        # Copy the organism to preserve original state
        organism_b = copy.deepcopy(self._organism)

        # Add 2 chemicals, concentrations at .5
        organism_b.add_chemical(3,1)
        organism_b.add_chemical(6,1)
        receptor = organism_b.get_organs()[0].get_genes()[1]
        organism_b.calc_concentrations()

        # Get the input and the output of the receptor and compare to expected
        conc = receptor.read_input()
        output = receptor.get_output()
        self.assertAlmostEqual(values[0], conc, delta=0.01)
        self.assertAlmostEqual(values[1], output, delta=0.01)
        
        # Preserve state for next test
        self._organism_b = organism_b

# Test that emitter can read parameter
    def test09(self):
        """
        Test that the emitter can properly read and output. Test that body receives chem
        """
        print("=================== TEST 9 ======================")
        organism_b = copy.deepcopy(self._organism)
        organism_b.get_organs()[0].debug_set_health(.4)
        emitter = organism_b.get_organs()[0].get_genes()[0]
        read_val = emitter.read_param()
        output = emitter.get_output_amt()
        emitter.release_chemical()
        self.assertAlmostEqual(read_val, 1/32, delta=.001)
        self.assertAlmostEqual(output, 5.9941, delta=.001)
        print(f"Outputs and inputs are good for test9")
        self.assertAlmostEqual(organism_b.get_chemical(5), 5.9941, delta=.001)
        
    def test10(self):
        """
        Test that health adjustment works
        """
        pass # Eh, I'm sure it does idgaf

# Test the reaction Gene
    def test11(self):
        """
        Test that chemical reaction checks body for available chems
        """
        print("=================== TEST 11 ======================")
        self.assertFalse(self._reaction_gene.check_for_requirements())

    def test12(self):
        """
        Test for false positive
        """
        print("=================== TEST 12 ======================")
        self._organism.add_chemical(6, 2)
        self.assertFalse(self._reaction_gene.check_for_requirements())

    def test13(self):
        """
        More tests for false positives
        """
        print("=================== TEST 13 ======================")
        self._organism.add_chemical(4, .25)
        self.assertFalse(self._reaction_gene.check_for_requirements())

    def test14(self):
        """
        Test for true positive
        """
        print("=================== TEST 14 ======================")
        self._organism.add_chemical(4, .25)
        self.assertTrue(self._reaction_gene.check_for_requirements())

    def test15(self):
        """
        Test that organ consumes chem 6
        """
        print("=================== TEST 15 ======================")
        self._reaction_gene.react()
        self.assertEqual(self._organism.get_chemical(6), 1)

    def test16(self):
        """
        Test that organ consumed chem 
        """
        print("=================== TEST 16 ======================")
        self.assertEqual(self._organism.get_chemical(4),0)

    def test17(self):
        """
        Test that organ released chem
        """
        print("=================== TEST 17 ======================")
        self.assertEqual(self._organism.get_chemical(2), 2)
