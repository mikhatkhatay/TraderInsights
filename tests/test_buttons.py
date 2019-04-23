import pytest

@pytest.mark.parametrize(('button', 'good_msg', 'bad_msg'),(
        ("logout", [b'Welcome to Trader Insights', b'To log in', b'To create an account'], [b'Profile Management', b'Order History', b'Quote Form', b'\'s Home Page']),
        ("profile", [b'Profile Management', b'Full Name', b'State'], [b'Welcome to Trader Insights', b'Order History', b'Quote Form', b'\'s Home Page']),
        ("request", [b'Quote Form', b'Number of Gallons', b'Delivery Date'], [b'Welcome to Trader Insights', b'Order History', b'Profile Management', b'\'s Home Page']),
        ("history", [b'Order History'], [b'Welcome to Trader Insights', b'Quote Form', b'Profile Management', b'\'s Home Page']),
))
def test_userButtons(auth, client, app, button, good_msg, bad_msg):
    auth.login()
    response = client.get('/admin@mail.com')
    assert response.status_code == 200

    response = client.post('/admin@mail.com', data={button: button}, follow_redirects = True)
    assert response.status_code == 200

    for msg in good_msg:
        assert msg in response.data

    for msg in bad_msg:
        assert msg not in response.data