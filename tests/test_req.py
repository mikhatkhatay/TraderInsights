# -*- coding: utf-8 -*-
"""
Created on Thu Mar 28 23:42:59 2019

@author: M. Ibrahim
"""

import pytest
from TraderInsights.db import get_db

def test_place_order(client, auth, app):
    auth.login()
    assert client.get('/request/admin@mail.com/quote').status_code == 200
    response = client.post(
        '/request/admin@mail.com/quote', data={'gal': '500', 'deliv_date': '2020-07-31',
            'deliv_time': '05:00','proceed': 'Proceed'},
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

@pytest.mark.parametrize(('gallons','deliv_date','deliv_time','button','good_msg','bad_msg'),(
        ('','','','cancel', [b'Home Page', b'Welcome John'], [b'Quote Form', b'Quote Order Confirmation']),
        ('','','','proceed', [b'Quote Form', b'Error(s)', b'Fuel amount is required', b'Delivery date is required', b'Delivery time is required'], [b'Home Page', b'Welcome John', b'Quote Order Confirmation']),
        ('','2020-07-31','05:00','proceed', [b'Quote Form', b'Error(s)', b'Fuel amount is required'], [b'Quote Order Confirmation', b'Cannot deliver in the past']),
        ('0','2020-07-31','05:00','proceed', [b'Quote Form', b'Error(s)', b'Please enter a valid amount (greater than zero)'], [b'Fuel amount is required', b'Quote Order Confirmation', b'Cannot deliver in the past']),
        ('-500','2020-07-31','05:00','proceed', [b'Quote Form', b'Error(s)', b'Please enter a valid amount (greater than zero)'], [b'Fuel amount is required', b'Quote Order Confirmation', b'Cannot deliver in the past']),
        ('500','','05:00','proceed', [b'Quote Form', b'Error(s)', b'Delivery date is required'], [b'Quote Order Confirmation']),
        ('500','2020-07-31','','proceed', [b'Quote Form', b'Error(s)', b'Delivery time is required'], [b'Quote Order Confirmation', b'Cannot deliver in the past']),
        ('500','2019-03-05','05:00','proceed', [b'Quote Form', b'Error(s)', b'Cannot deliver in the past'], [b'Quote Order Confirmation']),
        ('500','2019-04-27','05:00','proceed', [b'Quote Form', b'Error(s)', b'Please allow at least 10 business days for delivery'], [b'Quote Order Confirmation'])
))
def test_validate_quote_input(auth, client, gallons, deliv_date, deliv_time, button, good_msg, bad_msg):
    auth.login()
    if button == 'proceed':
        response = client.post(
            '/request/admin@mail.com/quote',
            data={'gal': gallons, 'deliv_date': deliv_date, 'deliv_time': deliv_time, 'proceed': button},
            follow_redirects=True
        )
    else:
        response = client.post(
            '/request/admin@mail.com/quote',
            data={'gal': gallons, 'deliv_date': deliv_date, 'deliv_time': deliv_time, 'cancel': button},
            follow_redirects=True
        )

    for msg in good_msg:
        assert msg in response.data

    for msg in bad_msg:
        assert msg not in response.data

@pytest.mark.parametrize(('button','good_msg','bad_msg'),(
        ('cancel', [b'Home Page', b'Welcome John'], [b'Error(s)', b'Quote Form']),
        ('confirm', [b'Quote Order Confirmation', b'return to home page', b'Success!'], [b'Error(s)', b'Quote Form', b'Home Page', b'Welcome John']),
))
def test_validate_quote_confirm(auth, client, button, good_msg, bad_msg):
    auth.login()
    assert client.get('/request/admin@mail.com/quote').status_code == 200
    response = client.post(
        '/request/admin@mail.com/quote', data={'gal': '500', 'deliv_date': '2020-07-31',
            'deliv_time': '05:00','proceed': 'Proceed'},
        follow_redirects=True
    )

    if button == 'confirm':
        response = client.post(
            '/request/admin@mail.com/quote-confirm',
            data={'confirm': button},
            follow_redirects=True
        )
    else:
        response = client.post(
            '/request/admin@mail.com/quote-confirm',
            data={'cancel': button},
            follow_redirects=True
        )

    for msg in good_msg:
        assert msg in response.data

    for msg in bad_msg:
        assert msg not in response.data