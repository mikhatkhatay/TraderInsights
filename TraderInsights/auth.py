# -*- coding: utf-8 -*-
"""
Team: Fund_Khatkhatay_Zaidi
File Description: All methods and classes relating to user authorization
"""

import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from TraderInsights.db import get_db

from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, validators, StringField, SelectField
from wtforms.fields.html5 import EmailField
import socket

bp = Blueprint('auth', __name__, url_prefix='/auth')
max_attempt = 5

class SignUp(FlaskForm):
    email = EmailField("Email:", validators=[validators.Email(message="Please provide a valid email"), validators.InputRequired(message="Email is required")])
    password = PasswordField("Password:", validators=[validators.DataRequired(message="Password is required"), validators.Length(min=3, max=35, message="Password must be between 3 and 35 characters")])
    passconf = PasswordField("Repeat Password:", validators=[validators.InputRequired(message="Repeat password is required"), validators.EqualTo("password", message="Passwords must match")])
    tos = BooleanField("I accept the Terms of Service",validators=[validators.DataRequired(message="Please accept Terms of Service")])

@bp.route('/newuser', methods=('GET', 'POST'))
def signup():
    form = SignUp(request.form)
    if request.method == "POST":
        # print(form.errors)
        if "cancel" in request.form:
            return redirect(url_for("auth.login"))
        if "register" in request.form:
            email=request.form["email"]
            password=request.form["password"]
            (db, cur) = get_db()
            error = None
            
            if form.validate() or (len(form.errors.items()) == 1 and "csrf_token" in form.errors):
                cur.execute(
                    "SELECT email FROM users WHERE email = '" + email + "'"
                )
                row = cur.fetchone()
                # print("does "+email+" exist?", row)
                if row is not None:
                    session['flash'] = "Error: "+email+" already exists."
                    flash(session['flash'], 'error')
                else:
                    session.clear()
                    session['email'] = email
                    session['password'] = generate_password_hash(password)
                    return redirect(url_for("auth.initProfile"))
            else:
                if (len(form.errors.items()) == 1 and "csrf_token" not in form.errors) or len(form.errors.items()) > 1:
                    out = "Error(s) encountered!"
                    for item, error in form.errors.items():
                        if item != "csrf_token":
                            out += "<br/>"+error[0]
                    session['flash'] = out
                    flash(session['flash'],'error')
    return render_template("auth/register.html", form=form)

def zip_check(form, field):
    if (len(field.data)!=5 and len(field.data)!=9) or not field.data.isdigit:
        raise validators.ValidationError("Please input 5- or 9-digit Zipcode")

def states():
    return [("AL","AL"),("AK","AK"),("AZ","AZ"),("AR","AR"),("CA","CA"),("CO","CO"),("CT","CT"),("DE","DE"),("FL","FL"),
            ("GA", "GA"),("HI","HI"),("ID","ID"),("IL","IL"),("IN","IN"),("IA","IA"),("KS","KS"),("KY","KY"),("LA","LA"),
            ("ME", "ME"),("MD","MD"),("MA","MA"),("MI","MI"),("MN","MN"),("MS","MS"),("MO","MO"),("MT","MT"),("NE","NE"),
            ("NV", "NV"),("NH","NH"),("NJ","NJ"),("NM","NM"),("NY","NY"),("NC","NC"),("ND","ND"),("OH","OH"),("OK","OK"),
            ("OR", "OR"),("PA","PA"),("RI","RI"),("SC","SC"),("SD","SD"),("TN","TN"),("TX","TX"),("UT","UT"),("VT","VT"),
            ("VA", "VA"),("WA","WA"),("WV","WV"),("WI","WI"),("WY","WY")]

class RegProfile(FlaskForm):
    fullname = StringField("Full Name:", validators=[validators.InputRequired("Please input Full Name")])
    company = StringField("Company Name:", validators=[validators.InputRequired("Please input Company")])
    addr1 = StringField("Street Address 1:", validators=[validators.InputRequired("Please input company's Street Address")])
    addr2 = StringField("Street Address 2:", validators=[validators.Optional()])
    city = StringField("City:", validators=[validators.InputRequired("Please input City")])
    state = SelectField("State:", choices=states())#StringField("State:", validators=[validators.InputRequired("Please input 2-letter State abbreviation"), validators.Length(min=2,max=2,message="State abbreviation must be 2 letters")])
    zipcode = StringField("Zipcode:", validators=[validators.InputRequired("Please input 5- or 9-digit Zipcode"), zip_check])

@bp.route('/newprofile', methods=('GET', 'POST'))
def initProfile():
    # print(request.form)
    form = RegProfile(request.form)
    (db, cur) = get_db()
    if request.method == "POST":
        if "cancel" in request.form:
            return redirect(url_for("auth.login"))
        if "finish" in request.form:
            fullname=request.form["fullname"]
            company=request.form["company"]
            addr1=request.form["addr1"]
            addr2=request.form["addr2"]
            city=request.form["city"]
            state=request.form["state"]
            zipcode=request.form["zipcode"]
    
            if form.validate() or (len(form.errors.items()) == 1 and "csrf_token" in form.errors):
                cur.execute(
                    "INSERT INTO users (email, password, full_name, company_name, addr1, addr2, city, state, zipcode) "+
                    "VALUES ('"+session['email']+"', '"+session['password']+"', '"+fullname+"', '"+company+"', '"
                    +addr1+"', '"+addr2+"', '"+city+"', '"+state.upper()+"', '"+zipcode+"')",
                )
                db.commit()
                session.clear()
                return redirect(url_for("auth.complete"))
            else:
                if (len(form.errors.items()) == 1 and "csrf_token" not in form.errors) or len(form.errors.items()) > 1:
                    out = "Error(s) encountered!"
                    for item, error in form.errors.items():
                        if item != "csrf_token":
                            out += "<br/>"+error[0]
                    session['flash'] = out
                    flash(session['flash'],'error')
    return render_template("auth/initProfile.html", form=form)

@bp.route('/complete', methods=('GET', 'POST'))
def complete():
    return render_template("auth/complete.html")

class LoginForm(FlaskForm):
    email = EmailField("Email:", validators=[validators.Email(message="Please provide a valid email"), validators.InputRequired(message="Email is required")])
    password = PasswordField("Password:", validators=[validators.InputRequired(message="Password is required"), validators.Length(min=3, max=35,message="Password must be between 3 and 35 characters")])

def insertToDB(email, password, reason, ip):
    (db, cur) = get_db()
    cur.execute(
        "INSERT INTO attempts (email, password, result, ip_address) VALUES ('"+email+"','"+generate_password_hash(password)+"',"+str(reason)+",'"+ip+"')"
    )
    db.commit()

@bp.route("/login", methods=("GET", "POST"))
def login():
    form = LoginForm(request.form)
    # print(form.errors)
    # print(generate_password_hash('password'))
    if request.method == "POST":
        if "register" in request.form:
            return redirect(url_for("auth.signup"))
        if "login" in request.form:
            # print(request.form)
            password=request.form["password"]
            email=request.form["email"]
            (db, cur) = get_db()
            
            if form.validate() or (len(form.errors.items()) == 1 and "csrf_token" in form.errors):
                ip = socket.gethostbyname(socket.gethostname())
                # print("flag user check")
                cur.execute(
                    "SELECT * FROM users WHERE email = '"+email+"'"
                )
                user = cur.fetchone()
                # print(user)
                if user is None:
                    insertToDB(email, password, 0, ip)
                    session['flash'] = "Error: Email or password is incorrect. Try again..."
                    flash(session['flash'],'error')
                elif not check_password_hash(user[1], password):
                    if user[9] < max_attempt-1:
                        insertToDB(email, password, 1, ip)
                        cur.execute(
                            "UPDATE users SET number_of_attempts = "+str(user[9]+1)+" WHERE email = '"+email+"'"
                        )
                        db.commit()
                        session['flash'] = "Error: Email or password is incorrect. Try again..."
                        flash(session['flash'],'error')
                    else:
                        insertToDB(email, password, 2, ip)
                        cur.execute(
                            "UPDATE users SET number_of_attempts = "+str(max_attempt)+" WHERE email = '"+email+"'"
                        )
                        db.commit()
                        session['flash'] = "Error: Email or password is incorrect. Account is locked. Contact Customer Support for assistance."
                        flash(session['flash'],'error')
                else:
                    if user[9] == max_attempt:
                        insertToDB(email, password, 2, ip)
                        session['flash'] = "Error: Account is locked. Contact Customer Support for assistance."
                        flash(session['flash'],'error')
                    else:
                        session['flash'] = ''
                        insertToDB(email, password, 3, ip)
                        cur.execute(
                            "UPDATE users SET number_of_attempts = 0, logged_in = 1 WHERE email = '"+email+"'"
                        )
                        db.commit()
                        session.clear()
                        session['email'] = email
                        [session['fullname'],
                         session['company'],
                         session['addr1'],
                         session['addr2'],
                         session['city'],
                         session['state'],
                         session['zipcode']] = [user[x] for x in range(2,len(user)-2)]
                        
                        return redirect(url_for("userPage", email=email))
            else:
                if (len(form.errors.items()) == 1 and "csrf_token" not in form.errors) or len(form.errors.items()) > 1:
                    out = "Error(s) encountered!"
                    for item, error in form.errors.items():
                        if item != "csrf_token":
                            out += "<br/>"+error[0]
                    session['flash'] =  out
                    flash(session['flash'],'error')
            # print(form.errors)
    return render_template("auth/login.html", form=form)

@bp.before_app_request
def load_logged_in_user():
    email = session.get('email')
    
    if email is None:
        g.user = None
    else:
        (db, cur) = get_db()
        cur.execute(
            "SELECT * FROM users WHERE email = '"+email+"'"
        )
        g.user = cur.fetchone()

@bp.route('/logout')
def logout():
    (db, cur) = get_db()
    cur.execute(
        "UPDATE users SET logged_in = 0 WHERE email = '"+session['email']+"'"
    )
    db.commit()
    db.close()
    session.clear()
    # print(session)
    return redirect(url_for('welcome'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)
    
    return wrapped_view