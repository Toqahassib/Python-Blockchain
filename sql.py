# this file is to simplify using mysql with python
from MySQLdb.cursors import Cursor
from app import mysql, session
from blockchain import Block, Blockchain


class Table():
    def __init__(self, tbl_name, *args):
        self.table = tbl_name
        self.columns = "(%s)" % ",".join(args)

        # check if table exists
        if tbl_exists(tbl_name):
            cursor = mysql.connection.cursor()
            cursor.execute("CREATE TABLE {}{}".format(
                self.table, self.columns))
            cursor.close()

    # get all the values from the table
    def getall(self):
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM %s" % self.table)
        data = cur.fetchall()
        return data

    # get from the table using column's data
    # e.g getone("hash","000438jjk70fv...")
    def getone(self, search, value):
        data = {}
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM %s WHERE %s = \"%s\"" %
                             (self.table, search, value))
        if result > 0:
            data = cur.fetchone()
        cur.close()
        return data

    # delete from the table using a column's data
    def deleteone(self, search, value):
        cur = mysql.connection.cursor()
        cur.execute("DELETE from %s where %s = \"%s\"" %
                    (self.table, search, value))
        mysql.connection.commit()
        cur.close()

    # delete all from the table.
    def deleteall(self):
        self.drop()  # remove table and recreate
        self.__init__(self.table, *self.columnsList)

    # remove table from mysql
    def drop(self):
        cur = mysql.connection.cursor()
        cur.execute("DROP TABLE %s" % self.table)
        cur.close()

    # insert into the table
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


def tbl_exists(tableName):
    cursor = mysql.connection.cursor()
    try:
        result = cursor.execute("SELECT * FROM {}".format(tableName))
        cursor.close()
    # table doesn't exist
    except:
        return True
    # table exists
    else:
        return False
