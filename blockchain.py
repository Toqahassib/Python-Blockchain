from hashlib import sha256
from datetime import datetime

time = datetime.now()


def updatehash(*args):
    hashing_text = ""
    h = sha256()
    for arg in args:
        hashing_text += str(arg)

    h.update(hashing_text.encode('utf-8'))
    return h.hexdigest()


class Block():
    data = None
    hash = None
    nonce = 0
    prev_hash = 0 * 64
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S.%f')

    def __init__(self, data, number=0):
        self.data = data
        self.number = number

    def hash(self):
        return updatehash(self.prev_hash, self.number, self.data, self.nonce, self.timestamp)

    # convert object to a readable format
    def __str__(self):
        return str("Block: {}\nHash: {}\nPrevious: {}\nData: {}\nNonce: {}\nTime: {}\n".format(self.number, self.hash(), self.prev_hash, self.data, self.nonce, self.timestamp))


class Blockchain():
    pass


def main():
    pass


if __name__ == '__main__':
    main()
