# -*- coding: utf-8 -*-
"""
    :Authors: - qweqwe
"""

from flask import Flask, session, request, url_for, flash, redirect
from flaskext.oauth import OAuth
from .config import DefaultConfig as conf

oauth = OAuth()

facebook = oauth.remote_app('facebook',
    base_url            ='https://graph.facebook.com/',
    request_token_url   = None,
    authorize_url       ='https://www.facebook.com/dialog/oauth',
    access_token_url    ='/oauth/access_token',
    consumer_key        = conf.FACEBOOK_APP_ID,
    consumer_secret     = conf.FACEBOOK_APP_SECRET,
    request_token_params= {'scope': 'email'}
)

twitter = oauth.remote_app('twitter',
    base_url          ='http://api.twitter.com/1/',
    request_token_url ='http://api.twitter.com/oauth/request_token',
    authorize_url     ='http://api.twitter.com/oauth/authenticate',
    access_token_url  ='http://api.twitter.com/oauth/access_token',
    consumer_key      = conf.TWITTER_CONSUMER_KEY,
    consumer_secret   = conf.TWITTER_CONSUMER_SECRET,
)

@twitter.tokengetter
def get_twitter_token():
    #TODO: return twitter token from database by user.id
    return session.get('twitter_token')

@facebook.tokengetter
def get_facebook_token():
    #TODO: return facebook token from database by user.id
    return session['facebook_token']
