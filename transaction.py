from collections import OrderedDict
from sqlite3 import Date
import rsa
import block
import binascii
import json
import uuid
from binascii import unhexlify, hexlify
from hashlib import sha256
from Crypto.Hash import SHA
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA
import requests
import jsonpickle
import datetime


class Transaction:

    def __init__(self, sender_public_key, sender_private_key, receiver_public_key, amount, transaction_inputs):        
        #self.sender_address: To public key του wallet από το οποίο προέρχονται τα χρήματα
        self.sender_address = sender_public_key
        #self.receiver_address: To public key του wallet στο οποίο θα καταλήξουν τα χρήματα
        self.receiver_address = receiver_public_key
        #self.amount: το ποσό που θα μεταφερθεί
        self.amount = amount
        #self.transaction_inputs: λίστα από Transaction Input 
        self.transaction_inputs = transaction_inputs
        #self.transaction_outputs: λίστα από Transaction Output 
        self.transaction_outputs = []
        #selfSignature
        self.signature = self.sign_transaction(sender_private_key)
        #universal unique identifier: used for signing transaction
        #self.unique_id = uuid.uuid1().bytes
        #self.transaction_id: το hash του transaction
        self.transaction_id = SHA.new(uuid.uuid1().bytes).hexdigest()

        self.timestamp = datetime.datetime.now().strftime("%x %X")
        

    def serialize(self):
        return self.__dict__

    def hashing(self):
        stringed = str(self.sender_address) + str(self.receiver_address) + str(self.amount) + str(self.transaction_inputs) + str(self.transaction_outputs)
        #print(sha256(stringed.encode('ascii')).hexdigest())
        return sha256(stringed.encode('ascii')).hexdigest()


    def sign_transaction(self, sender_private_key):
        signer = PKCS1_v1_5.new(RSA.importKey(unhexlify(sender_private_key)))
        h = SHA.new(self.hashing().encode('utf8'))
        signature = hexlify(signer.sign(h)).decode('ascii')
        return signature



    def get_created_transaction(self, sender_address, receiver_address, amount, transaction_inputs, transaction_outputs, signature, transaction_id, timestamp):
        self.sender_address = sender_address
        self.receiver_address = receiver_address
        self.amount = amount
        self.transaction_inputs = transaction_inputs
        self.transaction_outputs = transaction_outputs
        self.signature = signature
        self.transaction_id = transaction_id
        self.timestamp = timestamp