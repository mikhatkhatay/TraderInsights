# -*- coding: utf-8 -*-
"""
Created on Sun Mar 24 10:20:49 2019

@author: M. Ibrahim
"""

import os, tempfile, pytest
from TraderInsights import create_app
from TraderInsights.db import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')

@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app({
        'TESTING': False,
        'DATABASE': db_path,
        'WTF_CSRF_ENABLED': False
    })
    
    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)
    
    yield app
    
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

class AuthActions(object):
    def __init__(self,client):
        self._client = client
    
    def login(self, email='admin@mail.com', password = 'password'):
        return self._client.post(
            '/auth/login',
            data=dict(email=email, password=password)
        )
    
    def logout(self):
        return self._client.get('/auth/logout')

@pytest.fixture
def auth(client):
    return AuthActions(client)