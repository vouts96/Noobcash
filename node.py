from flask import Flask
from flask import jsonify 
import wallet
import block
import blockchain
import transaction
import requests
from requests.models import Response
import json
from json import JSONEncoder
import time
from binascii import unhexlify, hexlify
from hashlib import sha256
from Crypto.Hash import SHA
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA
from datetime import datetime
import threading


class Node:
	def __init__(self, bootstrap, N, ip, port, capacity, difficulty):
		
		##set
		self.N = N
		self.id = 0
		self.ip_address = ip
		self.port = port
		self.wallet = wallet.wallet()
		self.transaction_list = []
		self.current_block = block.Block(0,0, [], difficulty)	# create a dummy block
		self.temp_block = block.Block(0,0, [], difficulty)	# create a dummy block
		self.ring = []
		self.chain = blockchain.Blockchain()
		self.capacity = capacity
		self.difficulty = difficulty
		self.has_conflict = False
		self.total_mining_time = 0
		self.total_minings = 0
		

		# utxos is a list of the current sum of all utxos for every wallet
		self.utxos = []

		if(bootstrap):
			print("Creating bootstrap node...")
			bootstrap_vitals = {}
			bootstrap_vitals["id"] = self.id
			bootstrap_vitals["address"] = ip + ":" + port
			bootstrap_vitals["public_key"] = self.wallet.public_key
			bootstrap_vitals["utxos"] = []

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
			#print(data['current_chain'])
			#print(json.dumps(data, indent=4))
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
	
	def create_new_block(self, difficulty, transaction_list):
		new_block = block.Block(len(self.chain.chain), self.chain.chain[-1].hash, transaction_list, difficulty)
		return new_block

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
		#print('my balance: ' + str(balance))
		threads = []
		if balance >= amount:
			tx = transaction.Transaction(self.wallet.public_key, self.wallet.private_key, recipient, amount, transaction_list)
			start_time = time.time()
			for i in range(len(self.ring)):
				url = self.ring[i]["address"] + "/broadcast/transaction"
				thread = threading.Thread(target=self.broadcast_transaction, args = (tx, url, start_time))
				thread.start()
				threads.append(thread)
				#self.broadcast_transaction(tx, url, start_time)
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
			# the (utxo_in["id"] not in [utxo["id"] for utxo in self.utxos]) fails for first transaction from bootstrap to nodes
			# because there are no utxos in the node, self.utxos is empty
			if (utxo_in["recipient"] != transaction.sender_address):
				valid = False
				break
			
		
		#print(valid)
		#print(self.verify_signature(transaction))
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
			change_utxo = {}
			
			change_utxo["id"] = transaction.transaction_id+"0"
			change_utxo["previous_trans_id"] = transaction.transaction_id
			change_utxo["amount"] = self.balance(transaction.sender_address,transaction.transaction_inputs)-transaction.amount
			change_utxo["recipient"] = transaction.sender_address
			
			
			transaction.transaction_outputs.append(change_utxo)
			
			recipient_utxo = {}
			recipient_utxo["id"] = transaction.transaction_id+"1"
			recipient_utxo["previous_trans_id"] = transaction.transaction_id 
			recipient_utxo["amount"] = transaction.amount
			recipient_utxo["recipient"] = transaction.receiver_address
			
			self.utxos = [self.utxos[x] for x in idx]
			if change_utxo["amount"] != 0:
				self.utxos.append(change_utxo)
			self.utxos.append(recipient_utxo)
			transaction.transaction_outputs.append(recipient_utxo)

			return 1
		else:
			return 0
		
		#print("Transcation validated")
	
	def balance(self,recipient,utxos):
		total = 0
		for utxo in utxos:
			if (utxo["recipient"]==recipient):
				total += utxo["amount"]
		return total

	def add_transaction_to_block(self, transaction, capacity, difficulty):
		
		self.current_block.transactions.append(transaction.serialize())
		if(transaction.sender_address != "0"):
			if len(self.current_block.transactions) == capacity:
				
				if(self.current_block.index == 0):
					self.chain.add_block_to_chain(self.current_block)
					print("Added Genesis Block to chain")
				else:
					print('Current block reached its limit. Time to mine!')
					if self.mine_block(int(difficulty)):
						self.chain.add_block_to_chain(self.current_block)
						print("Block appended to blockchain")				

				self.create_new_block(difficulty, [])

		# we should write some code for handling a full block
		# when trying to add a new transaction to current block
		# e.g. start to mine the block etc.


	def mine_block(self, difficulty):
		length = len(self.chain.chain)

		# set index for current block based on the last block index of blockchain 
		index = self.chain.chain[length-1].index + 1
		self.current_block.index = index

		# get previous hash for current block from last block of blockchain
		previous_hash = self.chain.chain[length-1].hash
		self.current_block.previous_hash = previous_hash

		# generate a new timestamp for current block 
		self.current_block.timestamp = datetime.timestamp(datetime.now())
		
		# generate a hash for current block
		#self.current_block.hash = self.current_block.hashing

		self.current_block.difficulty = difficulty

		start_time = time.time()
		flag = False
		
		#print(self.current_block.nonce)
		

		while True:
			if(self.count_zeros(self.current_block.hash) < self.current_block.difficulty):
				self.current_block.nonce = self.current_block.nonce + 1 
				self.current_block.hash = self.current_block.hashing()
			else:
				flag = True
				break;

		if(flag):
			mining_time = time.time()-start_time
			print('NONCE FOUND: ')
			print(self.current_block.nonce)
			threads = []
			for i in range(len(self.ring)):
				url = self.ring[i]["address"] + "/broadcast/block"
				thread = threading.Thread(target=self.broadcast_block, args = (self.current_block, url))
				thread.start()
				threads.append(thread)

			for t in threads:
					t.join()
			# we use these fields to calculate average block time: total_mining_time / total_minings
			self.total_mining_time += mining_time
			self.total_minings += 1

			return 1

		else:
			print("Block was not mined")
			return 0

	def broadcast_block(self, block, url):
		data = {}
		data['block'] = block.serialize()
		data['sender'] = self.id
		resp = requests.post(url, data = json.dumps(data))		

	def count_zeros(self, hash):
		counter = 0
		i = 0
		while 1:
			if hash[i] == '0':
				counter = counter + 1
				i = i + 1
			else:
				break
		return counter

	def validate_block(self, block, difficulty, chain):

		if block.index != 0:
			if block.index > len(chain.chain):
				index = -1
			else:
				index = block.index - 1
			
			if block.previous_hash == chain.chain[index].hash:
				return 1
			elif block.previous_hash != chain.chain[index].hash:
				self.has_conflict = True
				print("Resolving blockchain conflicts...\n")
				
				if self.resolve_conflict(difficulty):
					self.has_conflict = False
				
				return 0
		# we get here only on genesis block
		return 1
	
	def resolve_conflict(self, difficulty):
		print("Conflcit resolved")