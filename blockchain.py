import block
from llist import dllist, dllistnode



class Βlockchain:
    def __init__(self):

        # list of blocks added to be added to chain
        # these blocks are vaildated
        self.chain = []

    def serialize(self):
        return self.__dict__
    
    def add_block_to_chain(self, block):
        self.chain.append(block)