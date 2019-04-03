# -*- coding: utf-8 -*-
"""
Team: Fund_Khatkhatay_Zaidi
File Description: Creating the "database"
"""

import psycopg2
import sys
#import sqlite3
import click
from flask import current_app, g
from flask.cli import with_appcontext

def get_db():
    if 'db' not in g:
        g.db = current_app.config['postgreSQL_pool'].getconn()
    
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    
    if db is not None:
        current_app.config['postgreSQL_pool'].putconn(db)

def init_db():
    db = get_db()
    
    drop_tables(db,db.cursor())
    
    setup_db(db,db.cursor())
    
    populate_tables(db,db.cursor())

def setup_db(conn, cur):
    cur.execute('create table users (\
        email varchar(50) primary key,\
        password varchar(100),\
        full_name varchar(50),\
        company_name varchar(50),\
        addr1 varchar(100),\
        addr2 varchar(100),\
        city varchar(100),\
        state varchar(2),\
        zipcode varchar(9),\
        number_of_attempts numeric default 0,\
        logged_in numeric default 0)')
    conn.commit()
    cur.execute('create  table attempts (\
        id serial primary key,\
        email varchar(50),\
        password varchar(100),\
        result numeric,\
        ip_address varchar(50))')
    conn.commit()
    cur.execute('create table history (\
        id serial primary key,\
        email varchar(50) references users(email),\
        full_name varchar(50),\
        company_name varchar(50),\
        addr1 varchar(100),\
        addr2 varchar(100),\
        city varchar(100),\
        state varchar(2),\
        zipcode varchar(9),\
        gallons numeric,\
        date timestamp,\
        price_per_gal numeric,\
        transport numeric,\
        discount_level varchar(50),\
        percent_discount numeric,\
        comp_price numeric,\
        total numeric\
        )')
    conn.commit()
    cur.execute('create table comp_rate (\
        id serial primary key,\
        name varchar(50),\
        January numeric,\
        February numeric,\
        March numeric,\
        April numeric,\
        May numeric,\
        June numeric,\
        July numeric,\
        August numeric,\
        September numeric,\
        October numeric,\
        November numeric,\
        December numeric,\
        year numeric)')
    conn.commit()
    cur.execute('create table season_flux (\
        season numeric,\
        perc_inc numeric)')
    conn.commit()

def drop_tables(conn,cur):
    cur.execute("drop table if exists season_flux")
    conn.commit()
    cur.execute("drop table if exists history")
    conn.commit()
    cur.execute("drop table if exists comp_rate")
    conn.commit()
    cur.execute("drop table if exists attempts")
    conn.commit()
    cur.execute("drop table if exists users")
    conn.commit()

def populate_tables(conn,cur):
    f = open(r'populate_users.csv', 'r')
    cur.copy_from(f, 'users', sep=',')
    conn.commit()
    f.close()
    f = open(r'populate_comp2017.csv', 'r')
    cur.copy_from(f, 'comp_rate', sep=',')
    conn.commit()
    f.close()
    f = open(r'populate_comp2018.csv', 'r')
    cur.copy_from(f, 'comp_rate', sep=',')
    conn.commit()
    f.close()
    f = open(r'populate_flux.csv', 'r')
    cur.copy_from(f, 'season_flux', sep=',')
    conn.commit()
    f.close()
    f = open(r'populate_history.csv', 'r')
    cur.copy_from(f, 'history', sep=',')
    conn.commit()
    f.close()
    



@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)