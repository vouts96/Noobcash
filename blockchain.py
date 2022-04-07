import block



class Blockchain:
    def __init__(self):

        # list of blocks added to be added to chain
        # these blocks are vaildated
        self.chain = []

    def serialize(self):
        dict_chain = []
        for b in self.chain:
            b = b.serialize()
            dict_chain.append(b)
        return dict_chain
    
    def add_block_to_chain(self, block):
        self.chain.append(block)

    def get_created_chain(self, chain):
        self.chain = []
        for b in chain:
            b_temp = block.Block(0,0, [], 0)
            b_temp.get_created_block(b['index'], b['previous_hash'], b['timestamp'], b['transactions'], b['nonce'], b['hash'])
            self.chain.append(b_temp)

        