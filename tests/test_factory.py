# -*- coding: utf-8 -*-
"""
Created on Sun Mar 24 17:41:01 2019

@author: M. Ibrahim
"""

from SD_website import create_app
from flask import g, redirect, url_for, session, render_template
from wtforms import Form

def test_config():
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing

def test_welcome(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Welcome' in response.data
    assert b'log in' in response.data
    assert b'create an account' in response.data