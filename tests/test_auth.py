# -*- coding: utf-8 -*-
"""
Created on Sun Mar 24 18:27:23 2019

@author: M. Ibrahim
"""

import pytest
from TraderInsights import g, session, auth
from TraderInsights.db import get_db
from flask_wtf import FlaskForm
from flask import flash
from werkzeug import ImmutableMultiDict

import pytest
from flask import g, session
from flaskr.db import get_db


def test_register(client, app):
    assert client.get('/auth/newuser').status_code == 200
    response = client.post(
        '/auth/newuser', data={'email': 'admin@gmail.com', 'password': '123',
            'passconf': '123','tos': 'TOS', 'register': 'register'},
        follow_redirects=True
    )
    assert b'New User Profile' in response.data
    
    assert client.get('/auth/newprofile').status_code == 200
    response = client.post(
        '/auth/newprofile', data={'first': 'Jacob', 'last': 'Smith',
            'company': 'New World Inc.','addr': 'somewhere out there',
            'city': 'unknown', 'state': 'NM', 'zipcode': '99999',
            'finish': 'finish'},
        follow_redirects=True
    )
    assert b'Registration Complete' in response.data
    assert b'Congratulations!' in response.data
    
    with app.app_context():
        assert get_db().execute(
            "select * from users where email = 'admin@gmail.com'",
        ).fetchone() is not None


@pytest.mark.parametrize(('email', 'password', 'passconf', 'tos', 'register', 'cancel', 'good_msg', 'bad_msg'), (
    ('', '', '', '', '', 'cancel', [b'Redirecting', b'/auth/login'], []),
    ('', '', '', '', 'register', '',[], [b'Error(s)', b'Error']),
    ('', 'test', 'test', 'tos', 'register', '', [b'Error(s)', b'Email is required'], []),
    ('admin', 'test', 'test', 'tos', 'register', '', [b'Error(s)', b'Please provide a valid email'], []),
    ('admin@gmail', 'test', 'test', 'tos', 'register', '', [b'Error(s)', b'Please provide a valid email'], []),
    ('admin@gmail.c', 'test', 'test', 'tos', 'register', '', [b'Error(s)', b'Please provide a valid email'], []),
    ('admin@gmail.com', '', '', 'tos', 'register', '', [b'Error(s)', b'Password is required'], []),
    ('admin@gmail.com', 'test', '', 'tos', 'register', '', [b'Error(s)', b'Repeat password is required'], []),
    ('admin@gmail.com', 'test', 'test', '', 'register', '', [b'Error(s)', b'Please accept Terms of Service'], []),
    ('admin@gmail.com', 'test', '1234', 'tos', 'register', '', [b'Error(s)', b'Passwords must match'], []),
    ('admin@gmail.com', '12', '12', 'tos', 'register', '', [b'Error(s)', b'Password must be between 3 and 35 characters'], []),
    ('admin@gmail.com', '123456789012345678901234567890123456', '123456789012345678901234567890123456', 'tos', 'register', '', [b'Error(s)', b'Password must be between 3 and 35 characters'], []),
    ('admin@gmail.com', 'test', 'test', 'tos', 'register', '', [b'Redirecting', b'/auth/newprofile'], []),
    ('admin@mail.com', 'test', 'test', 'tos', 'register', '', [b'Error', b'admin@mail.com already exists'], [])
))
def test_register_validate_input(client, email, password, passconf, tos, register, cancel, good_msg, bad_msg):
    if register:
        response = client.post(
            '/auth/newuser',
            data={'email': email, 'password': password, 'passconf': passconf, 'tos': tos, 'register': register}
        )
    else:
        response = client.post(
            '/auth/newuser',
            data={'email': email, 'password': password, 'passconf': passconf, 'tos': tos, 'cancel': cancel}
        )
#    print(response.data)
#    print("\n\n")
    for message in good_msg:
        assert message in response.data
    
    for message in bad_msg:
        assert message not in response.data