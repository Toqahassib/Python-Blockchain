from flask import Flask, render_template, flash, redirect, url_for, session, request
from wtforms import Form, StringField, PasswordField, validators
from passlib.hash import sha256_crypt
from flask_mysqldb import MySQL
from functools import wraps
from blockchain import Blockchain
import time
from sql import *
from app import *

if __name__ == '__main__':
    node = '127.0.0.1'

    blockchain.register_node(node)

    app.secret_key = 'secret123'
    app.run(host=node, port=5001, debug=True)
