# -*- coding: utf-8 -*-
"""
Team: Fund_Khatkhatay_Zaidi
File Description: Method used across multiple files
"""

from flask import url_for, redirect, session
from flask_wtf import FlaskForm

def userButtons(form=FlaskForm):
    buttons = ["logout","profile","request","history"]
    links = [url_for("auth.logout"),url_for("ut.manageProfile", email=session['email']),url_for("req.getQuote",email=session['email']),url_for("ut.getHistory", email=session['email'])]
    for val in range(len(buttons)):
        if buttons[val] in form:
            return redirect(links[val])
    return None