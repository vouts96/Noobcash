from binascii import hexlify
from Crypto.PublicKey import RSA

from time import time
from urllib.parse import urlparse
from uuid import uuid4



class wallet:

	def __init__(self):
		
		key = RSA.generate(1024)
		self.private_key = hexlify(key.exportKey(format='DER')).decode('ascii')
		pub_key = key.publickey()
		self.public_key = hexlify(pub_key.exportKey(format='DER')).decode('ascii')
		self.address = 0
		self.transactions = []

	def balance():
		return 0