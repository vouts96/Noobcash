import binascii
#import node
import string 
import random

#import Crypto
#import Crypto.Random
import rsa
import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4



class wallet:

	def __init__(self):
		
		self.public_key = 0
		self.private_key = 0
		self.address = 0
		self.transactions = []

	def balance():
		return 0



def generate_wallet(ip_address):
	
	w = wallet()

	w.address = ip_address
	
	w.public_key, w.private_key = rsa.newkeys(512)

	#print(w.public_key)
	#print(w.private_key)

	return w
 
	

'''
def dummy_hash():
	
	public_key, private_key = rsa.newkeys(512)

#	data = ['32131', 2232, 43243242, 42342432, 'dsfsdfsd']

	data = 'affsdfsdfsds'.encode()
	data2 = 'afdsadadafsdfsdfsds'.encode()
	hash = rsa.compute_hash(data, 'SHA-1')
	signature = rsa.sign_hash(hash, private_key, 'SHA-1')
	rsa.verify(data2, signature, public_key)


	print(hash)
	print(signature)

dummy_hash()'''