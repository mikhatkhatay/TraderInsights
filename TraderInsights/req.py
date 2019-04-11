# -*- coding: utf-8 -*-
"""
Team: Fund_Khatkhatay_Zaidi
File Description: All methods and classes relating to quote request and confirmation
"""

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort
from werkzeug.security import check_password_hash, generate_password_hash
from TraderInsights.auth import login_required
from TraderInsights.db import get_db

from flask import Flask, abort
import os, datetime, time
from flask_wtf import FlaskForm
from wtforms import Form, PasswordField, SubmitField, BooleanField, TextField, TextAreaField, validators, StringField, IntegerField, DateTimeField, DateField, TimeField
from wtforms.fields.html5 import EmailField
import datetime
import socket
from .userButtons import userButtons

import random

bp = Blueprint('req', __name__, url_prefix='/request')

def date_check(form, field):
    good_date = datetime.date.today()
    min_date = datetime.date.today()+datetime.timedelta(days=14)
    if field.data < good_date:
        raise validators.ValidationError("Cannot deliver in the past")
    if field.data < min_date:
        raise validators.ValidationError("Please allow at least 10 business days for delivery. Earliest date is "+str(min_date))


class QuoteForm(FlaskForm):
    gal = IntegerField("Number of Gallons:", validators=[validators.InputRequired(message="Fuel amount is required"),validators.NumberRange(min=1,message="Please enter a valid amount (greater than zero)")])
    deliv_date = DateField("Delivery Date:", validators=[validators.InputRequired(message="Delivery date is required"), date_check])
    deliv_time = TimeField("Delivery Time:", validators=[validators.InputRequired(message="Delivery time is required")])

@bp.route('/<email>/quote', methods=('GET','POST'))
@login_required
def getQuote(email):
    form=QuoteForm(request.form)
    print(form)
    if request.method == "POST":
        button = userButtons(request.form)
        if button is not None:
            return button
        
        if "cancel" in request.form:
            return redirect(url_for("userPage", email=email))
        if "proceed" in request.form:
            print(request.form['deliv_date'], request.form['deliv_time'])
            if form.validate() or (len(form.errors.items()) == 1 and "csrf_token" in form.errors):
                print(form)
                session['gal'] = request.form["gal"]
                session['deliv_date'] = request.form["deliv_date"]
                session['deliv_time'] = request.form["deliv_time"]
                return redirect(url_for("req.quoteConf", email=email))
            else:
                if (len(form.errors.items()) == 1 and "csrf_token" not in form.errors) or len(form.errors.items()) > 1:
                    out = "Error(s) encountered!"
                    for item, error in form.errors.items():
                        if item != "csrf_token":
                            out += "<br/>"+error[0]
                    session['flash'] = out
                    flash(session['flash'], 'error')
    
    return render_template("request/quote.html", form=form, session=session)

def pricing_module(perc_disc):
    x = random.randint(5000,30000)*(1-perc_disc/100)
    return [session['price']*1.05, x]

@bp.route("/<email>/quote-confirm", methods=["GET","POST"])
@login_required
def quoteConf(email):
    form = request.form
    if request.method == "POST":
        button = userButtons(request.form)
        if button is not None:
            return button
        
        if "cancel" in request.form:
            return redirect(url_for("userPage", email=email))
        if "confirm" in request.form:
            
            session['price'] = 3.999
            if session['state'] == 'TX':
                session['transport'] = 0
            else:
                session['transport'] = 0.50
            (db, cur) = get_db()
            cur.execute(
                "SELECT COUNT(*) FROM history WHERE email = '"+email+"'"
            )
            count = cur.fetchone()
            
            discLvl = ""
            perc_disc = 0
            if count[0] < 5:
                discLvl = "<5"
            elif 4 < count[0] < 11:
                discLvl = "5-10"
                perc_disc = 1
            elif 10 < count[0] < 21:
                discLvl = "11-20"
                perc_disc = 1.5
            elif 20 < count[0] < 51:
                discLvl = "21-50"
                perc_disc = 3
            else:
                discLvl = ">50"
                perc_disc = 5
            
            [comp_pr, total] = pricing_module(perc_disc)
            
            """FIGURE THIS OUT"""
            cur.execute(
                "INSERT INTO history (id,email,full_name,company_name,addr1,addr2,city,state,zipcode, gallons, date,price_per_gal, transport, discount_level, percent_discount, comp_price, total) VALUES (default,'"+session['email']+"','"+session['fullname']+"','"+session['company']+"','"+session['addr1']+"','"+session['addr2']+"','"+session['city']+"','"+session['state']+"','"+session['zipcode']+"','"+session['gal']+"','"+session['deliv_date']+" "+session['deliv_time']+":00"+"','"+str(session['price'])+"','"+str(session['transport'])+"','"+discLvl+"','"+str(perc_disc)+"','"+str(comp_pr)+"','"+str(total)+"')"
            #
            #     session['email']+"',"+session['gal']+",'"+"','"+session['deliv_date']+" "+session['deliv_time']+":00"+"','"+str(session['price'])+
            #                 "','"+str(session['transport'])+"','"+discLvl+"',"+str(perc_disc)+","+str(comp_pr)+","+str(total)+")"
            #
            #
            )
            db.commit()
            return redirect(url_for("req.receipt", email=email))
    return render_template("request/orderConf.html", form=form, session=session)

@bp.route("/<email>/order-placed", methods=["GET","POST"])
@login_required
def receipt(email):
    form = FlaskForm
    session['flash'] = "Your order has been placed"
    flash(session['flash'],'success')
    return render_template("request/receipt.html", form=form, session=session)