# -*- coding: utf-8 -*-
"""
    :Authors: - qweqwe
"""

from flask import Blueprint, render_template, url_for, request, session, redirect, flash
from coltrane.db.models import User, FacebookUser, TwitterUser
from coltrane.website.oauth import facebook, twitter
from coltrane.website.extensions.warden import warden

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=4)


auth = Blueprint('auth', __name__)

@auth.route('/')
def main():
    return render_template('index.html')


@auth.route('/twitter/login')
def twitter_login():
    #FIXME: This is dummy hack. Without this hack if we already have twitter's
    #oauth tokens, twitter would return error, probably because of Flask-Oauth
#    print 'twitter login'
    if session.get('twitter_token'):
        del session['twitter_token']
    return twitter.authorize(
        callback=url_for('auth.twitter_oauth_authorized',
            next=request.args.get('next') or request.referrer or None,
            _external=True))


@auth.route('/facebook/login')
def facebook_login():
    # see comments above
    if session.get('facebook_token'):
        del session['facebook_token']
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

    #TODO:FIXME:REMOVE THIS FUCKING SHAME
    session['twitter_token'] = (
        resp['oauth_token'],
        resp['oauth_token_secret']
    )

    credentials = twitter.get('/account/verify_credentials.json')
    twitter_user = TwitterUser.get(resp['screen_name'])
    #if we don't have such user i.e. user signs in for the first time
    if not twitter_user:
        # if user is not logged in then we should create a new account
        if not warden.current_user():
            #create new user and associate it with new twitter user
            nickname = None
            if not User.get(resp['screen_name']):
                nickname = resp['screen_name']
            user = User.create(nickname=nickname,
                first_name=credentials.data['name'])
            twitter_user = TwitterUser.create(user,
                resp['screen_name'], resp['user_id'],
                resp['oauth_token'], resp['oauth_token_secret'])
        # or, if user somehow logged in and signs in with twitter,
        # we should associate current account with twitter user
        else:
            user = warden.current_user()
            twitter_user = TwitterUser.create(user,
                resp['screen_name'], resp['user_id'],
                resp['oauth_token'], resp['oauth_token_secret'])
    #if we already have a user associated with this account then we shall
    # update tokens associated with this user
    else:
        user = twitter_user.user
        twitter_user.update_tokens(resp['oauth_token'], resp['oauth_token_secret'])

    warden.login(user)

#    TODO: replace with the session token and normal storage
#    session['twitter_token'] = (
#        resp['oauth_token'],
#        resp['oauth_token_secret']
#    )
#    session['twitter_user'] = resp['screen_name']

    flash('You were signed in as %s' % resp['screen_name'])
    return redirect(next_url)


# Login with Facebook
@auth.route('/facebook/callback')
@facebook.authorized_handler
def facebook_oauth_authorized(resp):
    next_url = request.args.get('next') or url_for('index')
    if resp is None:
        # TODO: do not show this error to user
        flash('Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        ))
        return redirect(next_url)
    #TODO:FIXME:REMOVE THIS FUCKING SHAME
    session['facebook_token'] = (resp['access_token'], '')
    me = facebook.get('/me')
    facebook_user = FacebookUser.get(me.data['id'])
    if not facebook_user:
        if not warden.current_user():
            nickname = None
            if me.data.get('username') and not User.get(me.data['username']):
                nickname = me.data['username']
            user = User.create(nickname, me.data.get('email'),
                first_name=me.data.get('first_name'),
                last_name=me.data.get('last_name')
            )
            facebook_user = FacebookUser.create(user, me.data['id'],
                resp['access_token'])
        else:
            user = warden.current_user()
            facebook_user = FacebookUser.create(user, me.data['id'],
                resp['access_token'])
    else:
        user = facebook_user.user
        facebook_user.update_token(resp['access_token'])

    warden.login(user)

    return redirect(next_url)

    #return 'Logged in as id=%s name=%s redirect=%s' % (me.data['id'], me.data['name'], request.args.get('next'))