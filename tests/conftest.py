# -*- coding: utf-8 -*-
"""
Created on Sun Mar 24 10:20:49 2019

@author: M. Ibrahim
"""

import os, tempfile, pytest
from TraderInsights import create_app
from TraderInsights.db import get_db, init_db

@pytest.fixture
def app():
    
    app = create_app({
        'TESTING': True,
    })

    with app.app_context():
        init_db(True)

    yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

class AuthActions(object):
    def __init__(self,client):
        self._client = client
    
    def login(self, email='admin@mail.com', password='password', login='Login'):
        if login=='Login':
            return self._client.post(
                '/auth/login',
                data=dict(email=email, password=password, login=login),
                follow_redirects=True
            )
        else:
            return self._client.post(
                '/auth/login',
                data=dict(register=login),
                follow_redirects=True
            )

    def logout(self):
        return self._client.get('/auth/logout')

@pytest.fixture
def auth(client):
    return AuthActions(client)