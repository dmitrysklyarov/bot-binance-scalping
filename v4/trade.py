import psycopg2
import config
import settings

from binance import Binance
from order import Order, OrderDirection

class Trade:
    _binance:Binance = None
    _conn:psycopg2.extensions.connection = None
    _curs:psycopg2.extensions.cursor = None
    _commission_ratio = 0

    def __init__(self):
        self._binance = Binance(
            API_KEY = config.getAPIKey(),
            API_SECRET = config.getAPISecret())

    def __enter__(self):
        self._conn = psycopg2.connect(database="botv4", host="127.0.0.1", port="5432", user="ubuntu", password=config.getDBPassword())
        self._curs = self._conn.cursor()
        self._commission_ratio = config.getCommission()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:            
            #close connection
            if self._curs is not None:
                self._curs.close()
            if self._conn is not None:
                self._conn.close()

        except Exception as err:
            print(err)

    #METHODS WITH BINANCE MARKET
    def getMarketPrice(self):
        result = self._binance.tickerPrice(symbol = config.getSymbol())
        return float(result['price'])
    
    def getQuantity(self, currency):
        account = self._binance.account()
        json_balances = account['balances']
        for x in json_balances:
            if x['asset'] == currency:
                return float(x['free'])
        return 0

    #METHODS WITH ORDERS IN DATABASE
    def __getOpenedLimitOrder(self, direction:OrderDirection):
        self._curs.execute(f"SELECT * FROM {direction.value} WHERE status = 'NEW' OR status = 'PARTIALLY_FILLED'")
        result = self._curs.fetchone()
        if result is None:
            return None
        else:
            order = Order(self._conn, direction, result)
            return order

    def getOpenedBuyLimitOrder(self):
        return self.__getOpenedLimitOrder(OrderDirection.BUY)


    def getOpenedSellLimitOrder(self):
        return self.__getOpenedLimitOrder(OrderDirection.SELL)
    
    def getNotSatisfiedOrder(self, top=False):
        orderBy = "ASC"
        if top:
            orderBy = "DESC"
        self._curs.execute(f"SELECT * FROM {OrderDirection.BUY.value} WHERE satisfied = False AND status = 'FILLED' ORDER BY price {orderBy} LIMIT 1")
        result = self._curs.fetchone()
        if result is None:
            return None
        else:
            return Order(self._conn, OrderDirection.BUY, result)
        
    def __extractPrice(self, fills:list):
        amount = 0
        commission = 0
        quantity = 0
        price = 0
        for fill in fills:
            amount += float(fill['price']) * float(fill['qty'])
            quantity += float(fill['qty'])
            if 'commission' in fill:
                commission += float(fill['commission'])
        if quantity > 0:
            price = round(amount / quantity, 2)
        return price, commission
    
    #METHODS WITH ORDERS IN BINANCE
    def createBuyMarketOrder(self, buy_value):
        try:
            quantity = buy_value
            type = 'MARKET'
            result = self._binance.createOrder(
                symbol = config.getSymbol(),
                side = 'BUY',
                type = type,
                quantity = quantity
                )
            price, commission = self.__extractPrice(result['fills'])
            self._commission_ratio = round(commission / quantity, 6)
            order = Order(self._conn, 
                        OrderDirection.BUY, 
                        (result['orderId'],                   #id
                        0,                                    #date
                        type,                                 #type
                        'FILLED',                             #status 
                        quantity,                             #quantity
                        quantity,                             #filled
                        price,                                #price
                        round(commission * (-1) * price, 4),  #commission
                        0,                                    #profit
                        False))                               #satisfied
            settings.resetWaitCounter()
            return order
        except Exception as err:
            if 'insufficient balance' in str(err):
                return None
            else:
                raise err

    def createBuyLimitOrder(self, buy_price, buy_value):
        try:
            quantity = buy_value
            price = round(buy_price,2)
            type = 'LIMIT'
            result = self._binance.createOrder(
                symbol = config.getSymbol(),
                side = 'BUY',
                type = type,
                timeInForce = 'GTC',
                price = price,
                quantity = quantity
                )
            if result['status'] == 'FILLED':
                price, commission = self.__extractPrice(result['fills'])
            order = Order(self._conn, 
                        OrderDirection.BUY, 
                        (result['orderId'],                       #id
                        0,                                        #date
                        type,                                     #type
                        'NEW',                                    #status 
                        quantity,                                 #quantity
                        0,                                        #filled
                        price,                                    #price
                        0,                                        #commission
                        0,                                        #profit
                        False))                                   #satisfied
            settings.resetWaitCounter()
            return order
        except Exception as err:
            if 'insufficient balance' in str(err):
                return None
            else:
                raise err
    
    def cleanAllNotSatisfiedBuyOrders(self):
        self._curs.execute(f"DELETE FROM {OrderDirection.BUY.value} WHERE satisfied = False")
        self._conn.commit()

    def createSellMarketOrder(self, correspondingBuyOrder:Order):
        try:
            quantity = correspondingBuyOrder._quantity
            type = 'MARKET'
            result = self._binance.createOrder(
                symbol = config.getSymbol(),
                side = 'SELL',
                type = type,
                quantity = quantity
                )
            price, commission = self.__extractPrice(result['fills'])
            self._commission_ratio = round(commission / quantity, 6)
            order = Order(self._conn, 
                        OrderDirection.SELL, 
                        (result['orderId'],                                             #id
                        0,                                                              #date
                        type,                                                           #type
                        'FILLED',                                                       #status 
                        quantity,                                                       #quantity
                        quantity,                                                       #filled
                        price,                                                          #price
                        round(price * (self._commission_ratio), 4),                     #commission
                        round((price - correspondingBuyOrder._price) * quantity, 4),    #profit
                        correspondingBuyOrder._id))                                     #ref_id
            settings.resetWaitCounter()
            return order
        except Exception as err:
            if 'insufficient balance' in str(err):
                return None
            else:
                raise err


    def createSellLimitOrder(self, sell_price, correspondingBuyOrder:Order):
        try:
            quantity = correspondingBuyOrder._quantity
            price = round(sell_price, 2)
            type = 'LIMIT'
            result = self._binance.createOrder(
                symbol = config.getSymbol(),
                side = 'SELL',
                type = type,
                timeInForce = 'GTC',
                price = price,
                quantity = quantity
                )
            if result['status'] == 'FILLED':
                price, commission = self.__extractPrice(result['fills'])
            order = Order(self._conn, 
                        OrderDirection.SELL, 
                        (result['orderId'],                                             #id
                        0,                                                              #date
                        type,                                                           #type
                        'NEW',                                                          #status 
                        quantity,                                                       #quantity
                        0,                                                              #filled
                        price,                                                          #price
                        round(price * (self._commission_ratio), 4),                     #commission
                        round((price - correspondingBuyOrder._price) * quantity, 4),    #profit
                        correspondingBuyOrder._id))                                     #ref_id
            settings.resetWaitCounter()
            return order
        except Exception as err:
            if 'insufficient balance' in str(err):
                return None
            else:
                raise err
    
    def cancelLimitOrder(self, order:Order):
        result = self._binance.cancelOrder(
            symbol = config.getSymbol(),
            orderId = order._id
        )
        order._status = result['status']
        order._filled = float(result['executedQty'])
        return order
    
    def updateLimitOrder(self, order:Order):
        result = self._binance.orderInfo(
            symbol = config.getSymbol(),
            orderId = order._id
        )
        order._status = result['status']
        order._price = float(result['price'])
        order._filled = float(result['executedQty'])
        return order