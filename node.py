from flask import Flask
from flask import jsonify 
import socket
import wallet
import block
import transaction
import requests
from requests.models import Response
import json
from json import JSONEncoder
#import rsa
import sys
import time


class Node:
	def __init__(self, bootstrap, N, ip, port):
		
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
			print(json.dumps(data, indent=4))
			url = ip + ":" + port + "/current_data"
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
			#add transaction to current block
			self.add_transaction_to_block(first_transaction, difficulty)
			print("Genesis Block created")
	
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
		
		if balance >= amount:
			tx = transaction.Transaction(self.wallet.public_key, self.wallet.private_key, recipient, amount, transaction_list)
			start_time = time.time()
			for i in range(len(self.ring)):
				url = self.ring[i]["address"] + "/broadcast/transaction"
				self.broadcast_transaction(tx, url, start_time)

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


	def validate_transaction(self):
		print("Transcation validated")
	
	def add_transaction_to_block(self, transaction, difficulty):

		self.current_block.transactions.append(transaction.serialize())
		self.current_block.hash = self.current_block.hashing(difficulty)			

		# we should write some code for handling a full block
		# when trying to add a new transaction to current block
		# e.g. start to mine the block etc.








