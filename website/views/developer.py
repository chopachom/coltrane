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
        app = Application.create(form.name.data,
                          form.domain.data,
                          form.description.data,
                          warden.current_user())
        return redirect(url_for('developer.app_details', domain=app.domain))
    return render_template('developer/create_app.html', form=form)


@developer.route('/apps/<domain>')
def app_details(domain):
    app = Application.get(domain=domain)
    return render_template('developer/app_details.html', app=app)

