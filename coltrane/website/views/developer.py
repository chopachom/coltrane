# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, request,\
                  url_for, redirect, current_app

from coltrane.website.forms import CreateAppForm, EditAppForm
from coltrane.db.models import  Developer, Application
from coltrane.db.extension import db
from coltrane.website.extensions.warden import warden

import zipfile
import os

developer = Blueprint('developer', __name__)
warden.protect(developer)


@developer.route('/')
@developer.route('/apps/')
def index():
    developers_app = Application.find(author=warden.current_user())
    return render_template('developer/index.html', apps=developers_app)


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
    app = Application.get(domain=domain, author=warden.current_user())
    return render_template('developer/app_details.html', app=app)


#TODO: load the edit form at app_details page when user presses edit button
#TODO: set the maximum file size
@developer.route('/apps/<domain>/edit', methods=['GET', 'POST'])
def edit_app(domain):
    app = Application.get(domain=domain, author=warden.current_user())
    form = EditAppForm(request.form, name=app.domain, description=app.description)
    if form.validate_on_submit():
        file = request.files['zipfile']
        if zipfile.is_zipfile(file):
            with zipfile.ZipFile(file) as _zipfile:
                os.umask(022)
                path2appfiles = apps_files_path(app.author.nickname, app.domain)
                _zipfile.extractall(path2appfiles)
    return render_template('developer/edit_app.html', form=form)


ALLOWED_EXTENSIONS = {'zip',}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def apps_files_path(username, domain):
    webroot = os.path.join(current_app.config['WEBROOT'], 'webroot')
    return os.path.join(webroot, username, domain)



