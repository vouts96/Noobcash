from traceback import print_tb
from binascii import unhexlify, hexlify
from hashlib import sha256
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
		print("Port " + str(PORT) + " is in use.")
		run(PORT+1, clients)
	else:
		print("Port " + str(PORT) + " is not in use.")
		print("Opening Port " + str(PORT) + "......")
		global node
		node = node.Node()
		node.ip_address = 'http://localhost:' + str(PORT)
		node.current_id_count = PORT % 5000
		node.wallet = wallet.generate_wallet(node.ip_address)
		if PORT == 5000:
			node.ring.append((node.ip_address, node.wallet.public_key))
			node.NBC = 100 * clients
			
			#create genesis transaction for bootstrap node
			genesis_transaction = transaction.Transaction()
			transaction.create_transaction(genesis_transaction, 0, node.wallet.public_key, node.ip_address, 100 * clients, [0], [genesis_transaction.transaction_id, genesis_transaction.sender_address, genesis_transaction.amount])
			
			#print(transaction.stringify(genesis_transaction))
			transaction.sign_transaction(genesis_transaction, node.wallet.private_key)
			
			# append the genesis transaction to the wallet transactions of bootstrap node
			node.wallet.transactions.append(genesis_transaction)	

			#create genesis block for bootstrap node
			genesis_block = block.Block()
			block.create_block(genesis_block, 0, [genesis_transaction], 1)
		
		elif PORT != 5000:
			a_socket.connect(("127.0.0.1",5000))
			data = "Hello Server!"
			a_socket.send(data.encode())


			url = 'http://localhost:5000' + '/newnode/localhost:' + str(PORT) + '/' + node.wallet.public_key
			resp = requests.post(url)
			
		app.run(host='localhost', port=PORT)
			
	
		

@app.route("/", methods = ['GET', 'POST'])
def index():
	return {'len': len(node.ring), 'NBCs': node.NBC, 'ID': node.current_id_count, 'wallet_address': node.wallet.address, 'wallet_transactions': str(node.wallet.transactions[0].signature), 'ring': node.ring}



@app.route("/newnode/<url>/<public_key>", methods = ['GET', 'POST'])
def new_node(url, public_key):
	
	url = 'http://' + url
	node.ring.append((url, public_key))
	#print(node.ring[0][0])
	
	return 'append ok'


#bootstrap node is informed that all nodes are on the network
#and also creates transactions to send coins to all nodes
@app.route("/allnodes/<clients>", methods = ['GET'])
def allnodes(clients):
	#create initial transactions for all nodes except from bootstrap(i = 1)
	for i in range(1, len(node.ring)):
		receiver_ip_address = node.ring[i][0]
		#print(receiver_ip_address)
		receiver_address = node.ring[i][1]
		#print(receiver_address)
		t = transaction.Transaction()
		transaction.create_transaction(t, node.wallet.public_key, receiver_address, receiver_ip_address, 100, )
	
	#trigger requests for ring to send urls and public keys
	urls = [j[0] for j in node.ring]
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
def get_ring():
	urls = []
	public_keys = []
	urls = [j[0] for j in node.ring]
	public_keys = [j[1] for j in node.ring]
	resp = {'urls': urls, 'public_keys': public_keys}
	resp_json = json.dumps(resp)
	return resp_json


@app.route("/getfirsttransactions", methods = ['GET'])
def get_first_transactions():
	#for i in range(0, len(node.ring)):
	return "hi"

if __name__ == "__main__":
	clients = 0
	usage = 'usage error\npython app.py --clients <clients_number>'
	if len(sys.argv) < 3:
		print(usage)
		exit(0)

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
