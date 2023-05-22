import conf
from database import Database
from trade import Trade

def createTables(db:Database):
    #DROP TABLES
    db.curs.execute("DROP TABLE IF EXISTS buy")
    db.curs.execute("DROP TABLE IF EXISTS sell")
    db.curs.execute("DROP TABLE IF EXISTS log")

    #CREATE TABLES
    db.curs.execute('''CREATE TABLE buy (
        id bigint PRIMARY KEY NOT NULL,
        date timestamp NOT NULL DEFAULT now(), 
        type varchar (16) NOT NULL DEFAULT 'MARKET',
        status varchar (16) NOT NULL DEFAULT 'NEW',
        quantity real NOT NULL,
        price real NOT NULL,
        profit real NOT NULL DEFAULT 0,
        satisfied boolean NOT NULL DEFAULT FALSE
        )''')
    db.curs.execute('''CREATE TABLE sell (
        id bigint PRIMARY KEY NOT NULL,
        date timestamp NOT NULL DEFAULT now(), 
        type varchar (16) NOT NULL DEFAULT 'LIMIT',
        status varchar (16) NOT NULL DEFAULT 'NEW',
        quantity real NOT NULL,
        price real NOT NULL,
        profit real NOT NULL DEFAULT 0,
        buy_id bigint NOT NULL DEFAULT 0
        )''')
    db.curs.execute(''' CREATE TABLE log (
        date timestamp NOT NULL DEFAULT now(),
        type varchar(16) NOT NULL,
        message text
        )''')


def createData(db:Database):
    #insert buy orders for the current base quantity
    trade = Trade()
    price = trade.getPrice()
    baseQuantity = trade.getQuantity(conf.getBase())
    count = int(baseQuantity // conf.getQuantity())
    for i in range(count):
        db.curs.execute('''INSERT INTO buy
                            (id, status, quantity, price)
                            VALUES ({0}, 'FILLED', {1}, {2})
                            '''.format(i+1, conf.getQuantity(), price))
        price += conf.getIndent()

db = Database()
createTables(db)
createData(db)
db.conn.commit()
db.conn.close()
print('database created')