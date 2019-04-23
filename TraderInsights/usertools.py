# -*- coding: utf-8 -*-
"""
Team: Fund_Khatkhatay_Zaidi
File Description: All methods and classes relating to user tools (profile and
                    quote history)
"""

from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash
from TraderInsights.auth import login_required, zip_check
from TraderInsights.db import get_db

from flask_wtf import FlaskForm
from wtforms import PasswordField, validators, StringField, SelectField
from .userButtons import userButtons
from .auth import states

bp = Blueprint('ut', __name__, url_prefix='/tools')

class ProfileChange(FlaskForm):
    fullname = StringField("Full Name:", validators=[validators.InputRequired("Please input Full Name")])
    company = StringField("Company Name:", validators=[validators.InputRequired("Please input Company")])
    addr1 = StringField("Street Address 1:", validators=[validators.InputRequired("Please input company's Street Address")])
    addr2 = StringField("Street Address 2:", validators=[validators.Optional()])
    city = StringField("City:", validators=[validators.InputRequired("Please input City")])
    state = SelectField("State:",choices=states())#("State (XX):", validators=[validators.InputRequired("Please input 2-letter State abbreviation"), validators.Length(min=2,max=2,message="State abbreviation must be 2 letters")])
    zipcode = StringField("Zipcode:", validators=[validators.InputRequired("Please input 5- or 9-digit Zipcode"), zip_check])
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
            (db, cur) = get_db()
            
            if form.validate() or (len(form.errors.items()) == 1 and "csrf_token" in form.errors):
                cur.execute(
                    "SELECT password FROM users WHERE email = '"+email+"'"
                )
                pw = cur.fetchone()
                # print("\n\n")
                # print([pw[x] for x in range(len(pw))])
                currpass=request.form["currpass"]
                """confirm password with database"""
                if check_password_hash(pw[0],currpass):
                    session['fullname']=fullname=request.form["fullname"]
                    session['company']=company=request.form["company"]
                    session['addr1']=addr1=request.form["addr1"]
                    session['addr2']=addr2=request.form["addr2"]
                    session['city']=city=request.form["city"]
                    session['state']=state=request.form["state"]
                    session['zipcode']=zipcode=request.form["zipcode"]
                    session['newpass']=newpass=request.form["newpass"]
                    if newpass:
                        cur.execute(
                                "UPDATE users SET password = '"+newpass+"',full_name = '"+fullname+"',company_name = '"+company+"',addr1 = '"+
                                addr1+"',addr2 = '"+addr2+"',city = '"+city+"',state = '"+state+"', zipcode = '"+zipcode+"' WHERE email = '"+email+"'"
                        )
                        db.commit()
                        session['flash'] = "Information updated! New password stored!"
                        flash(session['flash'],'success')
                    else:
                        cur.execute(
                            "UPDATE users SET full_name = '"+fullname+"',company_name = '"+company+"',addr1 = '"+
                            addr1+"',addr2 = '"+addr2+"',city = '"+city+"',state = '"+state+"', zipcode = '"+zipcode+"' WHERE email = '"+email+"'"
                        )
                        db.commit()
                        session['flash'] = "Information updated!"
                        flash(session['flash'],'success')
                else:
                    session['flash'] = "Incorrect password"
                    flash(session['flash'],'error')
            else:
                if (len(form.errors.items())==1 and 'csrf_token' not in form.errors) or len(form.errors.items()) > 1:
                    out = "Error(s) encountered!"
                    for item, error in form.errors.items():
                        if item != "csrf_token":
                            out += "<br/>"+error[0]
                    session['flash'] = out
                    flash(session['flash'],'error')
    return render_template("tools/manageProfile.html", form=form,session=session)

def getUserQuotes():
    (db, cur) = get_db()
    cur.execute(
        "SELECT * FROM history WHERE email = '"+session['email']+"'"
    )
    orders = cur.fetchall()
    x = [10, 2, 3, 4, 5, 6, 7, 8, 9, 14, 12, 13, 16, 11, 17]
    # print(len(orders))
    # for order in orders:
    #     print(order)
        # print([order[i] for i in x])
        # print("")
    return [[order[i] for i in x] for order in orders]

@bp.route("/<email>/history", methods=["GET","POST"])
@login_required
def getHistory(email):
    form = FlaskForm
    
    orders = getUserQuotes()
    # print(orders)
    if request.method == "POST":
        button = userButtons(request.form)
        if button is not None:
            return button
    
    return render_template("tools/history.html", form=form, session=session, orders=orders)