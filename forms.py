from wtforms import Form, StringField, PasswordField, validators


class RegisterationForm(Form):
    name = StringField('Full Name', [validators.length(min=1, max=50)])
    username = StringField('Username', [validators.length(min=4, max=25)])
    email = StringField('Email', [validators.length(min=6, max=50)])
    password = PasswordField('Password', [validators.DataRequired(
    ), validators.EqualTo('confirm', message="Password doesn't match")])
    confirm_pwd = PasswordField('Confirm Password')
