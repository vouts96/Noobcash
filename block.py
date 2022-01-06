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

	
	

def calculateHash():
	#calculate self.hash
	return 'hi'

def createGenesisBlock():
	gen = Block()
	gen.previous_hash = 1
	
