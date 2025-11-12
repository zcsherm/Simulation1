"""
DNA decodes a brain made up of lobes. Each lobe is a mini neural net that is simple feed forward. The very first node in the brain is the top level "Thinking node". This takes in all inputs from subnodes, goes through mutable neural net, and decides on an action (4 ourputs, EAT, Turn, Forward, NOP).
Lobe types:
    Chem internal input (single chem)
    Food input (single space)
    Chemical food input (single chem from food) Tied to food input, 
    Energy input 

Lobe Header:
Start code: 
    8bits (in a larger range than for a gene)

Params: 
    type: 4 bits (room for more lobe options)
    layers: 1 bit (val +1) 1-2
    width: 3 bit(val % 4 +1) 1-4
    Lobe_param: 4 bits (chem or direction)
        We need to then get layers * width nodes
        Each node:
            function: 2 bits - maybe not, might be better to have a set function for all
            weights: 6 bits each, need width number of weights ((val-32)/32)->[-1,1]
        So we need: (layers * width) * (6*width + 2) = 6LW^2 + 2LW bits
        At max size of 2 layers with width 4: 208 bits <- Kinda large
            
Brain organ:
start is null:
params:
    layers: 1 bit (2-3)
    width: 1 bits (4-5)
    Then layer * width nodes:
    
"""
import numpy as np
class Node:
    """
    Represents a single node in the neural net
    """
    def __init__(self):
        self._bias = .01

    def set_bias(self, bias):
        """
        Present implementation doesn't read bias from genome.
        """
        self._bias = bias

    def set_weights(self, weights):
        """
        Sets all weights of output for the node
        :param weights: A list containing 1 weight for every output of the layer
        """
        if not isinstance(weights, list):
            weights = [weights]
        self._weights = weights

    def set_function(self, function):
        """
        Sets the type of activation function for this node.
        """
        self._function = function

    def get_output(self, inputs):
        """
        Given an input value, the node returns a list of all outputs modified by weight
        """
        out = self._function(inputs+self._bias)
        weighted = [out*weight for weight in self._weights]
        return weighted

class Lobe:
    """
    Represents a collection of neurons
    """
    def __init__(self, creature):
        self._hidden = []
        self._owner = creature

    def set_dna_head(self, node):
        self._dna_head = node

    def get_genome(self):
        return self._dna_head.get_entire_genome()
        
    def set_final_node(self, node):
        """
        Technically not necessary, but could be helpful. Default is a linear output with weight of 1
        """
        self._final = node

    def set_num_layers(self, num):
        """
        Sets the number of layers in the hidden layer of the neural net. Presently limited to 1 or 2
        """
        self._num_layers = num

    def set_width_layers(self, num):
        """
        Sets the number of nodes in each hidden layer. Presently limited to 1-4
        """
        self._width_layers = num

    def add_layer(self, nodes):
        """
        Adds a width sized layer of nodes to the lobe (ie a hidden layer)
        """
        self._hidden.append(nodes)

    def input_action(self, val = 1):
        """
        Generic input function for debugging.
        """
        return val
        
    def get_output(self, debug=False):
        """
        Gets the final output of the neural net
        """
        # If debug is a number, we pass that value as the input to each beginning node
        if debug is False:
            inputs = [self.input_action() for i in range(self._width_layers)]
        else:
            inputs = [debug for i in range(self._width_layers)]

        # Iterate through each layer
        for i in range(self._num_layers):
            # I believe we can skip this if we allow the final layer to have n outputs and ignore the bottom n-1
            #if i == self._num_layers - 1:
            #    outputs = [0]
            #else:
            #    outputs = [0 for _ in range(self._width_layers)]
            
            # Setup the outputs for this layer
            outputs = [0 for _ in range(self._width_layers)]
            
            # For each node in this layer....
            for j in range(self._width_layers):
                node = self._hidden[i][j]
                # Get the outputs of that node from its respective input
                outs = node.get_output(inputs[j])
                for q in range(len(outs)):
                    # Add each output to the inputs for the next layer
                    outputs[q] += outs[q]
                    
            inputs = outputs

        # For a generic lobe, we only have 1 output, so we grab the topmost output.
        final_output = self._final.get_output(outputs[0])[0]
        return final_output
        
class ChemLobe(Lobe):
    """
    Represents a lobe specialized in reading chemical concentrations in the body
    """
    def set_chem(self, chem):
        """
        Sets the chemical that this lobe reads
        """
        self._chem = chem
        
    def input_action(self):
        """
        Returns the concentration of the desired chemical in the body
        """
        input = self._owner.get_concentration(self._chem)
        return input

class FoodLobe(Lobe):
    
    def set_direction(self,direction):
        """
        Sets the "direction" that this lobe looks at. Essentially is a tuple of [-2 to 2, -2 to 2]. This modified by heading and position, gives the space that the node looks at.
        Maybe a tuple of 1 or -1 [1,1] or [-1,1] etc
        """
        self._direction = direction

    def input_action(self):
        """
        Checks if food exists on this space and then activates all food chem lobes on this item of food, and returns that result.
        """
        food = self._owner.get_food_at_space(self._direction)
        if food is not None:
            return self._owner.activate_food_chem_lobes(food)
        return 0

class FoodChemLobe(Lobe):
    """
    Represents a lobe specialized at reading the concentration of a chemical in a food item
    """
    def set_chem(self,chem):
        """
        Sets the chemical to read
        """
        self._chem = chem

    def input_action(self, food):
        """
        Gets the concentration of a chemical in a food item.
        """
        try:
            # Maybe change this to proportion instead of full amount
            return food._chems[self._chem]/food._size
        except:
            return 0

class EnergyLobe(Lobe):
    """
    A lobe specialized in reading the energy levels of the organism
    """
    def input_action(self):
        """
        Get energy as a percentage
        """
        input = self._owner.get_energy_percent()
        return input

class Brain(Lobe):
    """
    Represents an entire brain with a set of lobes. The outputs are tied to the available options of the simulator
    """
    def __init__(self, owner):
        self._lobes = []
        self._food_chem_lobes = []
        self._internal_lobes = []
        self._sensory_lobes = []
        self._owner = owner
        self._genome = None

    def add_lobe(self, lobe):
        """
        Add a new lobe to the brain
        """
        self._lobes.append(lobe)

    def add_food_chem_lobe(self, lobe):
        self.add_lobe(lobe)
        self._food_chem_lobes.append(lobe)

    def add_internal_lobe(self, lobe):
        self.add_lobe(lobe)
        self._internal_lobes.append(lobe)
    
    def add_sensory_lobe(self,lobe):
        self.add_lobe(lobe)
        self._sensory_lobes.append(lobe)

    def input_action(self, val=None):
        """
        Gets the outputs of each lobe contained in the brain and sums them. This becomes the input for the brains learnable NN
        """
        total = 0
        for lobe in self._internal_lobes:
            total += lobe.get_output()
        for lobe in self._sensory_lobes:
            total += lobe.get_output()
        return total

    def get_output(self, debug = False):
        """
        Gets the final outputs of the brains learnable NN
        """
        if debug is False:
            inputs = [self.input_action() for i in range(self._width_layers)]
        else:
            inputs = [debug for i in range(self._width_layers)]
        for i in range(self._num_layers):
            outputs = [0 for _ in range(self._width_layers)]
            for j in range(self._width_layers):
                node = self._hidden[i][j]
                outs = node.get_output(inputs[j])
                for q in range(len(outs)):
                    outputs[q] += outs[q]
            inputs = outputs
        return inputs

    def decide_action(self):
        """
        Gets the output of the neural net, and returns the index of the highest rated action. This index corresponds to the action to take.
        """
        outs = get_output()[:4]
        return outs.index(max(outs))
        
def linear(input):
    return input

def relu(input):
    return max(0, input)

def sigmoid(input):
    return 1 / (1+(np.e**-input))

def tanh(input):
    return 2 * sigmoid(2*input) - 1
