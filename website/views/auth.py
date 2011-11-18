# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, request, url_for, redirect
from website.forms import RegistrationForm, LoginForm
from website.models import  User
from website.extensions import db
from website.extensions.authentication import authentic


auth = Blueprint('login',__name__)

@auth.route('/login')
def main():
    return render_template('login.html')


@auth.route('/register', methods=['POST', 'GET'])
def register():
    form = RegistrationForm(request.form)
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    email=form.email.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('index.main'))
    return render_template('register.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form, csrf_enabled=False)
    if form.validate_on_submit():
        authentic.login(form.user)
        return redirect(url_for('index.main'))
    return render_template('login.html', form=form)


@auth.route('/users')
def users():
    return render_template('users.html', users=User.query.all())