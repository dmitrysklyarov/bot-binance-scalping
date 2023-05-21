#---INSTALL POSTRESQL MAC---
#pip install psycopg2
#brew install postgresql

#---CREATE DATABASE AND ASSIGN ROLES---
#sudo -u postgres psql
#CREATE DATABASE binance OWNER ubuntu;

import os
import psycopg2
from Order import Order
import traceback

class DB():

    def __init__(self):
        self.conn = psycopg2.connect(database="binance", host = "127.0.0.1", port = "5432", user="ubuntu", password="ubuntu")
        self.curs = self.conn.cursor()
    
    def addLog(self, type, message):
        message = str(message).replace("'", "\"")
        trace = str(traceback.format_exc()).replace("'", "\"")
        self.curs.execute("INSERT INTO log (type, message, trace) VALUES ('{0}', '{1}', '{2}')".format(type, message, trace))
        self.conn.commit()

i = DB()