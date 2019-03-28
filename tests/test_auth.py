# -*- coding: utf-8 -*-
"""
Created on Sun Mar 24 18:27:23 2019

@author: M. Ibrahim
"""

import pytest
from TraderInsights import g, session
from TraderInsights.db import get_db
from flask_wtf import FlaskForm
from flask import flash
from werkzeug import ImmutableMultiDict


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
    ('', '', '', '', '', 'cancel', [b'Trader Insights - Login'], [b'Error(s)', b'Error']),
    ('', '', '', '', 'register', '', [b'Error(s)', b'Email is required', b'Password is required', b'Repeat password is required', b'Please accept Terms of Service'], [b'Trader Insights - New user Profile']),
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
    ('admin@gmail.com', 'test', 'test', 'tos', 'register', '', [b'Trader Insights - New User Profile'], []),
    ('admin@mail.com', 'test', 'test', 'tos', 'register', '', [b'Error', b'admin@mail.com already exists'], [])
))
def test_register_validate_input(client, email, password, passconf, tos, register, cancel, good_msg, bad_msg):
    if register:
        response = client.post(
            '/auth/newuser',
            data={'email': email, 'password': password, 'passconf': passconf, 'tos': tos, 'register': register},
            follow_redirects=True
        )
    else:
        response = client.post(
            '/auth/newuser',
            data={'email': email, 'password': password, 'passconf': passconf, 'tos': tos, 'cancel': cancel},
            follow_redirects=True
        )
    
    for message in good_msg:
        assert message in response.data
    
    for message in bad_msg:
        assert message not in response.data

@pytest.mark.parametrize(('first', 'last', 'company', 'addr', 'city', 'state', 'zipcode', 'finish', 'cancel', 'good_msg', 'bad_msg'), (
    ('', '', '', '', '', '', '', '', 'cancel', [b'Trader Insights - Login'], [b'Error(s)', b'Error']),
    ('', '', '', '', '', '', '', 'finish', '', [b'Error(s)', b'Please input First Name', b'Please input Last Name', b'Please input Company', b'company\'s Street Address', b'Please input City', b'State abbreviation', b'-digit Zipcode'], []),
    ('', 'Doe', 'John Doe Ltd.', '1234 Main St.', 'Houston', 'TX', '77002', 'finish', '', [b'Error(s)', b'Please input First Name'], [b'Please input Last Name', b'Please input Company', b'company\'s Street Address', b'Please input City', b'State abbreviation', b'-digit Zipcode']),
    ('John', '', 'John Doe Ltd.', '1234 Main St.', 'Houston', 'TX', '77002', 'finish', '', [b'Error(s)', b'Please input Last Name'], [b'Please input First Name', b'Please input Company', b'company\'s Street Address', b'Please input City', b'State abbreviation', b'-digit Zipcode']),
    ('John', 'Doe', '', '1234 Main St.', 'Houston', 'TX', '77002', 'finish', '', [b'Error(s)', b'Please input Company'], [b'Please input First Name', b'Please input Last Name', b'company\'s Street Address', b'Please input City', b'State abbreviation', b'-digit Zipcode']),
    ('John', 'Doe', 'John Doe Ltd.', '', 'Houston', 'TX', '77002', 'finish', '', [b'Error(s)', b'company\'s Street Address'], [b'Please input First Name', b'Please input Last Name', b'Please input Company', b'Please input City', b'State abbreviation', b'-digit Zipcode']),
    ('John', 'Doe', 'John Doe Ltd.', '1234 Main St.', '', 'TX', '77002', 'finish', '', [b'Error(s)', b'Please input City'], [b'Please input First Name', b'Please input Last Name', b'Please input Company', b'company\'s Street Address', b'State abbreviation', b'-digit Zipcode']),
    ('John', 'Doe', 'John Doe Ltd.', '1234 Main St.', 'Houston', '', '77002', 'finish', '', [b'Error(s)', b'State abbreviation'], [b'Please input First Name', b'Please input Last Name', b'Please input Company', b'company\'s Street Address', b'Please input City', b'-digit Zipcode']),
    ('John', 'Doe', 'John Doe Ltd.', '1234 Main St.', 'Houston', 'TX', '', 'finish', '', [b'Error(s)', b'-digit Zipcode'], [b'Please input First Name', b'Please input Last Name', b'Please input Company', b'company\'s Street Address', b'Please input City', b'State abbreviation']),
    ('John', 'Doe', 'John Doe Ltd.', '1234 Main St.', 'Houston', 'TX', '7702', 'finish', '', [b'Error(s)', b'-digit Zipcode'], [b'Please input First Name', b'Please input Last Name', b'Please input Company', b'company\'s Street Address', b'Please input City', b'State abbreviation']),
    ('John', 'Doe', 'John Doe Ltd.', '1234 Main St.', 'Houston', 'TX', '770022', 'finish', '', [b'Error(s)', b'-digit Zipcode'], [b'Please input First Name', b'Please input Last Name', b'Please input Company', b'company\'s Street Address', b'Please input City', b'State abbreviation']),
    ('John', 'Doe', 'John Doe Ltd.', '1234 Main St.', 'Houston', 'TX', '77002', 'finish', '', [b'Trader Insights - Registration Complete'], [b'Error(s)', b'Please input First Name', b'Please input Last Name', b'Please input Company', b'company\'s Street Address', b'Please input City', b'State abbreviation', b'-digit Zipcode']),
    ('John', 'Doe', 'John Doe Ltd.', '1234 Main St.', 'Houston', 'TX', '770025096', 'finish', '', [b'Trader Insights - Registration Complete'], [b'Error(s)', b'Please input First Name', b'Please input Last Name', b'Please input Company', b'company\'s Street Address', b'Please input City', b'State abbreviation', b'-digit Zipcode']),
))
def test_initProfile_validate_input(client, first, last, company, addr, city, state, zipcode, finish, cancel, good_msg, bad_msg):
    response = client.post(
        '/auth/newuser', data={'email': 'admin@gmail.com', 'password': '123',
            'passconf': '123','tos': 'TOS', 'register': 'register'},
        follow_redirects=True
    )
    if finish:
        response = client.post(
            '/auth/newprofile',
            data={'first': first, 'last': last, 'company': company, 'addr': addr, 'city': city, 'state': state, 'zipcode': zipcode, 'finish': finish},
            follow_redirects=True
        )
    else:
        response = client.post(
            '/auth/newprofile',
            data={'first': first, 'last': last, 'company': company, 'addr': addr, 'city': city, 'state': state, 'zipcode': zipcode, 'cancel': cancel},
            follow_redirects=True
        )
    
    for message in good_msg:
        assert message in response.data
    
    for message in bad_msg:
        assert message not in response.data

def test_login(client, auth):
    assert client.get('/auth/login').status_code == 200
    response = auth.login()
    
    assert b'Welcome John' in response.data
    
    with client:
        client.get('/')
        assert session['email'] == 'admin@mail.com'
        assert g.user['email'] == 'admin@mail.com'

@pytest.mark.parametrize(('emails', 'passwords', 'login', 'messages'), (
    ([''], [''], 'Register', [[b'Trader Insights - New User']]),
    ([''], ['123'], 'Login', [[b'Error(s)', b'Email is required']]),
    (['admin@gmail.com'], [''], 'Login', [[b'Error(s)', b'Password is required']]),
    (['admin@gmail.com'], ['123'], 'Login', [[b'Error', b'is incorrect', b'Try again']]),
    (['admin@gmail.com'], ['12'], 'Login', [[b'Error(s)', b'Password must be between 3 and 35 characters']]),
    (['admin@gmail.com'], ['123456789012345678901234567890123456'], 'Login', [[b'Error(s)', b'Password must be between 3 and 35 characters']]),
    (['admin@mail.com','admin@mail.com','admin@mail.com','admin@mail.com','admin@mail.com','admin@mail.com'], ['test', 'test', 'test', 'test', 'test', 'password'], 'Login', [[b'Error', b'is incorrect', b'Try again'], [b'Error', b'is incorrect', b'Try again'], [b'Error', b'is incorrect', b'Try again'], [b'Error', b'is incorrect', b'Try again'], [b'Error', b'is incorrect', b'Account is locked', b'Contact Customer Support'], [b'Error', b'Account is locked', b'Contact Customer Support']]),
    (['python@mail.com'], ['python'], 'Login', [[b'Welcome Johann']]),
))
def test_login_validate_input(auth, emails, passwords, login, messages):
    for email, password, message in zip(emails, passwords, messages):
        response = auth.login(email, password, login)
        for msg in message:
            assert msg in response.data

def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'email' not in session
