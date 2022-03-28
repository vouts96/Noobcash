from flask import Flask
from flask import jsonify 
import socket
import wallet
import block
import transaction
import requests
from requests.models import Response
import json
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
		self.current_block = []
		self.ring = []

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
			node_vitals = {}
			node_vitals["id"] = len(self.ring)
			node_vitals["address"] = ip + ":" + port
			node_vitals["public_key"] = public_key

			self.ring.append(node_vitals)

			if(len(self.ring) == self.N):
				for i in range(1, self.N):
					url = self.ring[i]["address"] + "/broadcast/ring"
					data = {}
					data = {"ring": json.dumps(self.ring)}
					resp = requests.post(url, data)

				return resp

			if(len(self.ring) > self.N ):
				print("Maximum number of nodes reached")

	def create_genesis_block(capacity, difficulty):
		print("Genesis Block created")
	









