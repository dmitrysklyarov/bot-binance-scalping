#---CREATE DATABASE at ec2---
#sudo -u postgres psql
#CREATE DATABASE binance OWNER ubuntu;
#---CREATE DATABASE locally---
#createdb -O ubuntu botv4

#then run "python3 database.py" command to create tables and populate orders

import sys
import psycopg2
import configparser
import conf
import traceback

from trade import Trade

def main():
    conn =  psycopg2.connect(database="botv4", host="127.0.0.1", port="5432", user="ubuntu", password=conf.getDBPassword())
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
        filled real NOT NULL DEFAULT 0,
        price real NOT NULL,
        commission real NOT NULL DEFAULT 0,
        profit real NOT NULL DEFAULT 0,
        satisfied boolean NOT NULL DEFAULT FALSE
        )''')
    curs.execute('''CREATE TABLE sell (
        id bigint PRIMARY KEY NOT NULL,
        date timestamp NOT NULL DEFAULT now(), 
        type varchar (16) NOT NULL DEFAULT 'LIMIT',
        status varchar (16) NOT NULL DEFAULT 'NEW',
        quantity real NOT NULL,
        filled real NOT NULL DEFAULT 0,
        price real NOT NULL,
        commission real NOT NULL DEFAULT 0,
        profit real NOT NULL DEFAULT 0,
        buy_id bigint NOT NULL DEFAULT 0
        )''')
    curs.execute(''' CREATE TABLE log (
        date timestamp NOT NULL DEFAULT now(),
        type varchar(16) NOT NULL,
        message text
        )''')
    conn.commit()
    print('tables are created')

    #create buy orders for existing base
    with Trade() as trade:
        initprice = price = round(trade.getMarketPrice(), 2)
        baseQuantity = trade.getQuantity(conf.getBase())
        count = int(baseQuantity // conf.getQuantity())
        for i in range(count):
            curs.execute('''INSERT INTO buy
                            (id, status, quantity, filled, price, commission, profit)
                            VALUES ({0}, 'FILLED', {1}, {1}, {2}, {3}, 0)
                            '''.format(i+1, conf.getQuantity(), price, round(conf.getQuantity() * price * trade._commission_ratio * (-1), 4)))
            price += conf.getIndent()
    conn.commit()
    print(f'{count} buy orders are created for {conf.getBase()} in the interval ({initprice}-{price}) with quantity {conf.getQuantity()} and indent {conf.getIndent()}')

    curs.close()
    conn.close()

if __name__ == "__main__":
    try:
        main()
    except Exception as err:
        print(err)
        print(traceback.format_exc())
