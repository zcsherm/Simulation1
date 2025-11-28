"""
Creates a class for the genome in which the entire genome is saved into chunks and is a singly linked list
"""

class Node:
    """
    Each node points to the next node in the genome. Contains the bits as the start (opcode), the parameters of the structure, and then all non-coding sections following it. Genome segments must be passed as bytes, and then are prepended with 1 (to preserve leading 0s) and converted to binary(save space while stored in mem). Using the segments means needing to drop the leading 1
    """
    def __init__(self):
        self._start = None
        self._params = None 
        self._noncoding = None
        self.next = None

    def get_structure_genome(self):
        """
        Return the gene for this node
        Test to confirm this works correctly and doesnt add or lose values.
        """
        return self.get_start() + self.get_params() + self.get_noncoding()

    def set_start(self, start):
        # Sets the start code of the node, prepends a 1 and converts to binary
        self._start = bin(int(b'1'+start,2))

    def set_params(self, params):
        """
        # Sets the parameter portion of the node, prepends a 1 and converts to binary
        """
        self._params = bin(int(b'1'+params,2))

    def set_noncoding(self, noncoding):
        """
        Sets the noncoding section of the node, prepends a 1 and converts to binary
        """
        self._noncoding = bin(int(b'1'+noncoding,2))

    def get_start(self):
        """
        Convert the binary portion into a byte string and remove the prepended one
        """
        if self._start is None:
            return b''
        return bytes(str(self._start)[3:],'utf-8')
        
    def get_params(self):
        """
        Convert the binary portion into a byte string and remove the prepended one
        """
        if self._params is None:
            return b''
        return bytes(str(self._params)[3:],'utf-8')

    def get_noncoding(self):
        """
        Convert the binary portion into a byte string and remove the prepended one
        """
        if self._noncoding is None:
            return b''
        return bytes(str(self._noncoding)[3:],'utf-8')

    def get_next(self):
        """
        Get the next node of dna
        """
        return self.next

    def get_entire_genome(self):
        """
        Returns the entire dna strand from this node onwards
        """
        val = self.get_structure_genome()
        if self.next is not None:
            val += self.next.get_entire_genome()
        return val
