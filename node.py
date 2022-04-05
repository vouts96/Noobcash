from flask import Flask
from flask import jsonify 
import socket
import wallet
import block
import blockchain
import transaction
import app
import requests
from requests.models import Response
import json
from json import JSONEncoder
#import rsa
import sys
import time
from binascii import unhexlify, hexlify
from hashlib import sha256
from Crypto.Hash import SHA
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA


class Node:
	def __init__(self, bootstrap, N, ip, port, capacity, difficulty):
		
		##set
		self.N = N
		self.id = 0
		self.NBC = 0
		self.ip_address = ip
		self.port = port
		self.wallet = wallet.wallet()
		self.chain = []
		self.transaction_list = []
		self.current_block = block.Block(0,0, [], 0)
		self.ring = []
		self.chain = blockchain.Blockchain()
		self.capacity = capacity
		self.difficulty = difficulty
		

		# utxos is a list of the current sum of all utxos for every wallet
		self.utxos = []

		if(bootstrap):
			print("Creating bootstrap node...")
			bootstrap_vitals = {}
			bootstrap_vitals["id"] = self.id
			bootstrap_vitals["address"] = ip + ":" + port
			bootstrap_vitals["public_key"] = self.wallet.public_key

			self.ring.append(bootstrap_vitals)
	
	def create_new_node(self, bootstrap):
		if(bootstrap == 0):
			data = {}
			data["public_key"] = self.wallet.public_key
			data["ip"] = self.ip_address
			data["port"] = self.port
			url = "http://localhost:5000/newnode"
			resp = requests.post(url, data)
			return resp

	def register_node(self, bootstrap, ip, port, public_key):
		# function to register nodes to ring
		# only called by bootstrap node
		if(bootstrap):
			new_node_id = len(self.ring)
			node_vitals = {}
			node_vitals["id"] = new_node_id
			node_vitals["address"] = ip + ":" + port
			node_vitals["public_key"] = public_key
			node_vitals["utxos"] = []

			self.ring.append(node_vitals)

			
			# must create a request to post to /original_data
			# data to post: blockchain

			data = {}
			data['id'] = new_node_id
			data['utxos'] = self.utxos
			data['current_block'] = self.current_block.serialize()
			data['current_chain'] = self.chain.serialize()
			print(data['current_chain'])
			print(json.dumps(data, indent=4))
			url = ip + ":" + port + "/current_chain"
			r = requests.post(url, data = json.dumps(data))
			

			if(len(self.ring) == self.N):
				for i in range(1, self.N):
					url = self.ring[i]["address"] + "/broadcast/ring"
					data = {}
					data = {"ring": json.dumps(self.ring)}
					resp = requests.post(url, data)
					
				return resp

			if(len(self.ring) > self.N ):
				print("Maximum number of nodes reached")

	def create_genesis_block(self, capacity, difficulty):
		if(self.id == 0):
	
			first_transaction = transaction.Transaction("0", self.wallet.private_key, self.wallet.public_key, 100*self.N, [])
			first_utxo = {'id': first_transaction.transaction_id, 'previous_transaction_id': -1, 'amount': first_transaction.amount, 'recipient': self.wallet.public_key}
			self.utxos.append(first_utxo)
			self.current_block = block.Block(0, 1, [], difficulty)
			# add transaction to current block
			self.add_transaction_to_block(first_transaction, capacity, difficulty)
			# add genesis block to blockchain
			self.chain.add_block_to_chain(self.current_block)
			print("Genesis Block created and appended to blockchain")
	
	def create_transaction(self, recipient, amount):

		transaction_list = []
		balance = 0
		for u in self.utxos:
			if(balance < amount):
				if(u["recipient"]==self.wallet.public_key):
					balance += u["amount"] 
					transaction_list.append(u)
			else:
				break
		print('my balance: ' + str(balance))
		if balance >= amount:
			tx = transaction.Transaction(self.wallet.public_key, self.wallet.private_key, recipient, amount, transaction_list)
			start_time = time.time()
			for i in range(len(self.ring)):
				url = self.ring[i]["address"] + "/broadcast/transaction"
				self.broadcast_transaction(tx, url, start_time)
				#self.add_transaction_to_block(tx, self.capacity, self.difficulty)

		else:
			return "Error creating transaction"
		
		return "New transaction created"
	

	def broadcast_transaction(self, transaction, url, start_time):
		
		data = {}
		data = {'transaction': json.dumps(transaction.serialize()), 'timestamp': start_time}
		#data['transaction'] = transaction.serialize()
		#data['timestamp'] = start_time

		resp = requests.post(url, data)
		
		#if resp.status_code == 200:
		#	transaction.transaction_outputs = resp.json()["outputs"]
		

	def broadcast_block(self, block, url):
		data={}
		data['block'] = json.dumps(block)
		data['sender'] = self.id
		resp = requests.post(url, data)

	def verify_signature(self, transaction):
		key = RSA.importKey(unhexlify(transaction.sender_address))
		verifier = PKCS1_v1_5.new(key)
		h = SHA.new(transaction.hashing().encode('utf8'))
		if not verifier.verify(h, unhexlify(transaction.signature)):
			raise ValueError("Not valid Signature")
		else:
			return 1

	def validate_transaction(self, transaction):
		
		valid = True
		for utxo_in in transaction.transaction_inputs:
			if ((utxo_in["id"] not in [utxo["id"] for utxo in self.utxos]) or utxo_in["recipient"] != transaction.sender_address):
				valid = False
				break
		
		if (self.verify_signature(transaction) and valid):	
			index = []
			temp = [(i,utxo["id"]) for i,utxo in enumerate(self.utxos)]

			for utxo_in in transaction.transaction_inputs:
				for i,x in temp:
					if x==utxo_in["id"]:
						index.append(i)

			# something's wrong here 
			idx = [i for i in range(len(self.utxos)) if i not in index]
			# ----------------------s
			'''change_utxo = {}
			change_utxo["id"] = transaction.transaction_id+"0"
			change_utxo["previous_trans_id"] = transaction.transaction_id
			# balance function does not exist in node we have to create it
			change_utxo["amount"] = self.balance(transaction.sender_address,transaction.transaction_inputs)-transaction.amount
			# ------------------------------------------------------------
			change_utxo["recipient"] = transaction.sender_address.decode()

			transaction.transaction_outputs.append(change_utxo)

			recipient_utxo = {}
			recipient_utxo["id"] = transaction.transaction_id+"1"
			recipient_utxo["previous_trans_id"] = transaction.transaction_id 
			recipient_utxo["amount"] = transaction.amount
			recipient_utxo["recipient"] = transaction.receiver_address.decode()
			self.utxos = [self.utxos[x] for x in idx]
			if change_utxo["amount"] != 0:
				self.utxos.append(change_utxo)
			self.utxos.append(recipient_utxo)
			transaction.transaction_outputs.append(recipient_utxo)'''

			return 1
		else:
			return 1
		
		#print("Transcation validated")
	
	def add_transaction_to_block(self, transaction, capacity, difficulty):
		
		self.current_block.transactions.append(transaction.serialize())
		if(transaction.sender_address != "0"):
			#print('transaction_list_length: ' + str(len(self.current_block.transactions)))
			if len(self.current_block.transactions) == capacity:
				print('Current block reached its limit. Time to mine!')

		self.current_block.hash = self.current_block.hashing()			

		# we should write some code for handling a full block
		# when trying to add a new transaction to current block
		# e.g. start to mine the block etc.








