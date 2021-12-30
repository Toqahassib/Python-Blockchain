from app import mysql

from blockchain import Block, Blockchain, Transactions

# custom exceptions for transaction errors


class InvalidTransactionException(Exception):
    pass


class InsufficientFundsException(Exception):
    pass


class Table():

    def __init__(self, table_name, *args):
        self.table = table_name
        self.columns = "(%s)" % ",".join(args)
        self.columnsList = args

        # if table does not already exist, create it.
        if isnewtable(table_name):
            create_data = ""
            for column in self.columnsList:
                create_data += "%s varchar(100)," % column

            cur = mysql.connection.cursor()  # create the table
            cur.execute("CREATE TABLE %s(%s)" %
                        (self.table, create_data[:len(create_data)-1]))
            cur.close()

    # get all the values from the table
    def getall(self):
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM %s" % self.table)
        data = cur.fetchall()
        return data

    # get one value from the table based on a column's data
    # EXAMPLE using blockchain: ...getone("hash","00003f73gh93...")
    def getone(self, search, value):
        data = {}
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM %s WHERE %s = \"%s\"" %
                             (self.table, search, value))
        if result > 0:
            data = cur.fetchone()
        cur.close()
        return data

    # delete a value from the table based on column's data
    def deleteone(self, search, value):
        cur = mysql.connection.cursor()
        cur.execute("DELETE from %s where %s = \"%s\"" %
                    (self.table, search, value))
        mysql.connection.commit()
        cur.close()

    # delete all values from the table.
    def deleteall(self):
        self.drop()  # remove table and recreate
        self.__init__(self.table, *self.columnsList)

    # remove table from mysql
    def drop(self):
        cur = mysql.connection.cursor()
        cur.execute("DROP TABLE %s" % self.table)
        cur.close()

    # insert values into the table
    def insert(self, *args):
        data = ""
        for arg in args:  # convert data into string mysql format
            data += "\"%s\"," % (arg)

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO %s%s VALUES(%s)" %
                    (self.table, self.columns, data[:len(data)-1]))
        mysql.connection.commit()
        cur.close()

# execute mysql code from python


def sql_raw(execution):
    cur = mysql.connection.cursor()
    cur.execute(execution)
    mysql.connection.commit()
    cur.close()

# check if table already exists


def isnewtable(tableName):
    cur = mysql.connection.cursor()

    try:  # attempt to get data from table
        result = cur.execute("SELECT * from %s" % tableName)
        cur.close()
    except:
        return True
    else:
        return False

# check if user already exists


def isnewuser(username):
    # access the users table and get all values from column "username"
    users = Table("users", "name", "email", "username", "password")
    data = users.getall()
    usernames = [user.get('username') for user in data]

    return False if username in usernames else True

# send money from one user to another


def send_money(sender, reciever, amount):
    # verify that the amount is an integer or floating value
    try:
        amount = float(amount)
    except ValueError:
        raise InvalidTransactionException("Invalid Transaction.")

    # ensure that the sender has enough money to send (except BANK)
    if amount > get_balance(sender) and sender != "BANK":
        raise InsufficientFundsException("Insufficient Funds.")

    # ensure that the sender is not sending money to themselves or amount is less than 0
    elif sender == reciever or amount <= 0.00:
        raise InvalidTransactionException("Invalid Transaction.")

    # ensure that the recipient is valid
    elif isnewuser(reciever):
        raise InvalidTransactionException("User Does Not Exist.")

    # update the blockchain and sync to mysql
    blockchain = get_blockchain()
    key = blockchain.generateKeys()

    number = len(blockchain.chain) + 1
    transaction = "%s-->%s-->%s" % (sender, reciever, amount)

    blockchain.addTrans(sender, reciever, amount, key, key)

    # ensure that transaction is signed

    blockchain.mining(Block(number, transaction=transaction))
    sync_blockchain(blockchain)


# get the balance of a user


def get_balance(username):
    balance = 0.00
    blockchain = get_blockchain()

    # loop through the blockchain and update balance
    for block in blockchain.chain:
        data = block.transaction.split("-->")
        if username == data[0]:
            balance -= float(data[2])
        elif username == data[1]:
            balance += float(data[2])
    return balance

# get the blockchain from mysql and change it to Blockchain object


def get_blockchain():
    blockchain = Blockchain()
    blockchain_sql = Table("blockchain", "number", "hash",
                           "previous", "transaction", "nonce", "timestamp")
    for b in blockchain_sql.getall():
        blockchain.add(Block(int(b.get('number')), b.get(
            'previous'), b.get('transaction'), int(b.get('nonce')), b.get('timestamp')))

    return blockchain

# update blockchain in mysql table


def sync_blockchain(blockchain):
    blockchain_sql = Table("blockchain", "number", "hash",
                           "previous", "transaction", "nonce", "timestamp")
    blockchain_sql.deleteall()

    for block in blockchain.chain:
        blockchain_sql.insert(str(block.number), block.hash(
        ), block.prev_hash, block.transaction, block.nonce, block.timestamp)
