from traceback import print_tb
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
import rsa
import sys
import time

app = Flask(__name__)


def run(PORT, clients):

	a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	location = ("127.0.0.1", PORT)
	result_of_check = a_socket.connect_ex(location)

	if result_of_check == 0:
		print("Port is open: " + str(PORT))
		run(PORT+1, clients)
	else:
		print("Port is not open: " + str(PORT))
		global node
		node = node.Node()
		node.ip_address = 'http://localhost:' + str(PORT)
		node.current_id_count = PORT % 5000
		node.wallet = wallet.generate_wallet(node.ip_address)
		if PORT == 5000:
			node.ring.append((node.ip_address, node.wallet.public_key))
			node.NBC = 100 * clients
			#create genesis transaction for bootstrap node
			global genesis_transaction
			genesis_transaction = transaction.Transaction()
			transaction.create_transaction(genesis_transaction, 0, node.wallet.public_key, node.ip_address, 100 * clients, [0], [genesis_transaction.transaction_id, genesis_transaction.sender_address, genesis_transaction.amount])
			
			#print(transaction.stringify(genesis_transaction))
			#transaction.sign_transaction(genesis_transaction, node.wallet.private_key)
			
			#node.wallet.transactions.append(genesis_transaction)	# append the genesis transaction to the wallet transactions of bootstrap node


			#if transaction.verify_signature(genesis_transaction, node.wallet.public_key):
			#	print('verify ok')

			#create genesis block for bootstrap node
			global genesis_block
			genesis_block = block.Block()

			genesis_block.index = 0
			genesis_block.previous_hash = 1
			genesis_block.nonce = 0
			genesis_block.transactions = [genesis_transaction]
			#genesis_block.hash = ?
		
		elif PORT != 5000:
			url = 'http://localhost:5000' + '/newnode/localhost:' + str(PORT) + '/' + node.wallet.public_key
			resp = requests.post(url)
			
		app.run(host='localhost', port=PORT)
			
	
		

@app.route("/", methods = ['GET', 'POST'])
def index():
	return {'NBCs': node.NBC, 'ID': node.current_id_count, 'wallet_address': node.wallet.address, 'wallet_transactions': str(node.wallet.transactions), 'ring': node.ring}



@app.route("/newnode/<url>/<public_key>", methods = ['GET', 'POST'])
def new_node(url, public_key):
	
	url = 'http://' + url
	node.ring.append((url, public_key))
	#print(node.ring[0][0])
	
	return 'append ok'


#bootstrap node is informed that all nodes are on the network
@app.route("/allnodes/<clients>", methods = ['GET'])
def allnodes(clients):
	#urls = []
	#my_url = node.ip_address
	#urls.append(my_url)
	#urls = urls + [j[0] for j in node.ring]
	urls = [j[0] for j in node.ring]
	print('urls are: ')
	print(urls)
	for i in range(1, (int(clients))):
		resp = requests.get(urls[i] + '/askforring')
	
	return 'sent to all nodes'


#request from bootstrap node to all nodes to ask for everyone's addresses
@app.route("/askforring", methods = ['GET'])
def ask_for_ring():
	resp = requests.get("http://localhost:5000/getring")
	data = resp.content
	data = json.loads(data)
	#print(data['urls'][0])
	length = len(data['urls'])
	for i in range(0, length):
		node.ring.append((data['urls'][i], data['public_keys'][i]))
	#print(node.ring)

	return 'asked for ring'

#finally bootstrap node returns to each node everyone's addresses
@app.route("/getring", methods = ['GET'])
def check_ring():
	urls = []
	public_keys = []
	urls = [j[0] for j in node.ring]
	public_keys = [j[1] for j in node.ring]
	resp = {'urls': urls, 'public_keys': public_keys}
	resp_json = json.dumps(resp)
	#print(resp_json)

	return resp_json



@app.route("/sendcoins/<id>/<coins>")
def sendcoins(id, coins):
	port = 5000 + int(id)
	#print(port) 
	url = 'http://localhost:' + str(port) + '/getcoins/' + str(coins)
	#print(url)
	resp = requests.get(url)
	return resp.content
	
@app.route("/getcoins/<coins>")
def getcoins(coins):
	node.NBC = node.NBC + int(coins)
	return 'Hey there I am node with id:' + str(node.current_id_count) + ' and I have ' + str(node.NBC) + ' NBC'



if __name__ == "__main__":
	clients = 0
	usage = 'usage error\npython app.py --clients <clients_number>'
	if len(sys.argv) < 3:
		print(usage)
		exit(0)

	print(f"Arguments count: {len(sys.argv)}")
	for i, arg in enumerate(sys.argv):
		if i == 1 and arg != '--clients':
			print(usage)
			exit(0)
		if i == 2 and int(arg) > 10:
			print('clients can not be more than 10')
			exit(0)
		elif i == 2 and int(arg) <= 10:
			clients = int(arg)

	run(5000, clients)
