from crypt import methods
from ensurepip import bootstrap
from itertools import chain
from textwrap import indent
from traceback import print_tb
from binascii import unhexlify, hexlify
from hashlib import sha256
import flask
from flask import Flask
from flask import jsonify 
from flask import request
import node
import socket
import wallet
import block
import transaction
import requests
from requests.models import Response
from binascii import unhexlify, hexlify
from hashlib import sha256
from Crypto.Hash import SHA
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA
import json
#import rsa
import threading
import sys
import time

from argparse import ArgumentParser

app = Flask(__name__)


def create_node():
	req = new_node.create_new_node(arguments.node)
	if (req.status_code == 200):
		print("Creating new node...")
		time.sleep(0.5)
		print("New node created and registered in ring successfully!")


@app.route("/", methods = ['GET', 'POST'])
def index():
	return json.dumps(
			{'len': len(new_node.ring),
			'ip': new_node.ip_address, 
			'port': new_node.port, 
			'NBC': new_node.balance(new_node.wallet.public_key, new_node.utxos), 
			'ring': new_node.ring,
			'transaction_list': new_node.transaction_list,
			'UTXOS': new_node.utxos,
			'current_block': new_node.current_block.serialize()
			#'CHAIN': new_node.chain.serialize()
			}, indent=4)


@app.route("/newnode", methods = ['POST'])
def newnode():
	print("New node created successfuly!")
	public_key = request.form["public_key"]
	ip = request.form["ip"]
	port = request.form["port"]
	print("About to register new node...")
	new_node.register_node(arguments.node, ip, port, public_key)
	new_node.create_transaction(new_node.ring[-1]["public_key"], 100)
	print("New node registered successfully!")
	return 'New node registered successfully!'


@app.route("/broadcast/ring", methods = ['POST'])
def broadcast_ring():
	new_node.ring = json.loads(request.form["ring"])
	print("All nodes updated")
	return "All nodes updated"


@app.route("/broadcast/transaction", methods = ['GET', 'POST'])
def get_transaction():
	# This functions handles all incoming transactions.
	# The handling consists of four stages
	# First stage: Decode incoming transactions
	# Second stage: Insert incoming transaction to node's transaction list
	# Third stage: Validate transaction
	# Fourth stage: If transaction is valid, add it to block

	print("Transaction broadcasted successfully!")

	# if bootstrap clear current block from genesis
	if arguments.node == 1 and new_node.current_block.previous_hash == 1:
		#print("SENDER ADDRESS")
		#print(new_node.current_block.transactions[0]['sender_address'])
		# clear current block 
		new_node.current_block = block.Block(0,0, [], difficulty) 


	# Decode incoming transaction

	trans = json.loads(request.form["transaction"])
	#print(trans)
	tx = transaction.Transaction(0, new_node.wallet.private_key, 0, 0, [])
	tx.get_created_transaction(trans["sender_address"], trans["receiver_address"], trans["amount"], trans["transaction_inputs"], trans["transaction_outputs"], trans["signature"], trans["transaction_id"], trans["timestamp"])
	print("Sender address is:", trans["sender_address"])
	print("Receiver address is:", trans["receiver_address"])
	
	# Insert incoming transaction to node's transaction list, check "/" endpoint
	if not new_node.transaction_list or tx.timestamp > new_node.transaction_list[0].timestamp:
		new_node.transaction_list.append(tx)
	else:
		i = 0
		while(tx.timestamp > new_node.transaction_list[i].timestamp):
			i+=1
		new_node.transaction_list.insert(i,tx)

	# Validate transaction & If transaction is valid, add it to block
	tx = new_node.transaction_list.pop(0)
	result = []
	if new_node.validate_transaction(tx):
		result = tx.transaction_outputs
		new_node.add_transaction_to_block(tx, capacity, difficulty)
		print('Transaction added to current block')
		
	return jsonify({'result': result})
	

@app.route("/current_chain", methods = ['GET', 'POST'])
def current_data():
	# function to receive blockchain from bootstrap
	# & validate blockchain
	if(flask.request.method == 'GET'):
		print(json.dumps(new_node.utxos, indent=4))
		return json.dumps(new_node.utxos, indent=4)
	else:
		#new_node.current_block = request.form["current_block"]
		data = request.get_json(force=True)
		#print(data['current_block'])
		cb = data['current_block']	# current block shortcut 
		#new_node.current_block.get_created_block(cb['index'], cb['timestamp'], cb['transactions'], cb['previous_hash'], cb['nonce'], cb['hash'])
		#new_node.current_block = data['current_block']
		#new_node.chain.add_block_to_chain(new_node.current_block)
		#print(len(new_node.chain.chain))
		#print('current_chain')
		#print(data['current_chain'])
		new_node.chain.get_created_chain(data['current_chain'])
		print(len(new_node.chain.chain))
		print("Genesis Block appended to blockchain")
		new_node.current_block = block.Block(0,0, [], difficulty)
		print("Current block cleared.")

		return "block posted"
	# block = jsonpickle.decode(request.form["current_block"])
	#return block


@app.route("/get_balance", methods=['GET'])
def get_balance():
	balance = new_node.balance(new_node.wallet.public_key, new_node.utxos)
	return {"balance": balance}


@app.route("/get_view", methods=['GET'])
def get_view():
	length = len(new_node.chain.chain)
	last_block = new_node.chain.chain[length-1]
	return json.dumps(last_block.transactions)

@app.route("/create_transaction_cli", methods=['POST'])
def create_transaction_cli():
	recipient = request.form["recipient"]
	amount = request.form["amount"]
	if recipient != new_node.ip_address:
		for url in new_node.ring:
			if url["address"] == recipient:
				return new_node.create_transaction(recipient, int(amount))
		
	


if __name__ == "__main__":

	parser = ArgumentParser()
	parser.add_argument('node', type=int, help='if node is bootstrap enter 1 else enter 0')
	parser.add_argument('cap', type=int, help='enter block capacity 1, 5 or 10')
	parser.add_argument('diff', type=int, help='nonce difficulty digits (enter 4 or 5), hexadecimal')
	parser.add_argument('N', type=int, help='total number of nodes')
	parser.add_argument('port', type=int, help='port')
	global arguments
	arguments = parser.parse_args()

	a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	location = ("localhost", arguments.port)
	result_of_check = a_socket.connect_ex(location)

	if result_of_check == 0:
		print("Port " + str(arguments.port) + " is in use.")
		sys.exit("Bad port")

	global new_node 
	new_node = node.Node(arguments.node, arguments.N, "http://localhost", str(arguments.port), arguments.cap, arguments.diff)
	
	global capacity
	capacity = arguments.cap

	global difficulty 
	difficulty = arguments.diff

	if(arguments.node == 1):
		new_node.create_genesis_block(capacity, difficulty)

	if(arguments.node == 0):
		thread = threading.Thread(target=create_node)
		thread.start()
		#create_node()
	
	app.run(host='localhost', port=arguments.port, threaded = True)