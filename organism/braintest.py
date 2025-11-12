import unittest
from Brain import *
import random


class MyTestCase(unittest.TestCase):
    def test_something(self):
        # Set output
        final_node = Node()
        final_node.set_function(linear)
        final_node.set_weights([1])
        lobe = Lobe(None)
        lobe.set_num_layers(3)
        lobe.set_width_layers(3)
        lobe.set_final_node(final_node)
        # Make a 3x3 lobe
        w1 = [.4,-.9,.01]
        w2 = [-.1,.1,-.4]
        w3 = [.8,-1,.5]
        for i in range(3):
            layer = []
            for j in range(3):
                new = Node()
                if i == 2:
                    new.set_weights(random.choice(w1+w2+w3))
                else:
                    new.set_weights(random.choice([w1,w2,w3]))
                new.set_function(random.choice([linear,relu,sigmoid,tanh]))
                layer.append(new)
            lobe.add_layer(layer)
        print(lobe.get_output(1))
        for i in range(-50,50):
            print(f"Input = {i/10}, output = {lobe.get_output(i/10)}")

if __name__ == '__main__':
    unittest.main()
