"""
DNA decodes a brain made up of lobes. Each lobe is a mini neural net that is simple feed forward. The very first node in the brain is the top level "Thinking node". This takes in all inputs from subnodes, goes through mutable neural net, and decides on an action (4 ourputs, EAT, Turn, Forward, NOP).
Lobe types:
    Chem internal input (single chem)
    Food input (single space)
    Chemical food input (single chem from food) Tied to food input, 
    Energy input 

Input vector: Chem0-15, 
"""
import numpy as np
class Node:
    def __init__(self):
        self._bias = .01

    def set_bias(self, bias):
        self._bias = bias

    def set_weights(self, weights):
        self._weights = weights

    def set_function(self, function):
        self._function = function

    def get_output(self, inputs):
        out = self._function((inputs)+self._bias))
        weighted = [out*weight for weight in self._weights]
        return weighted

class Lobe:
    def __init__(self, creature):
        self._hidden = []
        self._owner = creature
    
    def set_final_node(self, node):
        self._final = node

    def set_num_layers(self, num):
        """
        Maybe 1-2?
        """
        self._num_layers = num

    def set_width_layers(self, num):
        """
        Maybe 1-4
        """
        self._width_layers = num

    def add_layer(self, nodes):
        self._hidden.append(layer)

    def input_action(self):
        return 1
        
    def get_output(self):
        inputs = [self.input_action * self._width_layers]
        for i in range(self._num_layers):
            if i == self._num_layers - 1:
                outputs = [0]
            else:
                outputs = [0 * width_layers]
            for j in range(self._width_layers):
                node = self._hidden[i][j]
                outs = node.get_output(inputs[j])
                for q in range(len(outs)):
                    outputs[q] += outs[q]
            inputs = outputs
        final_output = self._final.get_outputs(outputs[0])[0]
        return final_output
        
class ChemLobe(Lobe):

    def set_chem(self, chem):
        self._chem = chem
        
    def input_action(self):
        input = self._owner.get_concentration(self._chem)
        return input

class FoodLobe(Lobe):
    pass

class FoodChemLobe(Lobe):
    pass

class EnergyLobe(Lobe):
    def input_action(self):
        input = self._owner.get_energy()
            
def linear(input):
    return input

def relu(input):
    return max(0, input)

def sigmoid(input):
    return 1 / (1+(np.e**-x))

def tanh(input):
    return 2 * sigmoid(2*input) - 1
