from argparse import ArgumentParser
from ast import arg
from textwrap import indent
import sys
import requests
import json


'''def cli():
	parser = ArgumentParser()
	parser.add_argument('node', type=int, help='if node is bootstrap enter 1 else enter 0')
	parser.add_argument('cap', type=int, help='enter block capacity 1, 5 or 10')
	parser.add_argument('diff', type=int, help='nonce difficulty digits (enter 4 or 5), hexadecimal')
	parser.add_argument('N', type=int, help='total number of nodes')
	parser.add_argument('port', type=int, help='port')
	global arguments
	arguments = parser.parse_args()

'''

def print_help():
	print("view					View last transactions: Print the transactions contained in the last validated block")
	print("balance					Show balance: Print wallet balance")
	print("t <recipient_address> <amount>		New transaction: Send to recipient_address wallet an amount of NBC coins")


# Command Line Tool to be implemented once the app is running
def cli():
	parser = ArgumentParser()
	arguments = sys.argv
	#print(arguments)
	if(arguments[1] == "help"):
		print_help()
	elif(arguments[1] == "view"):
		view_resp = requests.get('http://localhost:5000/get_view')
		view = json.dumps(json.loads(view_resp.content.decode('ascii')), indent=4)
		print("Transactions of the last validated block:")
		print(view)

	elif(arguments[1] == "balance"):
		balance_resp = requests.get('http://localhost:5000/get_balance')
		balance = json.loads(balance_resp.content.decode('ascii'))['balance']
		print("My balance is: " + str(balance))
	elif(arguments[1] == "t"):
		# Error checks ---------------------------------------------
		if(len(arguments) != 4):
			print_help()
			exit(0)
		if(int(arguments[3]) < 0):
			print("Error: Amount cannot be negative")
			print_help()
			exit(0)
		# ----------------------------------------------------------
		data = {}
		data["recipient"] = arguments[2]
		data["amount"] = arguments[3]

		trans_resp = requests.post("http://localhost:5000/create_transaction_cli", data)
		print(trans_resp.content)
		

		'''for r in node.ring:
			if(r['url'] == arguments[2]):
				print("Correct IP")
				check = True
				amount = int(arguments[3])
				if(amount > 0):
					print("Correct amount")
				else:
					print("Incorrect amount")
					exit(0)
				break
		if(check == False):
			print("Please provide a correct address")
			
		else:
			print("Error: unknown command" + command[0])
			print("Run 'help' for usage")'''
	
	else:
		print_help()

# run cli
cli()

