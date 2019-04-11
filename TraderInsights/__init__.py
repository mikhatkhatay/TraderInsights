# -*- coding: utf-8 -*-
"""
Team: Fund_Khatkhatay_Zaidi
File Description: Setting up the Application Factory and main page for user
"""

import os

from flask import Flask, redirect, render_template, url_for, g, request, session
from wtforms import Form
from flask_wtf import FlaskForm
from .userButtons import userButtons
import psycopg2
from psycopg2 import pool

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )
    app.config['postgreSQL_pool'] = psycopg2.pool.SimpleConnectionPool(1,20,
              "user='ian' password='password' dbname='testdb' host='localhost'")
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)
    
    
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    @app.route('/', methods=('GET', 'POST'))
    def welcome():
        if g.user:
            return redirect(url_for('userPage', email=session['email']))
        else:
            return render_template('homepage.html', form=Form)
    
    from . import db
    db.init_app(app)
    
    from . import auth
    app.register_blueprint(auth.bp)
    
    from . import req
    app.register_blueprint(req.bp)
    
    from . import usertools
    app.register_blueprint(usertools.bp)
    
    @app.route('/<email>', methods=('GET','POST'))
    @auth.login_required
    def userPage(email):
        form = FlaskForm
        if request.method == "POST":
            button = userButtons(request.form)
            if button is not None:
                return button
        return render_template("userPage.html", form=form, session=session)
    
    return app