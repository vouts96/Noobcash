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
import json
import rsa
import sys

app = Flask(__name__)


def run(PORT):

	a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	location = ("127.0.0.1", PORT)
	result_of_check = a_socket.connect_ex(location)

	if result_of_check == 0:
		print("Port is open: " + str(PORT))
		run(PORT+1)
	else:
		print("Port is not open: " + str(PORT))
		global node
		node = node.Node()
		node.ip_address = 'http://localhost:' + str(PORT) + '/'
		node.current_id_count = PORT % 5000
		node.wallet = wallet.generate_wallet(node.ip_address)
		if PORT == 5000:
			#create genesis transaction for bootstrap node
			global genesis_transaction
			genesis_transaction = transaction.Transaction()
			transaction.create_transaction(genesis_transaction, 0, node.wallet.public_key, node.ip_address, 500, [0], [genesis_transaction.transaction_id, genesis_transaction.sender_address, genesis_transaction.amount])
			
			print(transaction.stringify(genesis_transaction))
			if transaction.sign_transaction(genesis_transaction, node.wallet.private_key):
				print('sign ok')
			node.wallet.transactions.append(genesis_transaction)	# append the genesis transaction to the wallet transactions of bootstrap node


			if not transaction.verify_transaction(genesis_transaction, node.wallet.public_key):
				print('verify ok')

			#create genesis block for bootstrap node
			global genesis_block
			genesis_block = block.Block()

			genesis_block.index = 0
			genesis_block.previous_hash = 1
			genesis_block.nonce = 0
			genesis_block.transactions = [genesis_transaction]
			#genesis_block.hash = ?
		
		elif PORT != 5000:
			url = 'http://localhost:5000' + '/newnode/localhost:' + str(PORT)
			#print(url)
			resp = requests.get(url, data = {'key': node.wallet.public_key})

		app.run(host='localhost', port=PORT)		
	
		

@app.route("/")
def index():
	return {'NBCs': node.NBC, 'ID': node.current_id_count, 'wallet_address': node.wallet.address, 'wallet_transactions': str(node.wallet.transactions), 'ring': str(node.ring)}



@app.route("/newnode/<url>")
def new_node(url):
	data = request.data['key']
	node.ring.append((url, data))	
	print(node.ring[0])
	return str(node.ring[0])
	
	#return 'hi'
	#return data

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
	usage = 'usage error\npython app.py --clients <clients_number>'
	if len(sys.argv) < 3:
		print(usage)
		exit(0)

	print(f"Arguments count: {len(sys.argv)}")
	for i, arg in enumerate(sys.argv):
		if i == 1 and arg != '--clients':
			print(usage)
			exit(0)
		if i == 2 and arg != '5' and arg != '10':
			print('clients can only be 5 or 10')
			exit(0)


	run(5000)
