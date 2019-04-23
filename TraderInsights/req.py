# -*- coding: utf-8 -*-
"""
Team: Fund_Khatkhatay_Zaidi
File Description: All methods and classes relating to quote request and confirmation
"""

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from TraderInsights.auth import login_required
from TraderInsights.db import get_db

from flask_wtf import FlaskForm
from wtforms import validators, IntegerField, DateField, TimeField
import datetime
from .userButtons import userButtons

bp = Blueprint('req', __name__, url_prefix='/request')

def date_check(form, field):
    good_date = datetime.date.today()
    min_date = datetime.date.today()+datetime.timedelta(days=14)
    # print(good_date, min_date, field.data)
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
    # print(form)
    if request.method == "POST":
        button = userButtons(request.form)
        if button is not None:
            return button
        
        if "cancel" in request.form:
            return redirect(url_for("userPage", email=email))
        if "proceed" in request.form:
            # print(request.form['deliv_date'], request.form['deliv_time'])
            if form.validate() or (len(form.errors.items()) == 1 and "csrf_token" in form.errors):
                # print(form)
                session['gal'] = request.form["gal"]
                session['deliv_date'] = request.form["deliv_date"]
                session['deliv_time'] = request.form["deliv_time"]
                pricing_module()
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

def pricing_module():
    curr_price = 1.50
    if 'location' not in session:
        session['location'] = 0
        if session['state'] == 'TX':
            session['location'] = 0.02
        else:
            session['location'] = 0.04

    session['hist_disc'] = 0
    [conn, cur] = get_db()
    cur.execute("SELECT COUNT(*) FROM history WHERE email='{}'".format(session['email']))
    past_orders = cur.fetchone()[0]
    if past_orders == 0:
        session['hist_disc'] = 0
    else:
        session['hist_disc'] = 0.01

    session['gal_disc'] = 0
    if int(session['gal']) > 1000:
        session['gal_disc'] = 0.02
    else:
        session['gal_disc'] = 0.03

    session['comp_profit'] = 0.10
    # print(session['deliv_date'].split('-')[1])
    cur.execute("SELECT perc_inc FROM season_flux WHERE month='{}'".format(session['deliv_date'].split('-')[1]))
    session['rate_flux'] = float(cur.fetchone()[0])
    # print(session['rate_flux'])
    # print("location",type(session['location']))
    # print("hist_disc",type(session['hist_disc']))
    # print("gal_disc",type(session['gal_disc']))
    # print("margin",type(session['comp_profit']))
    # print("rate_flux",type(session['rate_flux']))
    session['price'] = curr_price * (1 + session['location'] - session['hist_disc'] + session['gal_disc'] + session['comp_profit'] + session['rate_flux'])
    session['total'] = session['price'] * float(session['gal'])

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
            (db, cur) = get_db()
            cur.execute(
                "INSERT INTO history (id,email,full_name,company_name,addr1,addr2,city,state,zipcode, gallons, date, price_per_gal, location_factor, history_factor, gallons_factor, comp_profit, season_flux, total) VALUES (default,'"+session['email']+"','"+session['fullname']+"','"+session['company']+"','"+session['addr1']+"','"+session['addr2']+"','"+session['city']+"','"+session['state']+"','"+session['zipcode']+"','"+session['gal']+"','"+session['deliv_date']+" "+session['deliv_time']+":00"+"','"+"{0:.3f}".format(session['price'])+"','"+str(session['location'])+"','"+str(session['hist_disc'])+"','"+str(session['gal_disc'])+"','"+str(session['comp_profit'])+"','"+str(session['rate_flux'])+"','"+"{0:.2f}".format(session['total'])+"')"
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