# -*- coding: utf-8 -*-
from  flaskext.wtf import (Form, TextField, PasswordField, TextAreaField,
                           DecimalField, ValidationError, validators)
from website.extensions.warden import warden
from website.models import User, Application
from flaskext.bcrypt import check_password_hash



class RegistrationForm(Form):

    nickname = TextField("Username", [
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
        self.user = User.get(nickname=field.data)
        if not self.user:
            raise ValidationError("Wrong username")

    def validate_password(self, field):
        if not self.user:
            raise ValidationError("Wrong password")
        else:
            if not check_password_hash(self.user.pwd_hash, field.data):
                self.user = None
                raise ValidationError("Wrong password")



class CreateAppForm(Form):

    name =  TextField("App name", [
        validators.Length(min=2, max=255),
        validators.Required()
    ])

    description = TextAreaField("Description")

    #TODO: TO LOWEr
    domain = TextField("App domain", [
        validators.Length(min=2, max=255),
        validators.Required(),
        validators.Regexp(r'^[a-zA-Z0-9]{1}[a-zA-Z0-9_-]{2,253}[a-zA-Z0-9]{1}$',
            message="App domain may consist only of latin letters, numbers and dashes")
    ])

    def validate_domain(self, field):
        app = Application.get(domain=field.data, author=warden.current_user())
        if app:
            raise ValidationError("Domain already taken")