# -*- coding: utf-8 -*-
"""
    :Authors: - qweqwe
"""

from flask import Blueprint, render_template, url_for, request, session, redirect, flash
from coltrane.db.models import User, Fac
from coltrane.website.oauth import facebook, twitter


auth = Blueprint('auth', __name__)

@auth.route('/')
def main():
    return render_template('index.html')


@auth.route('/twitter/login')
def twitter_login():
    return twitter.authorize(
        callback=url_for('auth.twitter_oauth_authorized',
            next=request.args.get('next') or request.referrer or None))


@auth.route('/facebook/login')
def facebook_login():
    return facebook.authorize(
        callback=url_for('auth.facebook_oauth_authorized',
            next=request.args.get('next') or request.referrer or None,
            _external=True))


# Login with Twitter
@auth.route('/twitter/callback')
@twitter.authorized_handler
def twitter_oauth_authorized(resp):
    next_url = request.args.get('next') or url_for('index')
    if resp is None:
        #TODO: replace with a normal page
        flash('You denied the request to sign in.')
        return redirect(next_url)

    #TODO: replace with the session token and normal storage
    session['twitter_token'] = (
        resp['oauth_token'],
        resp['oauth_token_secret']
    )

    session['twitter_user'] = resp['screen_name']

    flash('You were signed in as %s' % resp['screen_name'])
    return redirect(next_url)


# Login with Facebook
@auth.route('/facebook/callback')
@facebook.authorized_handler
def facebook_oauth_authorized(resp):
    next_url = request.args.get('next') or url_for('index')
    if resp is None:
        flash('Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        ))
        return redirect(next_url)

    session['facebook_token'] = (resp['access_token'], '')
    print resp['access_token']
    me = facebook.get('/me')
    return 'Logged in as id=%s name=%s redirect=%s' % \
            (me.data['id'], me.data['name'], request.args.get('next'))