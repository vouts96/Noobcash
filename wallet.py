import binascii
import node
import string 
import random

#import Crypto
#import Crypto.Random
#from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
#from Crypto.Signature import PKCS1_v1_5

import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4



class wallet:

	def __init__(self):
		##set

		self.public_key = 0
		self.private_key = 0
		self.address = 0
		self.transactions = []

	def balance():
		return 0



def generate_wallet(ip_address):
	w = wallet()

	w.address = ip_address
	
	key = RSA.generate(2048)
	f = open('mykey.pem','wb')
	f.write(key.export_key('PEM'))
	print(key.export_key('PEM'))
	f.close()

	f = open('mykey.pem','r')
	key = RSA.import_key(f.read())
	#print(w.private_key)
	print(key)

	return w


generate_wallet('dasda')
