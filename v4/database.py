#run "createdb -O ubuntu botv4" command in order to create database
#then run "python3 database.py" command to create tables

import sys
import psycopg2
import configparser
import config

from trade import Trade

def connect():
    config = configparser.ConfigParser()
    config.read('secret.conf')
    password = config.get('database', 'password')
    return psycopg2.connect(database="botv4", host="127.0.0.1", port="5432", user="ubuntu", password=password)

def main():
    conn = connect()
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
        commission real NOT NULL DEFAULT 0,
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
    
    with Trade() as trade:
        price = trade.getMarketPrice()
        baseQuantity = trade.getQuantity(config.getBase())
        count = int(baseQuantity // config.getQuantity())
        for i in range(count):
            curs.execute('''INSERT INTO buy
                            (id, status, quantity, price)
                            VALUES ({0}, 'FILLED', {1}, {2})
                            '''.format(i+1, config.getQuantity(), price))
            price += config.getIndent()

    conn.commit()
    curs.close()
    conn.close()

    print('tables are created corresponding buy orders are added')

if __name__ == "__main__":
    main()
