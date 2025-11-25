# handles reading a genome
from Body import *
from Organ import *
from BioChemGene import *
from Chemicals import *
from Genome import *
from utilities import *
from Brain import *

GENE_READ_LENGTH = 4
GENE_TYPES = 3
GENE_OPCODES = [0b11010]
GENE_LOWER_LIMIT = 100
GENE_UPPER_LIMIT = 120
ORGAN_OPCODES = [0b11111]
ORGAN_LOWER_LIMIT = 200
ORGAN_UPPER_LIMIT = 204
ENERGY_LOWER_LIMIT = 40
ENERGY_UPPER_LIMIT = 60
LOBE_LOWER_LIMIT = 20
LOBE_UPPER_LIMIT = 140
NORMAL_READ_LENGTH = 8 # used to be 5
ENERGY_AMOUNT = 1
class Decoder:
    """
    A second decoder for when the genome is stored as linked list
    """
    def __init__(self):
        """
        Initialize to begin reading a dna strand
        """
        self._genome = None
        self._current_pos = 1
        self._current_organism = Body()
        self._current_organ = None
        self._current_gene = None
        self._current_read = b''
        self._current_node = Node()
        # Create a map for how many bits to read to assemble a function
        self._bits_for_funcs = dict(zip(func_names, bits_needed))
        self._brain_genome = None
        self._current_lobe = None
        self._current_brain = None

    def set_genome(self, genome):
        """
        Sets the active genome. Genome passed should be a byte string of the genome, ideally obtained from the parent.genome_head object
        """
        self._genome = b'1' + genome # prepend a 1 to prevent leading zero discrepensies

    def set_brain_genome(self, genome):
        """
        Same thing here, just for the brain
        """
        self._brain_genome = genome
        
    def finish_organism(self):
        """
        On reading the whole strand, the organism will be finished, and the decoder will be reset
        """
        if self._current_organ is not None:
            if self._current_gene is not None:
                self._current_node.set_noncoding(self._current_read)
                self._current_gene.set_dna_head(self._current_node)
            else:
                self._current_organ.set_dna_head(self._current_node)
            self._current_organism.add_organ(self._current_organ)
        self._current_read=b''
        self.read_brain()
        creature = self._current_organism
        self._current_organism = Body()
        self._genome = None
        self._brain_genome = None
        self._current_pos = 1
        self._current_organ = None
        self._current_gene = None
        self._current_node = Node()
        return creature
    
    def read_at_pos(self, pos=None, length = NORMAL_READ_LENGTH):
        """
        Reads a section of Binary DNA, at a starting position and with a length
        """
        if pos == None:
            pos = self._current_pos
        if length == 0:
            return b''
        if pos >= len(self._genome):
            self._current_pos = len(self._genome)
            return b''
        if pos + length >= len(self._genome):
            self._current_pos = len(self._genome)
            return b''
            
        val = self._genome[pos:(pos+length)]
        if pos == self._current_pos:
            self._current_pos += length
        return val

    def read_genome(self):
        """
        Continually reads the genome, constructing an organism as it goes.
        """
        while self._current_pos < (len(self._genome)-1)-100:
            read_val = self.read_at_pos()  # Returns a byte string
            # If the gene start code was encountered begin constructing a gene, unless no organ exists to house it
            if GENE_LOWER_LIMIT <= int(read_val,2) <= GENE_UPPER_LIMIT and self._current_organ is not None:
                self.start_new_node('gene') # Finish the previously read node, begin a new one
                self._current_node.set_start(read_val) # Assign the start value
                self.read_gene_data() # Start reading it

            # If the organ start code was encountered, begin constructing an organ
            elif ORGAN_LOWER_LIMIT <= int(read_val,2) <= ORGAN_UPPER_LIMIT:
                self.start_new_node('organ')
                self._current_node.set_start(read_val)
                self.read_organ_data()
                self._current_gene = None # resets the active gene so that we can use this as aflag as well
            else:
                # If a certain value is read in the organs non-coding, add a 'fat storage' unit. Like how fatty it is.
                if self._current_gene == None and self._current_organ:
                    if ENERGY_LOWER_LIMIT <= int(read_val,2) <= ENERGY_UPPER_LIMIT:
                        self._current_organ.increase_energy_capacity(ENERGY_AMOUNT)
                self._current_read += read_val
        if self._current_pos < (len(self._genome)):
            self._current_read += self._genome[self._current_pos:]
        # Finalize the organism and return it when complete.
        final = self.finish_organism()
        return final

    def read_organ_data(self):
        """
        Reads organ data (right now, only has 3 parameters: health, activation, and reaction), constructs the organ.
        """
        # Assign the current organism the previously active organ
        if self._current_organ is not None:
            self._current_organism.add_organ(self._current_organ)
            
        # Create a new organ and get the parameters.
        self._current_organ = InternalOrgan('internal', self._current_organism)
        self._current_organ.set_def_health()
        val = self.read_at_pos(length=5)
        read = val
        self._current_organ.set_reaction_rate(int(val,2)/32)
        val = self.read_at_pos(length=5)
        read += val
        self._current_organ.set_act_rate(int(val,2)/32)
        self._current_node.set_params(read)
        return

    def read_gene_data(self):
        """
        Constructs a gene (currently only 2 types (emitter, and receptor))) and gets parameters for it.
        """
        # Find out what type of gene it is
        type = self.read_at_pos(length = GENE_READ_LENGTH)
        read = type
        type = int(type,2) % GENE_TYPES
        if type == 2:
            # It's gonna be easier to separate all the logic into separate functions instead
            self._current_gene = Reaction(self._current_organ, 'reaction')
            self.read_reaction_data()
            return
        elif type == 1:
            self._current_gene = Emitter(self._current_organ, 'emitter')
            rate = self.read_at_pos(length=5)
            read += rate
            self._current_gene.set_output_rate(int(rate,2))
        elif type == 0:
            self._current_gene = Receptor(self._current_organ, 'receptor')
        
        # Now parse the function this gene uses. Each function needs different parameters
        func = self.read_at_pos(length = 3)
        read += func
        func = int(func,2)
        func_name = func_names[func]
        func_read_lengths = bits_needed[func]
        params = []
        # If the function needs parameters, then read each one as needed
        for param in func_read_lengths:
            val = self.read_at_pos(length = param)
            read += val
            params.append(int(val,2))
        if params:
            function = functions[func](*params)
        else:
            function = functions[func]()
        self._current_gene.set_activation(func_name, function)

        # Now handle the other parameters of the gene
        val = self.read_at_pos(length = 4)
        read += val
        val = int(val,2) % self._current_organ.get_param_numbers()
        p=  self._current_organ._parameters[val]
        self._current_gene.set_parameter(p[0], p[1])
        val = self.read_at_pos(length = 4)
        read += val
        val = int(val,2)
        self._current_gene.set_chemical(val)
        self._current_organ.add_gene(self._current_gene)
        self._current_node.set_params(read)

    def read_reaction_data(self):
        """
        Reads the data for a reaction gene, need to expand to handle energy?
        """
        read = b'0010'
        if self._current_pos > len(self._genome)-50:
            return
        # Get how many variables on each side of equation
        left = self.read_at_pos(length = 4)
        right = self.read_at_pos(length = 4)
        read += left + right
        self._current_gene.set_num_of_chems_left(int(left,2))
        self._current_gene.set_num_of_chems_right(int(right,2))
        chems = []
        # Iterate and get the chems
        for i in range((int(left,2) % 2) + 1 + (int(right,2) % 3)):
            val = self.read_at_pos(length = 6)
            read += val
            chem = self.read_at_pos(length = 6)
            read += chem
            chems.append((int(val,2),int(chem,2)%20))
        self._current_gene.set_chems_and_coefficients(chems)
        self._current_organ.add_gene(self._current_gene)
        self._current_node.set_params(read)
        
    def start_new_node(self, type):
        """
        Generates a new DNA node
        """
        # Add the noncoding section the current node and establish the next
        self._current_node.set_noncoding(self._current_read)
        self._current_node.next = Node()
        self._current_read = b''
        
        if self._current_organ is None and type != 'lobe':
            # If organ opcode was encountered but no organ started yet, this is the first node
            self._current_organism.set_dna_head(self._current_node)

        # If organ opcode was encountered and no gene was constructed in the last one, then set this node to the previous organ
        elif type == 'organ':
            if self._current_gene is None:
                self._current_organ.set_dna_head(self._current_node)
            else:
                self._current_gene.set_dna_head(self._current_node)

        # Handle brain data, probably separate this out
        elif type == 'lobe':
            if self._current_lobe is None:
                self._current_brain.set_dna_head(self._current_node)
            else:
                self._current_lobe.set_dna_head(self._current_node)
        else:
            if self._current_gene is not None:
                self._current_gene.set_dna_head(self._current_node)
        
        self._current_node = self._current_node.next

    def read_brain(self):
        """
        Reads the brain genome and constructs a brain
        """
        # Setup a blank brain and a starting node
        if self._brain_genome is None:
            return
        self._current_pos = 0
        self._current_node = Node()
        self._current_brain = Brain()
        self._current_brain.set_owner(self._current_organism)
        self._genome = self._brain_genome
        
        # Setup the brains basic stuffs
        self.parse_brain_super()
        
        # Read through the genome
        while self._current_pos < (len(self._genome)-1)-250:
            read_val = self.read_at_pos()  # Returns a byte string
            
            # If a lobe start code was encountered, make that lobe
            if LOBE_LOWER_LIMIT <= int(read_val,2) <= LOBE_UPPER_LIMIT:
                self.start_new_node('lobe') # Finish the previously read node, begin a new one
                self._current_node.set_start(read_val) # Assign the start value
                self.read_lobe_data() # Start reading it
            else:
                # SLowly build the noncoding portion
                self._current_read += read_val
        # Tack on the last bit of DNA that was not decoded
        if self._current_pos < (len(self._genome)):
            self._current_read += self._genome[self._current_pos:]
            
        # Finish the brain
        self._current_node.set_noncoding(self._current_read)
        if self._current_lobe is None:
            self._current_brain.set_dna_head(self._current_node)
        else:
            self._current_lobe.set_dna_head(self._current_node)
        self._current_organism.set_brain(self._current_brain)
        return

    def parse_brain_super(self):
        """
        Reads the basic attributes of the brain organ
        """
        read_val = b''
        # Get width and layers
        layers = self.read_at_pos(length=1)
        read_val += layers
        width = self.read_at_pos(length = 1)
        read_val += width

        self._current_brain.set_num_layers(int(layers,2)+2)
        self._current_brain.set_width_layers(int(width,2)+4)

        # Get each node of the neural net
        val, hidden_layers = self.read_and_build_neural_net(int(layers,2)+2, int(width,2)+4)
        read_val += val
        for layer in hidden_layers:
            self._current_brain.add_layer(layer)
            
        self._current_node.set_params(read_val)

    def read_lobe_data(self):
        """
        Reads a new lobe with the following header
        Type: 4 bits
        Layers: 3 bits
        Width: 3 bits
        Param: 6 bits
        Then: Layers * Width * (2+6*Width) bits
        """
        # Get the type and dimensions of neural net
        read_val = b''
        type = self.read_at_pos(length=4)
        read_val += type
        layers = self.read_at_pos(length=3)
        read_val += layers
        width = self.read_at_pos(length=3)
        read_val += width
        param = self.read_at_pos(length=6)
        read_val += param
        typer = int(type,2)
        # Parse the read values
        types = [ChemLobe, FoodLobe, FoodChemLobe, EnergyLobe]
        lobe = types[typer%4]()
        lobe.set_owner(self._current_organism)
        print(int(width,2))
        print(int(layers,2))
        lobe.set_width_layers((int(width,2)%4) + 1)
        lobe.set_num_layers((int(layers,2) % 3) + 1)

        # Parse parameters
        if typer%4 == 0 or typer%4 == 2:
            lobe.set_chem(int(param,2) % 16)
        if typer%4 == 1:
            x  = (int(param) % 8) % 5 -2
            y = (int(param) // 8) % 5 -2
            lobe.set_direction([x,y])

        # Build the neuralnetwork
        val, hidden_layers = self.read_and_build_neural_net((int(layers,2) % 3) + 1, (int(width,2)%4) + 1)
        read_val += val
        for layer in hidden_layers:
            lobe.add_layer(layer)
        
        if type == 2:
            self._current_brain.add_food_chem_lobe(lobe)
        elif type == 1:
            self._current_brain.add_sensory_lobe(lobe)
        else:
            self._current_brain.add_internal_lobe(lobe)
        self._current_lobe = lobe
        self._current_node.set_params(read_val)

    
    def read_and_build_neural_net(self, layers, width):
        read_val =b''
        hidden_layers = []
        for i in range(layers):
            val, layer = self.build_neural_net_layer(width)
            read_val += val
            hidden_layers.append(layer)
        return read_val, hidden_layers

    def build_neural_net_layer(self,width):
        read_val = b''
        funcs = [linr, relu, tanh, sigmoid]
        layer = []
        for i in range(width):
            node = BrainNode()
            func = self.read_at_pos(length=2)
            read_val += func
            weights = []
            for _ in range(width):
                weight = self.read_at_pos(length=6)
                read_val += weight
                weight = (int(weight,2) - 31)/32
                weights.append(weight)
            node.set_function(funcs[int(func,2)])
            node.set_weights(weights)
            layer.append(node)
        return read_val, layer
