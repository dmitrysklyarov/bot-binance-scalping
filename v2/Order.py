import DB
"""
id bigint PRIMARY KEY NOT NULL,
date timestamp NOT NULL DEFAULT now(), 
side varchar (8) NOT NULL,
status varchar (16) NOT NULL,
quantity real NOT NULL,
price real NOT NULL,
profit real NOT NULL DEFAULT 0,
ref_id bigint NOT NULL DEFAULT 0
"""

class Order():
    def __init__(self):
        return
    
    def load(self, id):
        DB.i.curs.execute("SELECT * FROM orders WHERE id = '{0}'".format(id))
        order = DB.i.curs.fetchone()
        self.id = order[0]
        self.date = order[1]
        self.side = order[2]
        self.status = order[3]
        self.quantity = order[4]
        self.price = order[5]
        self.profit = order[6]
        self.ref_id = order[7]
    
    def insert(self, id, side, status, quantity, price, profit, ref_id):
        self.id = id
        self.side = side
        self.status = status
        self.quantity = quantity
        self.price = price
        self.profit = profit
        self.ref_id = ref_id
        
        DB.i.curs.execute('''INSERT INTO orders 
            (id, side, status, quantity, price, profit, ref_id)
            VALUES ({0}, '{1}', '{2}', {3}, {4}, {5}, {6})
            '''.format(self.id, self.side, self.status, self.quantity, self.price, self.profit, self.ref_id))
        DB.i.conn.commit()
        DB.i.curs.execute("SELECT date FROM orders WHERE id = '{0}'".format(id))
        self.date = DB.i.curs.fetchone()[0]

    
    def save(self):
        DB.i.curs.execute('''UPDATE orders 
            SET status = '{0}', ref_id = {1}
            WHERE id = {2}
            '''.format(self.status, self.ref_id, self.id))
        DB.i.conn.commit()
    
    def remove(self):
        DB.i.curs.execute("UPDATE orders SET ref_id = 0 WHERE ref_id = {0}".format(self.id))
        DB.i.curs.execute("DELETE FROM orders WHERE id = {0}".format(self.id))
        DB.i.conn.commit()
