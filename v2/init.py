import DB
import Config
import time
from Bot import Bot

def createTables():
    #DROP TABLES
    DB.i.curs.execute("DROP TABLE IF EXISTS orders")
    DB.i.curs.execute("DROP TABLE IF EXISTS log")

    #CREATE TABLES
    DB.i.curs.execute('''CREATE TABLE orders (
        id bigint PRIMARY KEY NOT NULL,
        date timestamp NOT NULL DEFAULT now(), 
        side varchar (8) NOT NULL,
        status varchar (16) NOT NULL,
        quantity real NOT NULL,
        price real NOT NULL,
        profit real NOT NULL DEFAULT 0,
        ref_id bigint NOT NULL DEFAULT 0
        )''')
    DB.i.curs.execute(''' CREATE TABLE log (
        id serial PRIMARY KEY NOT NULL,
        date timestamp NOT NULL DEFAULT now(),
        type varchar(16) NOT NULL,
        message text,
        trace text
    )''')
    
    DB.i.conn.commit()
    return

def createData():
    base = 'BTC'
    quote = 'TUSD'
    Config.i.reloadConfig(base)
    bot = Bot(base, quote)
    price = bot.getPrice()
    baseAmount = bot.getQuantity(base)
    count = int(baseAmount // Config.i.quantity)
    for i in range(count):
        DB.i.curs.execute('''INSERT INTO orders
                            (id, side, status, quantity, price)
                            VALUES ({0}, 'buy', 'FILLED', {1}, {2})
                            '''.format(i+1, Config.i.quantity, price))
        price += Config.i.minstep

    #to buy first time normally
    DB.i.conn.commit()

    time.sleep(0.1)
    DB.i.curs.execute("INSERT INTO orders (id, side, status, quantity, price) VALUES (0, 'sell', 'FILLED', 0, 0)")
    DB.i.conn.commit()

createTables()
createData()
DB.i.conn.close()
print("done")