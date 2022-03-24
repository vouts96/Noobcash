from datetime import date, datetime
import transaction
import json
from binascii import unhexlify, hexlify
from hashlib import sha256
from Crypto.Hash import SHA
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA



class Block:
	def __init__(self):

		self.index = 0
		self.timestamp = datetime.now()
		self.transactions = []
		self.nonce = 0
		self.previous_hash = 0
		self.hash = 0
		
		
def create_block(b, index, transactions, previous_hash):
    b.index = index    
    b.transactions = transactions 
    b.previous_hash = previous_hash
    b.hash = stringify(b)

    return b	

def stringify(self):
    stringed = str(self.index) + str(self.timestamp) + str(self.transactions) + str(self.nonce) + str(self.previous_hash)
    #print(sha256(stringed.encode('ascii')).hexdigest())
    return sha256(stringed.encode('ascii')).hexdigest()
	

'''def stringify(b):
	stringed = str(b.index) + str(b.previous_hash) + str(b.nonce) + str(b.timestamp) + str(b.transactions)
	return stringed'''

