# -*- coding: utf-8 -*-
"""
Created on Tue Mar 19 00:50:17 2019

@author: M. Ibrahim
"""

import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tabledef import *
 
engine = create_engine('sqlite:///tutorial.db', echo=True)
 
# create a Session
Session = sessionmaker(bind=engine)
session = Session()
 
user = User("admin@mail.com","password")
session.add(user)
 
user = User("python@mail.com","python")
session.add(user)
 
user = User("jumpiness@mail.com","python")
session.add(user)
 
# commit the record the database
session.commit()
 
session.commit()