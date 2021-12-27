from hashlib import sha256
from datetime import datetime

time = datetime.now()

# function to hash the block


def new_hash(*args):
    text = ""
    hash = sha256()
    for arg in args:
        text += str(arg)

    hash.update(text.encode('utf-8'))

    return hash.hexdigest()


class Block():

    # transaction data
    data = None
    # hash of block
    hash = None
    # arbirtary number for proof of work
    nonce = 0
    # hash of previous block
    prev_hash = "0" * 64

    timestamp = time.strftime('%Y-%m-%d %H:%M:%S.%f')

    def __init__(self, data, number=0):
        self.data = data
        self.number = number

    # returns the hashed block
    def hash(self):
        return new_hash(self.prev_hash, self.number, self.data, self.nonce, self.timestamp)

    # convert object to a readable format
    def __str__(self):
        return str("Block: {}\nHash: {}\nPrevious: {}\nData: {}\nNonce: {}\nTime: {}\n".format(self.number, self.hash(), self.prev_hash, self.data, self.nonce, self.timestamp))


class Blockchain():

    # first 3 digits of the hash must be 0
    difficulty = 3

    def __init__(self, chain=[]):
        self.chain = chain

    # adds a block to the chain
    def add(self, block):
        self.chain.append(block)

    # removes a block from the chain
    def remove(self, block):
        self.chain.remove(block)

    # mines a new block
    def mining(self, block):

        # if the previous hash is equal to the chain's last hashed block
        try:
            block.prev_hash = self.chain[-1].hash()
        except IndexError:
            pass

        # loop until difficulty requirement is met
        while True:
            if block.hash()[:self.difficulty] == "0" * self.difficulty:
                self.add(block)
                break
            else:
                block.nonce += 1

    # validates that prev hash and hash are equal and difficulty is implemented
    def valid(self):
        for i in range(1, len(self.chain)):
            prev = self.chain[i].prev_hash
            curr = self.chain[i-1].hash()
            if prev != curr or curr[:self.difficulty] != "0"*self.difficulty:
                return False
        return True


def main():

    blockchain = Blockchain()
    database = ["hello", "what", "dsta", "test"]
    num = 0
    for data in database:
        num += 1
        blockchain.mining(Block(data, num))

    for block in blockchain.chain:
        print(block, "\n")

    blockchain.mining(blockchain.chain[2])

    print(blockchain.valid())


if __name__ == '__main__':
    main()
