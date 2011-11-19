# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, request, url_for, redirect
from website.forms import RegistrationForm, LoginForm
from website.models import  User
from website.extensions import db
from website.extensions.authentication import authentic


user = Blueprint('user',__name__)

@user.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form, csrf_enabled=False)
    if form.validate_on_submit():
        authentic.login(form.user)
        return redirect(url_for('index.main'))
    return render_template('login.html', form=form)


@user.route('/register', methods=['POST', 'GET'])
def register():
    form = RegistrationForm(request.form)
    if form.validate_on_submit():
        user = User(nickname=form.nickname.data,
                    email=form.email.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('index.main'))
    return render_template('register.html', form=form)



@user.route('/users')
def users():
    return render_template('users.html', users=User.query.all())