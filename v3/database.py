#---CREATE DATABASE AND ASSIGN ROLES---
#sudo -u postgres psql
#CREATE DATABASE trade OWNER ubuntu;

import psycopg2
import conf
from order import Order
import configparser

class Database():
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('secret.conf')
        password = config.get('database', 'password')

        self.conn = psycopg2.connect(database="trade", host = "127.0.0.1", port = "5432", user="ubuntu", password=password)
        self.curs = self.conn.cursor()

    #BUY ORDERS CHAPTER ---------------------------------------------------------------------------
    def getOpenBuyOrder(self):
        self.curs.execute("SELECT * FROM buy WHERE status = 'NEW' OR status = 'PARTIALLY_FILLED'")
        result = self.curs.fetchone()
        return result
    
    def getNotSatisfiedPrices(self):
        self.curs.execute("SELECT price FROM buy WHERE status = 'FILLED' AND NOT satisfied ORDER BY price ASC")
        return self.curs.fetchall()

    def getIdentMultiplier(self):
        lastOrders = ['sell', 'buy', 'sell']
        #TODO select join from buy and sell
        if lastOrders.count('sell') >= lastOrders.count('buy'):
            return 1
        else:
            return lastOrders.count('buy') / lastOrders.count('sell')

    def setSafisfaction(self, id):
        self.curs.execute("UPDATE buy SET satisfied = True WHERE id = {0}".format(id))
    
    #SELL ORDERS CHAPTER -------------------------------------------------------------------------
    def getOpenSellOrder(self):
        self.curs.execute("SELECT * FROM sell WHERE status = 'NEW' OR status = 'PARTIALLY_FILLED'")
        result = self.curs.fetchone()
        return result
    
    def getLowestNotSatisfiedOrder(self):
        self.curs.execute("SELECT * FROM buy WHERE status = 'FILLED' AND NOT satisfied ORDER BY price ASC")
        result = self.curs.fetchone()
        return result

    #COMMON ORDERS CHAPTER -----------------------------------------------------------------------
    def saveOrder(self, order:Order):
        self.curs.execute("SELECT id FROM {0} WHERE id = {1}".format(order.side, order.id))
        result = self.curs.fetchone()
        if result is None:
            self.curs.execute('''INSERT INTO {0} 
                (id, type, status, quantity, price, profit)
                VALUES ({1}, '{2}', '{3}', {4}, {5}, {6})
            '''.format(order.side, order.id, order.type, order.status, order.quantity, order.price, order.profit))
        else:
            self.curs.execute('''UPDATE {0}
                SET type = '{1}', status = '{2}', quantity = {3}, price = {4}, profit = {5}
                WHERE id = {6}
            '''.format(order.side, order.type, order.status, order.quantity, order.price, order.profit, order.id))
        if order.side == 'sell':
            self.curs.execute("UPDATE sell SET buy_id = {0} WHERE id = {1}".format(order.buy_id, order.id))
        else:
            self.curs.execute("UPDATE buy SET satisfied = {0} WHERE id = {1}".format(order.satisfied, order.id))
        self.conn.commit()
    
    def removeOrder(self, side, id):
        self.curs.execute("DELETE FROM {0} WHERE id = {1}".format(side, id))
        self.conn.commit()

    def addLog(self, type, message):
        self.curs.execute("INSERT INTO log (type, message) VALUES ('{0}', '{1}')".format(type, message))
        self.conn.commit()

