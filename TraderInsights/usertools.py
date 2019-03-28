# -*- coding: utf-8 -*-
"""
Team: Fund_Khatkhatay_Zaidi
File Description: All methods and classes relating to user tools (profile and
                    quote history)
"""

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort
from werkzeug.security import check_password_hash, generate_password_hash
from TraderInsights.auth import login_required, zip_check
from TraderInsights.db import get_db

from flask import Flask, abort
import os, datetime, time
from flask_wtf import FlaskForm
from wtforms import Form, PasswordField, SubmitField, BooleanField, TextField, TextAreaField, validators, StringField, IntegerField, DateTimeField, DateField, TimeField
from wtforms.fields.html5 import EmailField
import socket
from .userButtons import userButtons

bp = Blueprint('ut', __name__, url_prefix='/tools')

class ProfileChange(FlaskForm):
    first = TextField("First Name:", validators=[validators.InputRequired("Please input First Name")])
    last = TextField("Last Name:", validators=[validators.InputRequired("Please input Last Name")])
    company = TextField("Company Name:", validators=[validators.InputRequired("Please input Company")])
    addr = TextField("Street Address:", validators=[validators.InputRequired("Please input company's Street Address")])
    city = TextField("City:", validators=[validators.InputRequired("Please input City")])
    state = TextField("State (XX):", validators=[validators.InputRequired("Please input 2-letter State abbreviation"), validators.Length(min=2,max=2,message="State abbreviation must be 2 letters")])
    zipcode = TextField("Zipcode:", validators=[validators.InputRequired("Please input 5-digit Zipcode"), zip_check])
    newpass = PasswordField("New Password:", validators=[validators.Optional(),validators.Length(min=3,max=35,message="New password must be between 3 and 35 characters")])
    confpass = PasswordField("Confirm Password:", validators=[validators.EqualTo("newpass", message="Passwords must match")])
    currpass = PasswordField("Current Password:", validators=[validators.InputRequired(message="Please enter password to update profile or change password")])

@bp.route("/<email>/profile", methods=["GET","POST"])
@login_required
def manageProfile(email):
    form = ProfileChange()
    if request.method == "POST":
        button = userButtons(request.form)
        if button is not None:
            return button
        
        if "cancel" in request.form:
            return redirect(url_for("userPage", email=email))
        if "submit" in request.form:
            db = get_db()
            
            if form.validate() or (len(form.errors.items()) == 1 and "csrf_token" in form.errors):
                pw = db.execute(
                    'SELECT password FROM users WHERE email = ?', (email,)
                ).fetchone()
                print("\n\n")
                print([pw[x] for x in range(len(pw))])
                currpass=request.form["currpass"]
                """confirm password with database"""
                if check_password_hash(pw[0],currpass):
                    session['first']=first=request.form["first"]
                    session['last']=last=request.form["last"]
                    session['company']=company=request.form["company"]
                    session['addr']=addr=request.form["addr"]
                    session['city']=city=request.form["city"]
                    session['state']=state=request.form["state"]
                    session['zipcode']=zipcode=request.form["zipcode"]
                    session['newpass']=newpass=request.form["newpass"]
                    if newpass:
                        db.execute(
                            'UPDATE users SET password = ?,\
                            first = ?,\
                            last = ?,\
                            company = ?,\
                            addr = ?,\
                            city = ?,\
                            state = ?,\
                            zipcode = ? WHERE email = ?',
                            (newpass, first, last, company, addr, city, state, zipcode, email)
                        )
                        db.commit()
                        session['flash'] = "Information updated! New password stored!"
                        flash(session['flash'],'success')
                    else:
                        db.execute(
                            'UPDATE users SET first = ?,\
                            last = ?,\
                            company = ?,\
                            addr = ?,\
                            city = ?,\
                            state = ?,\
                            zipcode = ? WHERE email = ?',
                            (first, last, company, addr, city, state, zipcode, email)
                        )
                        db.commit()
                        session['flash'] = "Information updated!"
                        flash(session['flash'],'success')
                else:
                    session['flash'] = "Incorrect password"
                    flash(session['flash'],'error')
            else:
                if len(form.errors.items()) > 1:
                    out = "Error(s) encountered!"
                    for item, error in form.errors.items():
                        if item != "csrf_token":
                            out += "<br/>"+error[0]
                    session['flash'] = out
                    flash(session['flash'],'error')
    return render_template("tools/manageProfile.html", form=form,session=session)

def getUserQuotes():
    db = get_db()
    orders = db.execute(
        'SELECT requests.deliv_date, users.first,\
        users.last, users.company, users.addr,\
        users.city, users.state, users.zipcode,\
        requests.gallons, requests.price,\
        requests.transport, requests.discLvl,\
        requests.percDisc, requests.compPrice,\
        requests.total  FROM users INNER JOIN\
        requests ON users.email = requests.email\
        WHERE requests.email = ?',
        (session['email'],)
    ).fetchall()
    
    return [(order[i] for i in range(len(order))) for order in orders]

@bp.route("/<email>/history", methods=["GET","POST"])
@login_required
def getHistory(email):
    form = FlaskForm
    
    orders = getUserQuotes()
    print(orders)
    if request.method == "POST":
        button = userButtons(request.form)
        if button is not None:
            return button
    
    return render_template("tools/history.html", form=form, session=session, orders=orders)