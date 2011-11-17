# -*- coding: utf-8 -*-
from  flaskext.wtf import (Form, TextField, PasswordField, DecimalField,
                           ValidationError, validators)
from models import User
from flaskext.bcrypt import check_password_hash



class RegistrationForm(Form):

    username = TextField("Username", [
        validators.Length(min=2, max=255),
        validators.Required(),
        validators.Regexp(r'^[a-zA-Z0-9_-]{2,255}$',
            message="Username should consist only of latin letters, numbers and dashes")
    ])

    email = TextField("Email address", [
        validators.Length(min=3, max=255),
        validators.Required(),
        validators.Email()
    ])
    
    password = PasswordField("Password", [validators.Required()])
    confirm  = PasswordField("Password Confirmation", [
        validators.EqualTo('password',
            message="Password confirmation must match password")
    ])


class LoginForm(Form):

    user = None

    username = TextField("Username", [
        validators.Length(min=2, max=255),
        validators.Required(),
        validators.Regexp(r'^[a-zA-Z0-9_-]{2,255}$',
            message="Username should consist only of latin letters, numbers and dashes")
    ])
    
    password = PasswordField("Password", [validators.Required()])

    def validate_username(self, field):
        self.user = User.objects(username=field.data).first()
        if not self.user:
            raise ValidationError("Wrong username")

    def validate_password(self, field):
        if not self.user:
            raise ValidationError("Wrong password")
        else:
            if not check_password_hash(self.user.pwdhash, field.data):
                self.user = None
                raise ValidationError("Wrong password")
