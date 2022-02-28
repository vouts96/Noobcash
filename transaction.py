from collections import OrderedDict
import rsa
import block
import binascii

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


def stringify(t):
    stringed = str(t.sender_address) + str(t.receiver_address) + str(t.receiver_ip_address) + str(t.amount) + str(t.transaction_inputs) + str(t.transaction_outputs)
    return stringed


def sign_transaction(t, privkey):
    stringToHash = stringify(t).encode()
    t.transaction_id =  rsa.compute_hash(stringToHash, 'SHA-1')
    t.signature = rsa.sign_hash(t.transaction_id, privkey, 'SHA-1')

    return t.signature

def verify_transaction(t, pubkey):
    stringToVerify = stringify(t).encode()
    rsa.verify(stringToVerify, t.signature, pubkey)

    


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
