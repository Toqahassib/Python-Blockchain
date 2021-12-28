from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from passlib.hash import sha256_crypt
from flask_mysqldb import MySQL
from sql import *
from wtforms import Form, StringField, PasswordField, validators


class RegisterForm(Form):
    name = StringField('Full Name', [validators.length(min=1, max=50)])
    username = StringField('Username', [validators.length(min=4, max=25)])
    email = StringField('Email', [validators.length(min=6, max=50)])
    password = PasswordField('Password', [validators.DataRequired(
    ), validators.EqualTo('confirm', message='Password dont match')])
    confirm = PasswordField('Confirm Password')


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

# function to login the user with session


def loggedin(username):
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
            loggedin(username)
            return redirect(url_for('dashboard'))
        else:
            flash('Username is taken, please try another one.', 'danger')
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
                loggedin(username)
                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid password", 'danger')
                return redirect(url_for('login'))

    return render_template('login.html')


@app.route("/logout")
# make sure the user is logged in
@loggedin
def logout():
    session.clear()
    flash("Logout success", 'success')
    return redirect(url_for('login'))

# create a dashboard page


@app.route("/dashboard")
def dashboard():
    # a created table

    return render_template('dashboard.html', session=session)

# create homepage


@app.route("/")
def index():
    # a created table

    return render_template('index.html')


if __name__ == '__main__':
    app.secret_key = 'secret123'
    app.run(debug=True)
