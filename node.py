from flask import Flask
from flask import jsonify 
import wallet
import block
import requests
from requests.models import Response
import json
app = Flask(__name__)

class node:
	def __init__(self):
		
		##set

		#self.chain
		self.NBC = 100
		self.current_id_count = 0
		self.ip_address = ''
		#self.NBCs
		self.wallet = 0

		#slef.ring[]   #here we store information for every node, as its id, its address (ip:port) its public key and its balance 




n = node()


def run(PORT):
	try:
		n.ip_address = 'http://localhost:' + str(PORT)
		n.current_id_count = PORT % 5000
		n.wallet = wallet.generate_wallet(n.ip_address)
		app.run(host='localhost', port=PORT)	
	except:
		run(PORT+1)

@app.route("/")
def index():
	#print({'NBCs': n.NBC, 'ID': n.current_id_count})
	return {'NBCs': n.NBC, 'ID': n.current_id_count, 'wallet_address': n.wallet.address, 'wallet_public_key': n.wallet.public_key}
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
	n.NBC = n.NBC + int(coins)
	return 'Hey there I am node with id:' + str(n.current_id_count) + ' and I have ' + str(n.NBC) + ' NBC'



if __name__ == "__main__":
	run(5000)
		



