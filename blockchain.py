from hashlib import sha256
import time
from Crypto.Signature import pkcs1_15
from Crypto.PublicKey import RSA
from urllib.parse import urlparse


class Block():

    def __init__(self, number=0, prev_hash="0" * 64, transaction=None, nonce=0, timestamp=time.strftime('%Y-%m-%d %H:%M:%S')):
        # transaction data
        self.transaction = transaction
        self.number = number
        # arbirtary number for proof of work
        self.nonce = nonce
        # hash of previous block
        self.prev_hash = prev_hash
        self.timestamp = timestamp

    # returns the hashed block
    def hash(self):
        return new_hash(self.number, self.prev_hash, self.transaction, self.nonce, self.timestamp)

    # convert object to a string to make it readable
    def __str__(self):
        return str("Block: {}\nHash: {}\nPrevious: {}\nTransaction: {}\nNonce: {}\nTime: {}\n".format(self.number, self.hash(), self.prev_hash, self.transaction, self.nonce, self.timestamp))


class Blockchain():

    # first 3 digits of the hash must be 0
    difficulty = 3

    def __init__(self):
        self.chain = []
        self.pendingTrans = []
        self.nodes = set()

    # peer to peer function
    def register_node(self, address):
        parsedUrl = urlparse(address)
        # registers nodes
        self.nodes.add(parsedUrl.netloc)

    # adds blocks to the chain
    def add(self, block):
        self.chain.append(block)

    # removes blocks from the chain
    def remove(self, block):
        self.chain.remove(block)

    # mines blocks
    def mining(self, block):

        # the previous hash must be equal to the previous block's hash
        try:
            block.prev_hash = self.chain[-1].hash()
        except IndexError:
            pass

        # loop to ensure the difficulty of the hash is met
        while True:
            if block.hash()[:self.difficulty] == "0" * self.difficulty:
                self.add(block)
                break
            else:
                block.nonce += 1

    # adds transactions to the pending transaction list
    def addTrans(self, sender, receiver, amt, keyString, senderKey):
        # encode the keys
        keyByte = keyString.encode("ASCII")
        senderKeyByte = senderKey.encode('ASCII')

        # encrypt the keys
        key = RSA.import_key(keyByte)
        senderKey = RSA.import_key(senderKeyByte)

        if not sender or not receiver or not amt:
            # print('transaction error 1')
            return False

        transaction = Transactions(sender, receiver, amt)

        # sign the transaction using the keys
        transaction.signTrans(key, senderKey)

        if not transaction.validTrans():
            # print("transaction error 2")
            return False

        # add the transaction to the prending transaction list
        self.pendingTrans.append(transaction)
        return len(self.chain) + 1

    # generate keys
    def generateKeys(self):
        key = RSA.generate(2048)
        # save the private key in a file
        private_key = key.export_key()
        file_out = open("private.pem", "wb")
        file_out.write(private_key)

        public_key = key.publickey().export_key()
        # save the public key in a file
        file_out = open("receiver.pem", "wb")
        file_out.write(public_key)

        return key.publickey().export_key().decode('ASCII')

    # validates that prev hash and hash are equal and difficulty is implemented

    def valid(self):
        for i in range(1, len(self.chain)):
            previous = self.chain[i].prev_hash
            current = self.chain[i-1].hash()
            if previous != current or current[:self.difficulty] != "0"*self.difficulty:
                return False
        return True


class Transactions():
    def __init__(self, sender="", receiver="", amount=int, timestamp=time.strftime('%Y-%m-%d %H:%M:%S')):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.timestamp = timestamp
        self.hashed = self.hash()

    # validates transactions
    def validTrans(self):
        if self.hashed != self.hash():
            return False
        if self.sender == self.receiver:
            return False
        if not self.signature or len(self.signature) == 0:
            return False
        return True

    # signs the transaction
    def signTrans(self, key, senderKey):

        if self.hashed != self.hash():
            return False
        if str(key.publickey().export_key()) != str(senderKey.publickey().export_key()):
            return False

        pkcs1_15.new(key)

        self.signature = "made"
        return True

    # returns the hashed transaction

    def hash(self):
        return new_hash(self.sender, self.receiver, self.amount, self.timestamp)


# function to hash the block


def new_hash(*args):
    text = ""
    hash = sha256()
    for i in args:
        text += str(i)

    hash.update(text.encode('utf-8'))

    return hash.hexdigest()


def main():

    pass


if __name__ == '__main__':
    main()
