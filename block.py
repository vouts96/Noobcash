from datetime import date, datetime
import transaction
import json
from binascii import unhexlify, hexlify
from hashlib import sha256
from Crypto.Hash import SHA
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA
import Crypto.Random.random as random



class Block:
	def __init__(self, block_index, prev_hash, transaction_list, difficulty):

		self.index = block_index
		self.previous_hash = prev_hash
		self.timestamp = datetime.timestamp(datetime.now())
		self.transactions = transaction_list
		if(block_index == 0):
			self.nonce = 0
		else:
			self.nonce = random.randint(0, 2**32-1)
		
		# hash to be created by function considering also the difficulty bits
		self.hash = self.hashing()
		self.difficulty = difficulty
		
	def serialize(self):
		return self.__dict__

	def hashing(self):
		stringed = str(self.index) + str(self.timestamp) + str(self.transactions) + str(self.previous_hash) + str(self.nonce)
		#print(sha256(stringed.encode('ascii')).hexdigest())
		hashed = sha256(stringed.encode('ascii')).hexdigest()
		return hashed
	
	def get_created_block(self, index, timestamp, transactions, previous_hash, nonce, hash):
		self.index = index
		self.timestamp = timestamp
		self.transactions = transactions
		self.previous_hash = previous_hash
		self.nonce = nonce
		self.hash = hash
	
