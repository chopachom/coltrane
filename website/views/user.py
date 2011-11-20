# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, request, url_for, redirect
from website.forms import RegistrationForm, LoginForm
from models import  User, Developer
from website.extensions import db
from website.extensions.warden import warden


user = Blueprint('user',__name__)

@user.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form, csrf_enabled=False)
    if form.validate_on_submit():
        warden.login(form.user)
        return redirect(url_for('index.main'))
    return render_template('login.html', form=form)


@user.route('/signup', methods=['POST', 'GET'])
def signup():
    form = RegistrationForm(request.form)
    if form.validate_on_submit():
        user = User(nickname=form.nickname.data,
                    email=form.email.data,
                    password=form.password.data)
        developer = Developer(user=user)
        db.session.add_all([user, developer])
        db.session.commit()
        warden.login(user)
        return redirect(url_for('index.main'))
    return render_template('signup.html', form=form)



@user.route('/users')
def users():
    return render_template('users.html', users=User.query.all())