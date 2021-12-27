from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from passlib.hash import sha256_crypt
from flask_mysqldb import MySQL

# initialize the app

app = Flask(__name__)

# configure sql settings
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
# database name
app.config['MYSQL_DB'] = 'crypto'
# cursor class to access info in mysql using dictionary
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# initialize mysql
mysql = MySQL(app)

# create homepage


@app.route("/")
def index():
    return "Hello World!"


if __name__ == '__main__':
    app.secret_key = 'secret123'
    app.run(debug=True)
