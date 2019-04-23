# -*- coding: utf-8 -*-
"""
Created on Thu Mar 28 23:43:07 2019

@author: M. Ibrahim
"""

import pytest
from TraderInsights.db import get_db
from werkzeug.security import check_password_hash

def test_profile_change(client, auth, app):
    auth.login()
    fullname, company, addr1,addr2, city, state, zipcode, password, button = 'Jose Dose', 'Dose Dudes LLC', '4321 Moan Street','', 'Hooston', 'AL', '22997', 'password', 'submit'
    with app.app_context():
        [conn,cur] = get_db()

        cur.execute(
            "SELECT full_name, company_name, addr1,addr2, city, state, zipcode FROM users WHERE email='admin@mail.com'"
        )
        user = cur.fetchone()
        assert user is not None

    assert client.get('/tools/admin@mail.com/profile').status_code == 200
    response = client.post(
        '/tools/admin@mail.com/profile', data={'fullname': fullname,
            'company': company, 'addr1': addr1,'addr2': addr2 ,'city': city, 'state': state,
            'zipcode': zipcode, 'currpass': password, 'newpass': '', 'submit': button},
        follow_redirects=True
    )
    assert b'Jose' in response.data
    assert b'Dose' in response.data
    assert b'Dose Dudes LLC' in response.data
    assert b'4321 Moan Street' in response.data
    assert b'Hooston' in response.data
    assert b'AL' in response.data
    assert b'22997' in response.data
    assert b'Information updated!' in response.data

    with app.app_context():
        [conn,cur] = get_db()
        cur.execute(
            "SELECT full_name, company_name, addr1,addr2, city, state, zipcode FROM users WHERE email='admin@mail.com'"
        )
        user = cur.fetchone()

        assert user is not None
        assert [fullname, company, addr1,addr2, city, state, zipcode] == [user[i] for i in range(len(user))]

    fullname, company, addr1,addr2, city, state, zipcode, currpass, newpass, confpass, button = 'John Doe', 'John Doe Ltd', '1234 Main St','', 'Houston', 'TX', '77002', 'password', 'newpass', 'newpass', 'submit'
    with app.app_context():
        [conn,cur] = get_db()
        cur.execute(
            "SELECT full_name, company_name, addr1,addr2, city, state, zipcode FROM users WHERE email='admin@mail.com'"
        )
        user = cur.fetchone()

    assert client.get('/tools/admin@mail.com/profile').status_code == 200
    response = client.post(
        '/tools/admin@mail.com/profile', data={'fullname': fullname,
            'company': company, 'addr1': addr1, 'addr2': addr2, 'city': city, 'state': state,
            'zipcode': zipcode, 'currpass': currpass, 'newpass': newpass,
            'confpass': confpass, 'submit': button},
        follow_redirects=True
    )

    assert b'John Doe' in response.data
    assert b'John Doe Ltd' in response.data
    assert b'1234 Main St' in response.data
    assert b'Houston' in response.data
    assert b'TX' in response.data
    assert b'77002' in response.data
    assert b'Information updated!' in response.data
    assert b'New password stored!' in response.data

    with app.app_context():
        [conn,cur] = get_db()
        cur.execute(
            "SELECT password, full_name, company_name, addr1,addr2, city, state, zipcode FROM users WHERE email='admin@mail.com'"
        )
        user = cur.fetchone()

        assert user is not None
        assert [newpass, fullname, company, addr1,addr2, city, state, zipcode] == [user[i] for i in range(len(user))]

@pytest.mark.parametrize(('fullname','company','addr1','addr2','city','state','zipcode','password','newpass','confpass','button','good_msg','bad_msg'),(
        ('','','','','','TX','','','','','cancel', [b'Home Page', b'Welcome John Doe'], [b'Profile Management']),
        ('','','','','','TX','','','','','submit', [b'Profile Management', b'Error(s)', b'Please input Full Name', b'Please input Company',
            b'Please input company\'s Street Address', b'Please input City', b'5- or 9-digit Zipcode',
            b'Please enter password to update profile or change password'], [b'Home Page']),
        ('', 'Dose Dudes LLC', '4321 Moan Street', '', 'Hooston', 'AL', '22997', 'password', 'newpass', 'newpas', 'submit', [b'Profile Management',
            b'Error(s)', b'Please input Full Name'], [b'Home Page', b'Please input Company', b'Please input company\'s Street Address', b'Please input City',
            b'2-letter State abbreviation', b'5- or 9-digit Zipcode', b'Please enter password to update profile or change password']),
        ('Jose Dose','','4321 Moan Street','','Hooston','AL','22997','password','newpass','newpas','submit', [b'Profile Management', b'Error(s)', b'Please input Company'],
            [b'Home Page', b'Please input First Name', b'Please input Last Name', b'Please input company\'s Street Address', b'Please input City',
            b'2-letter State abbreviation', b'5- or 9-digit Zipcode', b'Please enter password to update profile or change password']),
        ('Jose Dose','Dose Dudes LLC','','','Hooston','AL','22997','password','','','submit', [b'Profile Management', b'Error(s)', b'Please input company\'s Street Address'],
            [b'Home Page', b'Please input First Name', b'Please input Last Name', b'Please input Company', b'Please input City', b'2-letter State abbreviation',
            b'5- or 9-digit Zipcode', b'Please enter password to update profile or change password']),
        ('Jose Dose','Dose Dudes LLC','4321 Moan Street','','','AL','22997','password','','','submit', [b'Profile Management', b'Error(s)', b'Please input City'],
            [b'Home Page', b'Please input First Name', b'Please input Last Name', b'Please input Company', b'Please input company\'s Street Address',
            b'2-letter State abbreviation', b'5- or 9-digit Zipcode', b'Please enter password to update profile or change password']),
        ('Jose Dose','Dose Dudes LLC','4321 Moan Street','','Hooston','AL','','password','','','submit', [b'Profile Management', b'Error(s)', b'5- or 9-digit Zipcode'],
            [b'Home Page', b'Please input First Name', b'Please input Last Name', b'Please input Company', b'Please input company\'s Street Address', b'Please input City',
            b'2-letter State abbreviation', b'Please enter password to update profile or change password']),
        ('Jose Dose','Dose Dudes LLC','4321 Moan Street','','Hooston','AL','22997','badpassword','','','submit', [b'Profile Management', b'Incorrect password'], [b'Home Page',
            b'Error(s)', b'Please input First Name', b'Please input Last Name', b'Please input Company', b'Please input company\'s Street Address', b'Please input City',
            b'2-letter State abbreviation', b'5- or 9-digit Zipcode', b'Please enter password to update profile or change password']),
        ('Jose Dose','Dose Dudes LLC','4321 Moan Street','','Hooston','AL','22997','password','01','01','submit', [b'Profile Management', b'Error(s)',
            b'New password must be between 3 and 35 characters'], [b'Home Page', b'Please input First Name', b'Please input Last Name', b'Please input Company',
            b'Please input company\'s Street Address', b'Please input City', b'2-letter State abbreviation', b'5- or 9-digit Zipcode',
            b'Please enter password to update profile or change password']),
        ('Jose Dose','Dose Dudes LLC','4321 Moan Street','','Hooston','AL','22997','password','0123456789012345678901234567890123456','0123456789012345678901234567890123456',
            'submit', [b'Profile Management', b'Error(s)', b'New password must be between 3 and 35 characters'], [b'Home Page', b'Please input First Name', b'Please input Last Name',
            b'Please input Company', b'Please input company\'s Street Address', b'Please input City', b'2-letter State abbreviation', b'5- or 9-digit Zipcode',
            b'Please enter password to update profile or change password']),
        ('Jose Dose','Dose Dudes LLC','4321 Moan Street','','Hooston','AL','22997','password','newpass','badnewpass','submit', [b'Profile Management', b'Error(s)',
            b'Passwords must match'], [b'Home Page', b'Please input First Name', b'Please input Last Name', b'Please input Company', b'Please input company\'s Street Address',
            b'Please input City', b'2-letter State abbreviation', b'5- or 9-digit Zipcode', b'Please enter password to update profile or change password']),
        ('Jose Dose', 'Dose Dudes LLC', '4321 Moan Street', 'does it matter', 'Hooston', 'AL', '22997', 'password', '', '', 'submit',
            [b'Profile Management'], [b'Error(s)', b'Please input Full Name', b'Home Page', b'Please input Company', b'Please input company\'s Street Address',
            b'Please input City', b'2-letter State abbreviation', b'5- or 9-digit Zipcode', b'Please enter password to update profile or change password']),
))
def test_validate_profile_input(auth, client, app, fullname, company, addr1, addr2, city, state, zipcode, password, newpass, confpass, button, good_msg, bad_msg):
    auth.login()
    if button == 'submit':

        response = client.post(
            '/tools/admin@mail.com/profile', data={'fullname': fullname,
                'company': company, 'addr1': addr1, 'addr2': addr2, 'city': city, 'state': state,
                'zipcode': zipcode, 'currpass': password, 'newpass': newpass,
                'confpass': confpass, 'submit': button},
            follow_redirects=True
        )

        if b'Incorrect password' in response.data:
            with app.app_context():
                [conn,cur] = get_db()
                cur.execute(
                    "SELECT password FROM users WHERE email='admin@mail.com'"
                )
                pw = cur.fetchone()
                assert not check_password_hash(pw[0],password)
        elif b'update profile or change password' not in response.data:
            with app.app_context():
                [conn,cur] = get_db()
                cur.execute(
                    "SELECT password FROM users WHERE email='admin@mail.com'"
                )
                pw = cur.fetchone()
                assert check_password_hash(pw[0],password)

        if newpass and b'Error(s)' not in response.data:
            with app.app_context():
                [conn,cur] = get_db()
                cur.execute(
                    "SELECT password FROM users WHERE email='admin@mail.com'"
                )
                pw = cur.fetchone()
                assert check_password_hash(pw[0],newpass)
    else:
        response = client.post(
            '/tools/admin@mail.com/profile', data={'fullname': fullname,
                'company': company, 'addr1': addr1, 'addr2': addr2, 'city': city, 'state': state,
                'zipcode': zipcode, 'currpass': password, 'newpass': newpass,
                'confpass': confpass, 'cancel': button},
            follow_redirects=True
        )

    for msg in good_msg:
        assert msg in response.data

    for msg in bad_msg:
        assert msg not in response.data

def test_history(client, auth, app):
    auth.login()

    response = client.post('/tools/admin@mail.com/history', follow_redirects=True)
    assert response.status_code == 200

    assert b'No orders placed yet!' in response.data

    #Place order 1
    assert client.get('/request/admin@mail.com/quote').status_code == 200
    response = client.post(
        '/request/admin@mail.com/quote', data={'gal': '500', 'deliv_date': '2020-07-31',
                                               'deliv_time': '05:00', 'proceed': 'Proceed'},
        follow_redirects=True
    )

    assert b'Quote Order Confirmation' in response.data
    assert b'Gallons Requested: 500' in response.data
    assert b'Delivery Date: 2020-07-31 05:00' in response.data

    assert client.get('/request/admin@mail.com/quote-confirm').status_code == 200
    response = client.post(
        '/request/admin@mail.com/quote-confirm',
        data={'confirm': 'Confirm'},
        follow_redirects=True
    )

    assert b'Order Placed' in response.data
    assert b'to return to home page' in response.data

    with app.app_context():
        [conn, cur] = get_db()
        cur.execute("select * from history")
        order = cur.fetchone()
        assert order is not None
    print("order 1 placed")

    # Place order 2
    assert client.get('/request/admin@mail.com/quote').status_code == 200
    response = client.post(
        '/request/admin@mail.com/quote', data={'gal': '1500', 'deliv_date': '2021-01-31',
                                               'deliv_time': '05:00', 'proceed': 'Proceed'},
        follow_redirects=True
    )

    assert b'Quote Order Confirmation' in response.data
    assert b'Gallons Requested: 1500' in response.data
    assert b'Delivery Date: 2021-01-31 05:00' in response.data

    assert client.get('/request/admin@mail.com/quote-confirm').status_code == 200
    response = client.post(
        '/request/admin@mail.com/quote-confirm',
        data={'confirm': 'Confirm'},
        follow_redirects=True
    )

    assert b'Order Placed' in response.data
    assert b'to return to home page' in response.data

    with app.app_context():
        [conn, cur] = get_db()
        cur.execute("select * from history")
        order = cur.fetchone()
        assert order is not None
    print("order 2 placed")

    response = client.post('/tools/admin@mail.com/history', follow_redirects=True)
    assert response.status_code == 200

    print(response.data)

    x = [b'Date', b'Full Name', b'Company', b'Address 1', b'Address 2', b'City', b'State', b'Zipcode', b'Gallons', b'Fuel Factor', b'Location Factor', b'History Factor', b'Seasonal Factor', b'$/Gal', b'Total ($)']

    for header in x:
        assert header in response.data

    info = [b'<td>2020-07-31 05:00:00</td><td>John Doe</td><td>John Doe Ltd.</td><td>1234 Main St.</td><td></td><td>Houston</td><td>TX</td><td>77002</td><td>500</td><td>0.03</td><td>0.02</td><td>0</td><td>0.15</td><td>1.950</td><td>975.00</td>',
            b'<td>2021-01-31 05:00:00</td><td>John Doe</td><td>John Doe Ltd.</td><td>1234 Main St.</td><td></td><td>Houston</td><td>TX</td><td>77002</td><td>1500</td><td>0.02</td><td>0.02</td><td>0.01</td><td>0.05</td><td>1.770</td><td>2655.00</td>']
    for row in info:
        assert row in response.data