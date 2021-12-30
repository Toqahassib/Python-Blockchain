from flask import Flask, render_template, flash, redirect, url_for, session, request
from wtforms import Form, StringField, PasswordField, validators
from passlib.hash import sha256_crypt
from flask_mysqldb import MySQL
from functools import wraps
from blockchain import Blockchain
import time
from sql import *


# registration forms


class RegisterForm(Form):
    name = StringField('Full Name', [validators.length(min=4, max=50)])
    username = StringField('Username', [validators.length(min=4, max=25)])
    email = StringField('Email', [validators.length(min=6, max=50)])
    password = PasswordField('Password', [validators.DataRequired(
    ), validators.EqualTo('confirm', message='Password dont match')])
    confirm = PasswordField('Confirm Password')


# send money form


class SendMoneyForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    amount = StringField('Amount', [validators.Length(min=1, max=50)])

# buy form


class BuyForm(Form):
    amount = StringField('Amount', [validators.Length(min=1, max=50)])


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

blockchain = Blockchain()


# wrap to ensure the user is logged in


def login_verification(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("Please login", 'danger')
            return redirect(url_for('login'))
    return wrap

# function to login the user with session


def loggin(username):
    # load users table from sql.py
    users = Table("users", "name", "email", "username", "password")
    user = users.getone("username", username)

    session['logged_in'] = True
    session['username'] = username
    session['name'] = user.get('name')
    session['email'] = user.get('email')


# registration page


@app.route("/register", methods=["GET", "POST"])
def register():
    register_form = RegisterForm(request.form)
    users = Table("users", "name", "email", "username", "password")

    if request.method == 'POST' and register_form.validate():
        username = register_form.username.data
        email = register_form.email.data
        name = register_form.name.data
        # check if new user
        if isnewuser(username):
            password = sha256_crypt.encrypt(register_form.password.data)
            users.insert(name, email, username, password)
            loggin(username)
            return redirect(url_for('dashboard'))
        else:
            flash('User already exists', 'danger')
            return redirect(url_for('register'))

    return render_template('register.html', form=register_form)

# login page


@app.route("/login", methods=['GET', 'POST'])
def login():
    # if login button is clicked
    if request.method == 'POST':
        # get the user's username and password from the form
        username = request.form['username']
        pwd_entered = request.form['password']

        users = Table("users", "name", "email", "username", "password")

        user = users.getone("username", username)
        password = user.get('password')

        if password is None:
            flash("Invalid Password or username", 'danger')
            return redirect(url_for('login'))
        else:
            if sha256_crypt.verify(pwd_entered, password):
                loggin(username)
                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid password", 'danger')
                return redirect(url_for('login'))

    return render_template('login.html')


@app.route("/buy", methods=['GET', 'POST'])
# ensure the user is logged in
@login_verification
def buy():
    form = BuyForm(request.form)
    balance = get_balance(session.get('username'))

    # if button is clicked
    if request.method == 'POST':
        try:
            send_money("BANK",
                       session.get('username'), form.amount.data)
            flash("Purchase Successful!", 'success')

        except Exception as e:
            flash(str(e), 'danger')
            return redirect(url_for('dashboard'))
    return render_template('buy.html', balance=balance, form=form, page='buy')


@app.route("/transaction", methods=['GET', 'POST'])
# ensure the user is logged in
@login_verification
def transaction():
    # blockchain.resolveConflicts()
    form = SendMoneyForm(request.form)
    balance = get_balance(session.get('username'))

    # if button is clicked
    if request.method == 'POST':
        try:
            send_money(session.get('username'),
                       form.username.data, form.amount.data)
            flash("Money Sent!", 'success')

        except Exception as e:
            flash(str(e), 'danger')
            return redirect(url_for('transaction'))
    return render_template('transaction.html', balance=balance, form=form, page='transaction')


@app.route("/logout")
# ensure the user is logged in
@login_verification
def logout():
    session.clear()
    flash("Logout success", 'success')
    return redirect(url_for('login'))

# create a dashboard page


@app.route("/dashboard")
# ensure the user is logged in
@login_verification
def dashboard():
    # a created table
    blockchain = get_blockchain().chain
    ct = time.strftime('%Y-%m-%d %H:%M:%S')
    balance = get_balance(session.get('username'))

    return render_template('dashboard.html', session=session, blockchain=blockchain, page='dashboard', ct=ct, balance=balance)


# create homepage


@app.route("/")
def index():
    return render_template('index.html')


@app.route('/chain', methods=['GET'])
def full_chain():

    response = {
        'chain': blockchain.chainJSONencode(),
        'length': len(blockchain.chain),
    }
    return response, 200

# blockchain DECENTRALIZED NODES


@app.route('/nodes/register', methods=['POST'])
def register_nodes():

    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:

        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return response, 201


if __name__ == '__main__':
    node = '127.0.0.1'

    blockchain.register_node(node)

    app.secret_key = 'secret123'
    app.run(host=node, port=5001, debug=True)
