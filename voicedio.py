#!/usr/bin/env python

from __future__ import with_statement
from contextlib import closing
import sys
import os
from rdio import Rdio
from rdio_consumer_credentials import *

# quit if python version too low
if sys.version_info < (2, 5):
    print "Sorry, Python 2.5+ Required"
    sys.exit()

# web serve
from flask import Flask, request, escape, make_response, session, g, redirect, url_for, abort, render_template, flash, json, jsonify
app = Flask(__name__)

def top_track(sesh):
    access_token = sesh['at']
    access_token_secret = sesh['ats']
    if len(access_token) > 0 and len(access_token_secret) > 0 and access_token and access_token_secret:
        rdio = Rdio((RDIO_CONSUMER_KEY, RDIO_CONSUMER_SECRET), (access_token, access_token_secret))
        try:
            currentUser = rdio.call('currentUser')['result']
        except urllib2.HTTPError:
        # this almost certainly means that authentication has been revoked for the app. log out.
            return {"error" : "failure"}
        topcharts = rdio.call('getTopCharts', {'type': 'Track', 'count' : 100})
        playbackToken = rdio.call('getPlaybackToken', {'domain' : 'localhost'})
        import random
        randomint = random.randint(0,99)
        song = topcharts['result'][randomint]
        song['playbackToken'] = playbackToken['result']
        return song
    else:
        return {"error" : "failure"}

def rdio_search(query, sesh):
    access_token = sesh['at']
    access_token_secret = sesh['ats']
    if len(access_token) > 0 and len(access_token_secret) > 0 and access_token and access_token_secret:
        rdio = Rdio((RDIO_CONSUMER_KEY, RDIO_CONSUMER_SECRET), (access_token, access_token_secret))
        try:
            currentUser = rdio.call('currentUser')['result']
        except urllib2.HTTPError:
        # this almost certainly means that authentication has been revoked for the app. log out.
            return {"error" : "failure"}

        result = rdio.call('search', {'query' : query, 'types' : "Artist,Track" })
        result = result['result']['results']

        pop = result[0]

        while pop['type'] != 't':
            pop = result.pop(0)
        
        return pop

    else:
        return {"error" : "failure"}

@app.route('/')
def home():
    access_token = session['at']
    access_token_secret = session['ats']
    if len(access_token) > 0 and len(access_token_secret) > 0 and access_token and access_token_secret:
        rdio = Rdio((RDIO_CONSUMER_KEY, RDIO_CONSUMER_SECRET), (access_token, access_token_secret))
        try:
            currentUser = rdio.call('currentUser')['result']
        except urllib2.HTTPError:
        # this almost certainly means that authentication has been revoked for the app. log out.
            return redirect(url_for(logout))
        return render_template('search_form.html')
    else:
        return redirect(url_for('login'))

@app.route('/toptrack', methods=["POST"])
def get_top_track():
    sesh = session
    jsonres = top_track(sesh)
    return jsonify(jsonres)

@app.route('/search', methods=["POST"])
def search_it():
    query = request.form['query']
    sesh = session
    jsonres = rdio_search(query, sesh)
    return jsonify(jsonres)

@app.route('/login')
def login():
    session['at'] = ''
    session['ats'] = ''
    session['rt'] = ''
    session['rts'] = ''
    # begin the authentication process
    rdio = Rdio((RDIO_CONSUMER_KEY, RDIO_CONSUMER_SECRET))
    url = rdio.begin_authentication(callback_url = 'http://localhost:5000/callback')
    # save our request token in cookies
    session['rt'] = rdio.token[0]
    session['rts'] = rdio.token[1]
    # go to Rdio to authenticate the app
    return redirect(url)

@app.route('/callback')
def callback():
    request_token = session['rt']
    request_token_secret = session['rts']
    verifier = request.args["oauth_verifier"]
    
    # make sure we have everything we need
    if request_token and request_token_secret and verifier:
        # exchange the verifier and request token for an access token
        rdio = Rdio((RDIO_CONSUMER_KEY, RDIO_CONSUMER_SECRET), (request_token, request_token_secret))
        rdio.complete_authentication(verifier)
        # save the access token in cookies (and discard the request token)
        session['at'] = rdio.token[0]
        session['ats'] = rdio.token[1]
        session['rt'] = ''
        session['rts'] = ''

        # go to the home page
        return redirect(url_for('home'))
    else:
        # we're missing something important
        return redirect(url_for('logout'))
@app.route('/logout')
def logout():
    session['at'] = ''
    session['ats'] = ''
    session['rt'] = ''
    session['rts'] = ''
    return render_template('logout.html')


app.secret_key = '\x00\x84\x87ve]M&w\xcf\x1e\x17\nn\x04a_\x1f0\x0f\xb3g\xdfj'

app.config.from_object(__name__)
if __name__ == '__main__':
    app.run()