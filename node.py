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
import sys


class Node:
	def __init__(self):
		
		##set

		self.NBC = 0
		self.current_id_count = 0
		self.ip_address = ''
		self.wallet = 0
		self.chain = []
		self.current_block = []
		self.ring = []








