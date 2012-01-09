__author__ = 'qweqwe'

from flask import Blueprint, render_template, request, url_for, redirect
from coltrane.website.forms import CreateAppForm
from coltrane.db.models import  Application, User
from coltrane.website.extensions.warden import warden


appstore = Blueprint('appstore', __name__)


@appstore.route('/')
def index():
    apps = Application.all()
    return render_template('appstore/index.html', apps=apps)


@appstore.route('/details/<nickname>')
def by_author(nickname):
    author = User.get(nickname)
    apps = Application.find(author)
    return render_template('appstore/by_author.html', apps=apps, author=author)


@appstore.route('/details/<nickname>/<domain>')
def details(nickname, domain):
    app = Application.get(domain, nickname)
    return render_template('appstore/details.html', app=app)

