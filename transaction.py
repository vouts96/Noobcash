from collections import OrderedDict
import rsa
import block
import binascii
import json
from binascii import unhexlify, hexlify
from hashlib import sha256
from Crypto.Hash import SHA
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA
#import Crypto
#import Crypto.Random
#from Crypto.Hash import SHA
#from Crypto.PublicKey import RSA
#from Crypto.Signature import PKCS1_v1_5

#import requests
#from flask import Flask, jsonify, request, render_template


class Transaction:

    def __init__(self):


        ##set
        
        #self.sender_address: To public key του wallet από το οποίο προέρχονται τα χρήματα
        self.sender_address = 0
        #self.receiver_address: To public key του wallet στο οποίο θα καταλήξουν τα χρήματα
        self.receiver_address = 0
        self.receiver_ip_address = 0
        #self.amount: το ποσό που θα μεταφερθεί
        self.amount = 0
        #self.transaction_id: το hash του transaction
        self.transaction_id = 0
        #self.transaction_inputs: λίστα από Transaction Input 
        self.transaction_inputs = []
        #self.transaction_outputs: λίστα από Transaction Output 
        self.transaction_outputs = []
        #selfSignature
        self.signature = 0


def create_transaction(t, sender_address, receiver_address, receiver_ip_address, amount, inputs, outputs):
    #t = Transaction()
    t.sender_address = sender_address    
    t.receiver_address = receiver_address 
    t.receiver_ip_address = receiver_ip_address
    t.amount = amount
    t.transaction_inputs = inputs
    t.transaction_outputs = outputs
    #t.signature = rsa

    return t


def stringify(self):
    stringed = str(self.sender_address) + str(self.receiver_address) + str(self.receiver_ip_address) + str(self.amount) + str(self.transaction_inputs) + str(self.transaction_outputs)
    #print(sha256(stringed.encode('ascii')).hexdigest())
    return sha256(stringed.encode('ascii')).hexdigest()


def sign_transaction(self, sender_private_key):
    signer = PKCS1_v1_5.new(RSA.importKey(unhexlify(sender_private_key)))
    h = SHA.new(stringify(self).encode('utf8'))
    self.signature = hexlify(signer.sign(h)).decode('ascii')
    #print(self.signature)

def verify_signature(self, signature):
    public_key = RSA.importKey(unhexlify(self.sender_address))
    verifier = PKCS1_v1_5.new(public_key)
    h = SHA.new((stringify(self)).encode('utf8'))
    if not verifier.verify(h, unhexlify(self.signature)):
        raise ValueError("Not valid Signature")






