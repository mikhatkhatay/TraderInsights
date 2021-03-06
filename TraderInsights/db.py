# -*- coding: utf-8 -*-
"""
Team: Fund_Khatkhatay_Zaidi
File Description: Creating the "database"
"""

import click
from flask import current_app, g
from flask.cli import with_appcontext

def get_db():
    if 'db' not in g:
        g.db = current_app.config['postgreSQL_pool'].getconn()

    if 'cur' not in g:
        g.cur = g.db.cursor()

    return (g.db, g.cur)

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        current_app.config['postgreSQL_pool'].putconn(db)

def init_db(testing=False):
    (db, cur) = get_db()
    
    drop_tables(db,cur)
    
    setup_db(db,cur)

    populate_tables(db,cur,testing)

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
    cur.execute('CREATE SEQUENCE table_name_id_seq')
    conn.commit()
    cur.execute('create table history (\
        id integer NOT NULL DEFAULT nextval(\'table_name_id_seq\') primary key,\
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
        location_factor numeric,\
        history_factor numeric,\
        gallons_factor numeric,\
        comp_profit numeric,\
        season_flux numeric,\
        total numeric\
        )')
    conn.commit()
    cur.execute("alter sequence table_name_id_seq minvalue 4 start with 4 restart with 4")
    conn.commit()
    cur.execute('create table season_flux (\
        month numeric,\
        perc_inc numeric)')
    conn.commit()

def drop_tables(conn,cur):
    cur.execute("drop table if exists season_flux")
    conn.commit()
    cur.execute("drop table if exists history")
    conn.commit()
    cur.execute("drop sequence if exists table_name_id_seq")
    conn.commit()
    cur.execute("drop table if exists comp_rate")
    conn.commit()
    cur.execute("drop table if exists attempts")
    conn.commit()
    cur.execute("drop table if exists users")
    conn.commit()

def populate_tables(conn,cur,testing):
    try:
        if testing:
            f = open(r'test_users.csv', 'r')
            cur.copy_from(f, 'users', sep=',')
            conn.commit()
            f.close()
            f = open(r'test_flux.csv', 'r')
            cur.copy_from(f, 'season_flux', sep=',')
            conn.commit()
            f.close()
            cur.execute("SELECT * FROM users")
            rows = cur.fetchall()
            for r in rows:
                print(r)
        else:
            f = open(r'populate_users.csv', 'r')
            cur.copy_from(f, 'users', sep=',')
            conn.commit()
            f.close()
            f = open(r'populate_flux.csv', 'r')
            cur.copy_from(f, 'season_flux', sep=',')
            conn.commit()
            f.close()
            # f = open(r'populate_history.csv', 'r')
            # cur.copy_from(f, 'history', sep=',')
            # conn.commit()
            # f.close()
        print("tables populated")
    except:
        print("No data files")



@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)