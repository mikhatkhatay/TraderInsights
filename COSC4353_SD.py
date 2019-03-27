# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 09:59:59 2019

@author: M. Ibrahim
"""

from flask import Flask, render_template, flash, request, url_for, redirect, session, abort
import os, datetime, time
from sqlalchemy.orm import sessionmaker
from tabledef import *
from flask_wtf import FlaskForm
from wtforms import Form, PasswordField, SubmitField, BooleanField, TextField, TextAreaField, validators, StringField, IntegerField, DateTimeField, DateField, TimeField
from wtforms.fields.html5 import EmailField

engine = create_engine("sqlite:///tutorial.db", echo=True)
 
# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config["SECRET_KEY"] = "doesitevenmatter"

max_count = 5
counter = 0


class LoginForm(FlaskForm):
    email = EmailField("Email:", validators=[validators.Email(message="Please provide a valid email"), validators.InputRequired(message="Email is required")])
    password = PasswordField("Password:", validators=[validators.InputRequired(message="Password is required"), validators.Length(min=3, max=35,message="Password must be between 3 and 35 characters")])

class SignUp(FlaskForm):
    email = EmailField("Email:", validators=[validators.Email(message="Please provide a valid email"), validators.DataRequired(message="Email is required")])
    password = PasswordField("Password:", validators=[validators.InputRequired(message="Password is required"), validators.Length(min=3, max=35, message="Password must be between 3 and 35 characters")])
    passconf = PasswordField("Repeat Password:", validators=[validators.InputRequired(message="Repeat password is required"), validators.EqualTo("password", message="Passwords must match")])
    tos = BooleanField("I accept the Terms of Service",validators=[validators.DataRequired(message="Please accept Terms of Service")])

def zip_check(form, field):
    if len(field.data)!=5 or not field.data.isdigit:
        raise validators.ValidationError("Zipcode must be 5 digits")

class RegProfile(FlaskForm):
    first = TextField("First Name:", validators=[validators.InputRequired("Please input First Name")])
    last = TextField("Last Name:", validators=[validators.InputRequired("Please input Last Name")])
    company = TextField("Company Name:", validators=[validators.InputRequired("Please input Company")])
    addr = TextField("Street Address:", validators=[validators.InputRequired("Please input company's Street Address")])
    city = TextField("City:", validators=[validators.InputRequired("Please input City")])
    state = TextField("State (XX):", validators=[validators.InputRequired("Please input 2-letter State abbreviation"), validators.Length(min=2,max=2,message="State abbreviation must be 2 letters")])
    zipcode = TextField("Zipcode (#####):", validators=[validators.InputRequired("Please input 5-digit Zipcode"), zip_check])

class ProfileChange(FlaskForm):
    first = TextField("First Name:", validators=[validators.InputRequired("Please input First Name")])
    last = TextField("Last Name:", validators=[validators.InputRequired("Please input Last Name")])
    company = TextField("Company Name:", validators=[validators.InputRequired("Please input Company")])
    addr = TextField("Street Address:", validators=[validators.InputRequired("Please input company's Street Address")])
    city = TextField("City:", validators=[validators.InputRequired("Please input City")])
    state = TextField("State (XX):", validators=[validators.InputRequired("Please input 2-letter State abbreviation"), validators.Length(min=2,max=2,message="State abbreviation must be 2 letters")])
    zipcode = TextField("Zipcode (#####):", validators=[validators.InputRequired("Please input 5-digit Zipcode"), zip_check])
    newpass = PasswordField("New Password:", validators=[validators.Optional(),validators.Length(min=3,max=35,message="New password must be between 3 and 35 characters")])
    currpass = PasswordField("Current Password:", validators=[validators.InputRequired(message="Please enter password to update profile or change password")])
    confpass = PasswordField("Confirm Password:", validators=[validators.EqualTo("currpass", message="Passwords must match")])

class QuoteForm(FlaskForm):
    gal = IntegerField("Number of Gallons:", validators=[validators.InputRequired(message="Fuel amount is required"),validators.NumberRange(min=1,message="Please enter a valid amount (greater than zero)")])
    deliv_date = DateField("Delivery Date:", validators=[validators.InputRequired(message="Delivery date is required")])
    deliv_time = TimeField("Delivery Time:", validators=[validators.InputRequired(message="Delivery time is required")])
    
@app.route("/", methods=["GET", "POST"])
def login():
    global counter
    form = LoginForm(request.form)
    
    if request.method == "POST":
        if "login" in request.form:
            password=request.form["password"]
            email=request.form["email"]
            if form.validate() or (len(form.errors.items()) == 1 and "csrf_token" in form.errors):
                Session = sessionmaker(bind=engine)
                s = Session()
                query = s.query(User).filter(User.username.in_([email]) )
                result = query.first()
                if result:
                    query = s.query(User).filter(User.username.in_([email]), User.password.in_([password]) )
                    result = query.first()
                    """OPTIONAL: log login attempt to database"""
                    if result:
                        """update counter in database"""
                        counter = 0
                        return redirect(url_for("userPage", name = email))
                    else:
                        """update counter in database"""
                        counter += 1
                        if counter == max_count:
                            flash("Error: Email or password is incorrect. Account is locked. Contact Customer Support for assistance.")
                        else:
                            flash("Error: Email or password is incorrect. Try again...")
                else:
                    flash("Error: Email or password is incorrect. Try again...")
            else:
                if len(form.errors.items()) > 1:
                    out = "Error(s) encountered!"
                    for item, error in form.errors.items():
                        if item != "csrf_token":
                            out += "<br/>"+error[0]
                    flash(out)
        if "register" in request.form:
            return redirect(url_for("signup"))
    return render_template("login.html", form=form)

@app.route("/register", methods=["GET", "POST"])
def signup():
    form = SignUp(request.form)
    
    if request.method == "POST":
        if "cancel" in request.form:
            return redirect(url_for("login"))
        if "register" in request.form:
            email=request.form["email"]
            password=request.form["password"]
            if form.validate() or (len(form.errors.items()) == 1 and "csrf_token" in form.errors):
                Session = sessionmaker(bind=engine)
                s = Session()
                query = s.query(User).filter(User.username.in_([email]) )
                result = query.first()
                if result:
                    flash("Error: "+email+" already exists.")
                else:
                    return redirect(url_for("initProfile", email=email, password=password))
            else:
                if len(form.errors.items()) > 1:
                    out = "Error(s) encountered!"
                    for item, error in form.errors.items():
                        if item != "csrf_token":
                            out += "<br/>"+error[0]
                    flash(out)
            
    return render_template("register.html", form=form)

@app.route("/<email>&<password>/new_user_profile", methods=["GET","POST"])
def initProfile(email, password):
    form = RegProfile(request.form)
    if request.method == "POST":
        if "cancel" in request.form:
            return redirect(url_for("login"))
        if "finish" in request.form:
            first=request.form["first"]
            last=request.form["last"]
            company=request.form["company"]
            addr=request.form["addr"]
            city=request.form["city"]
            state=request.form["state"]
            zipcode=request.form["zipcode"]
    
            if form.validate() or (len(form.errors.items()) == 1 and "csrf_token" in form.errors):
                """Send to database to insert"""
                return redirect(url_for("complete"))
            else:
                if len(form.errors.items()) > 1:
                    out = "Error(s) encountered!"
                    for item, error in form.errors.items():
                        if item != "csrf_token":
                            out += "<br/>"+error[0]
                    flash(out)
    return render_template("initProfile.html", **locals())

@app.route("/complete", methods=["GET"])
def complete():
    return render_template("complete.html")

@app.route("/<name>/profile", methods=["GET","POST"])
def manageProfile(name):
    print(name)
    """TODO: Pre-populate form fields"""
    form = ProfileChange(request.form)
    """query user profile information to populate fields"""
#    Session = sessionmaker(bind=engine)
#    s = Session()
#    query = s.query(User).filter(User.username.in_([name]) )
    [first, last, company, addr, city, state, zipcode] = ["John","Doe","John Doe Ltd.","1234 Main St.","Houston","TX","77002"]
    if request.method == "GET":
        return render_template("manageProfile.html",**locals())
    if request.method == "POST":
        button = userButtons(request.form,name)
        if button is not None:
            return button
        
        if "cancel" in request.form:
            return redirect(url_for("userPage", name=name))
        if "submit" in request.form:
            print(request.form)
            first=request.form["first"]
            last=request.form["last"]
            company=request.form["company"]
            addr=request.form["addr"]
            city=request.form["city"]
            state=request.form["state"]
            zipcode=request.form["zipcode"]
            newpass = request.form["newpass"]
            currpass=request.form["currpass"]
            
            if form.validate() or (len(form.errors.items()) == 1 and "csrf_token" in form.errors):
                Session = sessionmaker(bind=engine)
                s = Session()
                query = s.query(User).filter(User.username.in_([name]), User.password.in_([currpass]) )
                result = query.first()
                
                """confirm password with database"""
                if result:
                    print(newpass)
                    if newpass:
                        """Send to database to update with new password"""
                        flash("Information updated! New password stored!")
                    else:
                        """Send to database to update WITHOUT new password"""
                        flash("Information updated!")
                    return render_template("manageProfile.html",form=form,name=name)
                else:
                    flash("Error: Incorrect password")
                    return render_template("manageProfile.html",form=form,name=name)
            else:
                if len(form.errors.items()) > 1:
                    out = "Error(s) encountered!"
                    for item, error in form.errors.items():
                        if item != "csrf_token":
                            out += "<br/>"+error[0]
                    flash(out)
    return render_template("manageProfile.html", **locals())

@app.route("/user/<name>/quote", methods=["GET","POST"])
def getQuote(name):
    form=QuoteForm(request.form)
    """query user profile information to display constants"""
#    Session = sessionmaker(bind=engine)
#    s = Session()
#    query = s.query(User).filter(User.username.in_([name]))
#    userdict = query.__dict__
#    first = userdict["first"]
#    last = userdict["last"]
#    company = userdict["company"]
#    addr = userdict["addr"]
#    city = userdict["city"]
#    state = userdict["state"]
#    zipcode = userdict["zipcode"]
    userdict=("john", "doe", "john doe ltd.", "1234 Main Street", "Houston","TX","77002")
    first = userdict[0]
    last = userdict[1]
    company = userdict[2]
    addr = userdict[3]
    city = userdict[4]
    state = userdict[5]
    zipcode = userdict[6]
    if request.method == "POST":
        button = userButtons(request.form,name)
        if button is not None:
            return button
        
        if "cancel" in request.form:
            return redirect(url_for("userPage", name=name))
        if "proceed" in request.form:
            gal = request.form["gal"]
            deliv_date = request.form["deliv_date"]
            deliv_time = request.form["deliv_time"]
            if form.validate() or (len(form.errors.items()) == 1 and "csrf_token" in form.errors):
                return redirect(url_for("quoteConf", name=name, gallons=gal, deliv_date=deliv_date, deliv_time=deliv_time))
            else:
                if len(form.errors.items()) > 1:
                    out = "Error(s) encountered!"
                    for item, error in form.errors.items():
                        if item != "csrf_token":
                            out += "<br/>"+error[0]
                    flash(out)
    
    return render_template("request.html", **locals())

@app.route("/user/<name>/quote-confirm&<gallons>&<deliv_date>&<deliv_time>", methods=["GET","POST"])
def quoteConf(name, gallons, deliv_date, deliv_time):
    form = request.form
    """query user information to display constants"""
#    Session = sessionmaker(bind=engine)
#    s = Session()
#    query = s.query(User).filter(User.username.in_([name]))
#    userdict = query.__dict__
#    first = userdict["first"]
#    last = userdict["last"]
#    company = userdict["company"]
#    addr = userdict["addr"]
#    city = userdict["city"]
#    state = userdict["state"]
#    zipcode = userdict["zipcode"]
    userdict=("john", "doe", "john doe ltd.", "1234 Main Street", "Houston","TX","77002")
    first = userdict[0]
    last = userdict[1]
    company = userdict[2]
    addr = userdict[3]
    city = userdict[4]
    state = userdict[5]
    zipcode = userdict[6]
    
    if request.method == "POST":
        button = userButtons(request.form,name)
        if button is not None:
            return button
        
        if "cancel" in request.form:
            return redirect(url_for("userPage", name=name))
        if "confirm" in request.form:
            return redirect(url_for("receipt", name=name, gallons=gallons, deliv_date=deliv_date, deliv_time=deliv_time))
    return render_template("requestConf.html", **locals())

@app.route("/user/<name>/order-confirmation&<gallons>&<deliv_date>&<deliv_time>", methods=["GET","POST"])
def receipt(name, gallons, deliv_date, deliv_time):
    form = request.form
    
    flash("Your order has been placed")
    return render_template("receipt.html", **locals())

def getUserQuotes(name):
    orders = []
    Session = sessionmaker(bind=engine)
    s = Session()
    dictlist = [u.__dict__ for u in s.query(Quote).filter(User.username.in_([name]))]
    for item in dictlist:
        orders.append(item["date"],item["first"],item["last"],item["addr"],item["city"],item["state"],item["zipcode"],item["gal"],item["price"],item["trans"],item["disc_cat"],item["disc_perc"],item["total"])
    return orders

@app.route("/user/<name>/history", methods=["GET","POST"])
def getHistory(name):
    form = request.form
    
    """Send request to database to find all requests made by user"""
    """Store reply into variable "orders" """
    """Create dummy data for test"""
    orders = [(datetime.datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %H:%M:%S"),"john", "doe", "john doe ltd.", "1234 Main Street", "Houston","TX","77002",15,3.199,format(0,".2f"),"10-20","2%",format(15*3.199*(1-int("2%"[:-1])/100),".2f"))]
#    orders = getUserQuotes(name)
    
    if request.method == "POST":
        button = userButtons(request.form,name)
        if button is not None:
            return button
    
    return render_template("history.html", form=form, name=name, orders=orders)

@app.route("/user/<name>", methods=["GET","POST"])
def userPage(name):
    form = request.form
    """query user's first name to display customized, friendly welcome message"""
#    Session = sessionmaker(bind=engine)
#    s = Session()
#    query = s.query(User).filter(User.username.in_([name]))
#    userdict = query.__dict__
    first = "John"
    if request.method == "POST":
        button = userButtons(request.form,name)
        if button is not None:
            return button
    return render_template("userPage.html", **locals())

def userButtons(FlaskForm, name):
    buttons = ["logout","profile","request","history"]
    links = [url_for("login"),url_for("manageProfile",name=name),url_for("getQuote",name=name),url_for("getHistory",name=name)]
    for val in range(len(buttons)):
        if buttons[val] in request.form:
            if buttons[val] == "logout":
                """update field in database"""
            return redirect(links[val])
    return None

if __name__ == "__main__":
    app.run()