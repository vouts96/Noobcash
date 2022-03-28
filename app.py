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
#import rsa
import threading
import sys
import os
import time
from argparse import ArgumentParser

app = Flask(__name__)


def create_node():
	req = new_node.create_new_node(arguments.node)
	if (req.status_code == 200):
		print("Creating new node...")
		time.sleep(0.5)
		print("New node created and registerd in ring successfully!")

# Command Line Tool to be implemented once the app is running
def cli():
	while(True):
		terminal = input()
		if(terminal == "help"):
			print("view								View last transactions: Print the transactions contained in the last validated block")
			print("balance							Show balance: Print wallet balance")
			print("t <recipient_address> <amount>	New transaction: Send to recipient_address wallet an amount of NBC coins from sender_wallet wallet")
		elif(terminal == "view"):
			print("view")
		elif(terminal == "balance"):
			print("balance")
		else:
			command = terminal.split()
			# error-spell checking on 't <recipient_address> <amount>' command
			if(command[0] == "t"):
				check = False
				for r in node.ring:
					# if statement needs correction in r['url']
					if(r['url'] == command[1]):
						print("Correct IP")
						check = True
						amount = int(command[2])
						if(amount > 0):
							print("Correct amount")
						else:
							print("Incorrect amount")
						break
				if(check == False):
					print("Please provide a correct address")
				
			else:
				print("Error: unknown command" + command[0])
				print("Run 'help' for usage")


@app.route("/", methods = ['GET', 'POST'])
def index():
	return {'len': len(new_node.ring),'ip': new_node.ip_address, 'port': new_node.port, 'NBC': new_node.NBC, 'ring': new_node.ring}




@app.route("/newnode", methods = ['POST'])
def newNode():
	print("New node created successfuly!")
	public_key = request.form["public_key"]
	ip = request.form["ip"]
	port = request.form["port"]
	print("About to register new node...")
	new_node.register_node(arguments.node, ip, port, public_key)
	print("New node registered successfully!")
	return 'New node registered successfully!'


@app.route("/broadcast/ring", methods = ['POST'])
def broadcast_ring():
	new_node.ring = json.loads(request.form["ring"])

	return "Node " + str(new_node.id)  +  " updated"


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
		#t = transaction.Transaction()
		#transaction.create_transaction(t, node.wallet.public_key, receiver_address, receiver_ip_address, 100, )
	
	#trigger requests for ring to send urls and public keys
	urls = [j[0] for j in node.ring]
	for i in range(1, (int(clients))):
		resp = requests.get(urls[i] + '/askforring')
	
	start_new_thread(cli, ())
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

	parser = ArgumentParser()
	parser.add_argument('node', type=int, help='if node is bootstrap enter 1 else enter 0')
	parser.add_argument('cap', type=int, help='enter block capacity 1, 5 or 10')
	parser.add_argument('diff', type=int, help='nonce difficulty digits (enter 4 or 5), hexadecimal')
	parser.add_argument('N', type=int, help='total number of nodes')
	parser.add_argument('port', type=int, help='port')
	arguments = parser.parse_args()

	a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	location = ("localhost", arguments.port)
	result_of_check = a_socket.connect_ex(location)

	if result_of_check == 0:
		print("Port " + str(arguments.port) + " is in use.")
		sys.exit("Bad port")

	global new_node 
	new_node = node.Node(arguments.node, arguments.N, "http://localhost", str(arguments.port))
	#new_node.create_genesis_block(arguments.cap, arguments.diff)
	if(arguments.node == 0):
		thread = threading.Thread(target=create_node)
		thread.start()
		#create_node()
	
	app.run(host='localhost', port=arguments.port, threaded = True)