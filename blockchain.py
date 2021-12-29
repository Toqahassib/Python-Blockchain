from hashlib import sha256
import time
from Crypto.Signature import pkcs1_15
from Crypto.PublicKey import RSA
from urllib.parse import urlparse
import requests


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

    # convert object to a readable format
    def __str__(self):
        return str("Block: {}\nHash: {}\nPrevious: {}\nTransaction: {}\nNonce: {}\nTime: {}\n".format(self.number, self.hash(), self.prev_hash, self.transaction, self.nonce, self.timestamp))


class Blockchain():

    # first 3 digits of the hash must be 0
    difficulty = 3

    def __init__(self):
        self.chain = []
        self.pendingTrans = []
        self.nodes = set()

    # p2p
    def register_node(self, address):
        parsedUrl = urlparse(address)
        self.nodes.add(parsedUrl.netloc)

    # def resolveConflicts(self):
    #     neighbors = self.nodes
    #     newChain = None

    #     maxLength = len(self.chain)

    #     for node in neighbors:
    #         response = requests.get(f'http://{node}/transaction')

    #         if response.status_code == 200:
    #             length = response.json()['length']
    #             chain = response.json()['chain']

    #             if length > maxLength and self.isValidChain():
    #                 maxLength = length
    #                 newChain = chain

    #     if newChain:
    #         self.chain = self.chainJSONdecode(newChain)
    #         print(self.chain)
    #         return True

    #     return False

    def add(self, block):
        self.chain.append(block)

    def remove(self, block):
        self.chain.remove(block)

    def addTrans(self, sender, receiver, amt, keyString, senderKey):
        keyByte = keyString.encode("ASCII")
        senderKeyByte = senderKey.encode('ASCII')

        key = RSA.import_key(keyByte)
        senderKey = RSA.import_key(senderKeyByte)

        if not sender or not receiver or not amt:
            print('transaction error 1')
            return False

        transaction = Transactions(sender, receiver, amt)

        transaction.signTrans(key, senderKey)

        if not transaction.validTrans():
            print("transaction error 2")
            return False
        self.pendingTrans.append(transaction)
        return len(self.chain) + 1

    def minePendingTrans(self):
        lenPT = len(self.pendingTrans)
        for i in range(0, lenPT, 10):
            end = i + 10
            if i >= lenPT:
                end = lenPT

            transactionSlice = self.pendingTrans[i:end]

            newBlock = Block(transactionSlice, time(), len(self.chain))

            hashVal = self.chain[-1].hash()
            newBlock.prev = hashVal
            newBlock.mining(self.difficulty)
            self.chain.append(newBlock)
        print("MIning trans success")
        return True

    def generateKeys(self):
        key = RSA.generate(2048)
        private_key = key.export_key()
        file_out = open("private.pem", "wb")
        file_out.write(private_key)

        public_key = key.publickey().export_key()
        file_out = open("receiver.pem", "wb")
        file_out.write(public_key)

        return key.publickey().export_key().decode('ASCII')

    def mining(self, block):

        try:
            block.prev_hash = self.chain[-1].hash()
        except IndexError:
            pass

        while True:
            if block.hash()[:self.difficulty] == "0" * self.difficulty:
                self.add(block)
                break
            else:
                block.nonce += 1
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

    def validTrans(self):
        if self.hashed != self.hash():
            return False
        if self.sender == self.receiver:
            return False
        if not self.signature or len(self.signature) == 0:
            print("no sign")
            return False
        return True

    def signTrans(self, key, senderKey):
        if self.hashed != self.hash():
            print("transaction tampered error")
            return False
        if str(key.publickey().export_key()) != str(senderKey.publickey().export_key()):
            print("transaction attempt to be signed from another walled")
            return False

        pkcs1_15.new(key)

        self.signature = "made"
        print("Made signature!")
        return True
    # returns the hashed block

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

    blockchain = Blockchain()
    database = ["hello", "what", "dsta", "test"]

    num = 0

    for transaction in database:
        num += 1
        blockchain.mining(Block(num, transaction=transaction))

    for block in blockchain.chain:
        print(block, "\n")

    print(blockchain.valid())


if __name__ == '__main__':
    main()
