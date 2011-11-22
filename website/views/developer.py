# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, request, url_for, redirect
from website.forms import CreateAppForm
from website.models import  Developer, Application
from website.extensions import db
from website.extensions.warden import warden


developer = Blueprint('developer', __name__)
warden.protect(developer)


@developer.route('/')
def main():
    pass

#TODO: unique constraints for app_domain
@developer.route('/create-app', methods=['GET', 'POST'])
def create_app():
    form = CreateAppForm(request.form)
    if form.validate_on_submit():
        app = Application(form.app_name.data,
                          form.app_domain.data,
                          warden.current_user())
        db.session.add(app)
        db.session.commit()
    return render_template('developer/create_app.html', form=form)

