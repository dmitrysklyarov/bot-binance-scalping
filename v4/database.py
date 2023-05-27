#run "createdb botv4" command in order to create database
#then run "python3 database.py create" command to create tables

import sys
import psycopg2

def connect():
    return psycopg2.connect(database="botv4", host = "127.0.0.1", port = "5432", user="ubuntu", password="ubuntu")

def createTables(conn:psycopg2.extensions.connection):
    curs = conn.cursor()
    #DROP TABLES
    curs.execute("DROP TABLE IF EXISTS buy")
    curs.execute("DROP TABLE IF EXISTS sell")
    curs.execute("DROP TABLE IF EXISTS log")

    #CREATE TABLES
    curs.execute('''CREATE TABLE buy (
        id bigint PRIMARY KEY NOT NULL,
        date timestamp NOT NULL DEFAULT now(), 
        type varchar (16) NOT NULL DEFAULT 'MARKET',
        status varchar (16) NOT NULL DEFAULT 'NEW',
        quantity real NOT NULL,
        price real NOT NULL,
        profit real NOT NULL DEFAULT 0,
        satisfied boolean NOT NULL DEFAULT FALSE
        )''')
    curs.execute('''CREATE TABLE sell (
        id bigint PRIMARY KEY NOT NULL,
        date timestamp NOT NULL DEFAULT now(), 
        type varchar (16) NOT NULL DEFAULT 'LIMIT',
        status varchar (16) NOT NULL DEFAULT 'NEW',
        quantity real NOT NULL,
        price real NOT NULL,
        profit real NOT NULL DEFAULT 0,
        buy_id bigint NOT NULL DEFAULT 0
        )''')
    curs.execute(''' CREATE TABLE log (
        date timestamp NOT NULL DEFAULT now(),
        type varchar(16) NOT NULL,
        message text
        )''')

def main():
    command = sys.argv[1] if len(sys.argv) > 1 else None
    param = sys.argv[2] if len(sys.argv) > 2 else None

    if command == 'create':
        print('create')
