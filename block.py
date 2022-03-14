from datetime import date, datetime
import transaction



class Block:
	def __init__(self):

		self.index = 0
		self.previous_hash = 0
		self.hash = 0
		self.nonce = 0
		self.timestamp = datetime.now()
		self.transactions = []

	

def stringify(b):
	stringed = str(b.index) + str(b.previous_hash) + str(b.nonce) + str(b.timestamp) + str(b.transactions)
	return stringed

'''
def calculateHash():
	#calculate self.hash
	return 'hi'

def createGenesisBlock():
	genesis = Block()
	genesis.previous_hash = 1

	return genesis
	'''
