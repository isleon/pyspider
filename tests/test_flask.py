#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, render_template, request
try:
    import flask_login as login
except ImportError:
    from flask.ext import login

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'


'''
@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        if valid_login(request.form['username'],
                       request.form['password']):
            return log_the_user_in(request.form['username'])
        else:
            error = 'Invalid username/password'
    # the code below is executed if the request method
    # was GET or the credentials were invalid
    return render_template('login.html', error=error)
'''

# %%
import pandas as pd
