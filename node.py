from flask import Flask
from flask import jsonify 
import socket
import wallet
import block
import transaction
import requests
from requests.models import Response
import json
import rsa
app = Flask(__name__)

class Node:
	def __init__(self):
		
		##set

		self.NBC = 100
		self.current_id_count = 0
		self.ip_address = ''
		self.wallet = 0
		self.chain = []
		self.current_block = []





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
		node = Node()
		node.ip_address = 'http://localhost:' + str(PORT) + '/'
		node.current_id_count = PORT % 5000
		node.wallet = wallet.generate_wallet(node.ip_address)
		if PORT == 5000:
			#create genesis transaction for bootstrap node
			global genesis_transaction
			genesis_transaction = transaction.Transaction()
			
			transaction.create_transaction(genesis_transaction, 0, node.wallet.public_key, node.ip_address, 500, [0], [genesis_transaction.transaction_id, genesis_transaction.sender_address, genesis_transaction.amount])
			#genesis_transaction.transaction_id = ?
			#genesis_transaction.sender_address = 0
			#genesis_transaction.receiver_address = node.wallet.public_key 
			#genesis_transaction.receiver_ip_address = node.ip_address
			#genesis_transaction.amount = 500
			#genesis_transaction.transaction_inputs = [0]
			#genesis_transaction.transaction_outputs = [genesis_transaction.transaction_id, genesis_transaction.sender_address, genesis_transaction.amount]
			'''print(genesis_transaction.sender_address)
			print(genesis_transaction.receiver_address)
			print(genesis_transaction.receiver_ip_address)
			print(genesis_transaction.amount)
			print(genesis_transaction.transaction_inputs)
			print(genesis_transaction.transaction_outputs)'''
			print(transaction.stringify(genesis_transaction))
			if transaction.sign_transaction(genesis_transaction, node.wallet.private_key):
				print('sign ok')
			node.wallet.transactions.append(genesis_transaction)

			#transaction.verify_transaction(genesis_transaction, node.wallet.public_key)

			#create genesis block for bootstrap node
			global genesis_block
			genesis_block = block.Block()

			genesis_block.index = 0
			genesis_block.previous_hash = 1
			genesis_block.nonce = 0
			genesis_block.transactions = [genesis_transaction]
			#genesis_block.hash = ?

		app.run(host='localhost', port=PORT)		
	
		

@app.route("/")
def index():
	#print({'NBCs': n.NBC, 'ID': n.current_id_count})
	#print(n.wallet.public_key)
	#print(n.wallet.private_key)
	print(genesis_transaction.transaction_outputs)
	print(genesis_transaction.transaction_inputs)
	print(genesis_transaction.receiver_ip_address)
	print(genesis_transaction.transaction_id)
	return {'NBCs': node.NBC, 'ID': node.current_id_count, 'wallet_address': node.wallet.address, 'wallet_transactions': str(node.wallet.transactions)}
	#return 'hello', 200

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
	run(5000)
		



