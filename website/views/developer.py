# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, request, url_for, redirect
from website.forms import CreateAppForm
from db import  Developer, Application
from website.extensions import db
from website.extensions.warden import warden


developer = Blueprint('developer', __name__)
warden.protect(developer)


@developer.route('/')
def main():
    pass

@developer.route('/create-app', methods=['GET', 'POST'])
def create_app():
    form = CreateAppForm(request.form)
    return render_template('developer/create_app.html', form=form)

