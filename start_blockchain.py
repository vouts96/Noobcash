import os
from pydoc import cli
import sys
import time
import requests

usage = 'usage error\npython start_blockchain.py --clients <clients_number> --capacity <capacity> --difficulty <difficulty>'
clients = 0
capacity = 1
difficulty = 4

if __name__ == "__main__":
	
	if len(sys.argv) < 3:
		print(usage)
		exit(0)

	print(f"Arguments count: {len(sys.argv)}")
	for i, arg in enumerate(sys.argv):
		print(f"Argument {i:>6}: {arg}")
		#clients number
		if i == 1 and arg != '--clients':
			print(usage)
			exit(0)
		if i == 2 and int(arg) > 10:
			print('clients can not be more than 10')
			exit(0)
		if i == 2 and int(arg) <= 10:
			clients = arg
		#capacity
		if i == 3 and arg != '--capacity':
			print(usage)
			exit(0)
		if i == 4 and arg != '1' and arg != '5' and arg != '10':
			print('capacity can only be 1, 5 or 10')
			exit(0)
		if i == 4 and (arg == '1' or arg == '5' or arg == '10'):
			capacity = arg
		#difficulty
		if i == 5 and arg != '--difficulty':
			print(usage)
			exit(0)
		if i == 6 and arg != '4' and arg != '5':
			print('difficulty can only be 4 or 5')
			exit(0)
		if i == 6 and (arg == '4' or arg == '5'):
			difficulty = arg

	for i in range(0, int(clients)):
		os.system('pm2 start "python app.py --clients ' + clients + '"')
		time.sleep(0.5)
		#print('pm2 start "python app.py" --clients ' + clients)
	resp = requests.get('http://localhost:5000/allnodes/' + clients)