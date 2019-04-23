# -*- coding: utf-8 -*-
"""
Created on Sun Mar 24 17:47:57 2019

@author: M. Ibrahim
"""

from TraderInsights.db import get_db

def test_get_close_db(app):
    with app.app_context():
        db = get_db()
        assert db==get_db()

        db[0].close()
        assert db[0].closed

def test_init_db_command(runner, monkeypatch):
    class Recorder(object):
        called = False
    
    def fake_init_db():
        Recorder.called = True
    
    monkeypatch.setattr('TraderInsights.db.init_db', fake_init_db)
    result = runner.invoke(args=['init-db'])
    assert 'Initialized' in result.output
    assert Recorder.called