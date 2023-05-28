#run "createdb -O ubuntu botv4" command in order to create database
#then run "python3 database.py" command to create tables

import sys
import psycopg2
import configparser
import config

from trade import Trade

def main():
    conn =  psycopg2.connect(database="botv4", host="127.0.0.1", port="5432", user="ubuntu", password=config.getDBPassword())
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
        baseQuantity = trade.getQuantity(config.getBase())
        count = int(baseQuantity // config.getQuantity())
        for i in range(count):
            curs.execute('''INSERT INTO buy
                            (id, status, quantity, filled, price, commission, profit)
                            VALUES ({0}, 'FILLED', {1}, {1}, {2}, {3}, 0)
                            '''.format(i+1, config.getQuantity(), price, round(config.getQuantity() * price * trade._commission_ratio * (-1), 4)))
            price += config.getIndent()
    conn.commit()
    print(f'{count} buy orders are created for {config.getBase()} in the interval ({initprice}-{price}) with quantity {config.getQuantity()} and indent {config.getIndent()}')

    curs.close()
    conn.close()

if __name__ == "__main__":
    try:
        main()
    except Exception as err:
        print(err)
