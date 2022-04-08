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
import block
import transaction
from requests.models import Response
from binascii import unhexlify, hexlify
from hashlib import sha256
from Crypto.Hash import SHA
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA
import json
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
			{'id': new_node.id,
			'ring length': len(new_node.ring),
			'ip': new_node.ip_address, 
			'port': new_node.port, 
			'NBC': new_node.balance(new_node.wallet.public_key, new_node.utxos),
			'transactions in current block': len(new_node.current_block.transactions),
			'ring': new_node.ring,
			'transaction_list': new_node.transaction_list,
			'UTXOS': new_node.utxos,
			'current_block': new_node.current_block.serialize(),
			'CHAIN': new_node.chain.serialize()
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
	new_node.id = len(new_node.ring)
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
		new_node.current_block = new_node.create_new_block(difficulty, []) 
	


	# Decode incoming transaction

	trans = json.loads(request.form["transaction"])
	#print(trans)
	tx = transaction.Transaction(0, new_node.wallet.private_key, 0, 0, [])
	tx.get_created_transaction(trans["sender_address"], trans["receiver_address"], trans["amount"], trans["transaction_inputs"], trans["transaction_outputs"], trans["signature"], trans["transaction_id"], trans["timestamp"])
	#print("Sender address is:", trans["sender_address"])
	#print("Receiver address is:", trans["receiver_address"])
	
	new_node.transaction_lock.acquire()
	# Insert incoming transaction to node's transaction list, check "/" endpoint
	if not new_node.transaction_list or tx.timestamp > new_node.transaction_list[0].timestamp:
		new_node.transaction_list.append(tx)
	else:
		i = 0
		while(tx.timestamp > new_node.transaction_list[i].timestamp):
			i+=1
		new_node.transaction_list.insert(i,tx)
	
	new_node.transaction_lock.release()

	# Validate transaction & If transaction is valid, add it to block
	new_node.transaction_lock.acquire()
	tx = new_node.transaction_list.pop(0)
	new_node.utxos_lock.acquire()
	result = []
	if new_node.validate_transaction(tx):
		new_node.utxos_lock.release()
		result = tx.transaction_outputs
		new_node.add_transaction_to_block(tx, capacity, difficulty)
		print('Transaction added to current block')
	else:
		new_node.utxos_lock.release()
	
	new_node.transaction_lock.release()


	return jsonify({'result': result})

@app.route("/broadcast/block", methods = ['POST'])
def get_block():
	data = request.get_json(force=True)
	bl = data['block']
	new_node.current_block.get_created_block(bl['index'], bl['timestamp'], bl['transactions'], bl['previous_hash'], bl['nonce'], bl['hash'])
	i = 0
	for t in new_node.current_block.transactions:
		t = transaction.Transaction(0, new_node.wallet.private_key, 0, 0, [])
		t.get_created_transaction(t.sender_address, t.receiver_address, t.amount, t.transaction_inputs, t.transaction_outputs, t.signature, t.transaction_id, t.timestamp)
		new_node.current_block.transactions[i] = t
		i += 1
	#transaction_lock.acquire()

	'''
	temp = [transaction.transaction_id for transaction in new_node.current_block.transactions]
	for t in temp:
		if t in lock_list[::-1]:
			transaction_lock.release()
			return ("Already broadcasted")
	'''
	while(new_node.has_conflict):
		pass
	
	new_node.chain.lock.acquire()
	print("Index of block to be validated is: ", new_node.current_block.index)
	for block in new_node.chain.chain:
		if new_node.current_block.index == block.index :
			new_node.chain.lock.release()
			#transaction_lock.release()
			return ("Already broadcasted")

	
	#lock_list.extend(temp)

	#transaction_lock.release()

	if new_node.validate_block(new_node.current_block, difficulty, new_node.chain):
		'''
		for t in new_node.current_block.transactions:
			#new_node.utxo_lock.acquire()
			new_node.validate_transaction(t)
			#new_node.utxo_lock.release()
		'''
		new_node.chain.add_block_to_chain(new_node.current_block)
		new_node.current_block = new_node.create_new_block(difficulty, [])


	new_node.chain.lock.release()

	return "Block validated"

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
		#new_node.chain.add_block_to_chain(new_node.current_block)
		#print(len(new_node.chain.chain))
		#print('current_chain')
		#print(data['current_chain'])
		new_node.chain.get_created_chain(data['current_chain'])
		print(len(new_node.chain.chain))
		print("Genesis Block appended to blockchain")
		#new_node.current_block = new_node.create_new_block(difficulty, [])
		print("Current block cleared.")

		return "block posted"
	# block = jsonpickle.decode(request.form["current_block"])
	#return block

@app.route('/blockchain/length', methods=['POST'])
def blockchain_length():
	flag = False
	if not new_node.chain.lock.locked():
		flag = True
		new_node.chain.lock.acquire()
	data = {}
	data["length"] = len(new_node.chain.chain)
	data["conflict"] = new_node.has_conflict
	data["id"] = new_node.id
	if flag:
		new_node.chain.lock.release()
	
	return jsonify(data), 200

@app.route('/blockchain/request', methods=['POST'])
def blockchain_request():
	new_node.chain.lock.acquire()	

	data = {}
	temp = [b.serialize() for b in new_node.chain.chain]
	data["blocks"]=json.dumps(temp)
	if new_node.chain.lock.locked():
		new_node.chain.lock.release()
	return jsonify(data), 200


@app.route('/mining/stats',methods = ['GET'])
def get_stats():
	response = {}
	response["total_mining_time"] = new_node.total_mining_time
	response["total_minings"] = new_node.total_minings
	return jsonify(response), 200

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
	recipient = request.form['recipient']
	amount = request.form['amount']
	print("Data Collected successfully")
	if recipient != new_node.ip_address:
		receiver_id = recipient[-1]
		for r in new_node.ring:
			if r["id"] == int(receiver_id):
				return new_node.create_transaction(new_node.ring[int(receiver_id)]["public_key"], int(amount))
			else:
				print("Address not in ring")
		return "Address not in ring"
	else:
		print("Cannot send to myself")
		return "Cannot send to myself"


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

	global lock_list
	lock_list = []

	global transaction_lock
	transaction_lock = threading.Lock()

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