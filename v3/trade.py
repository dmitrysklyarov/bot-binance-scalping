import configparser
import conf

from binance import Binance
from order import Order

class Trade():
    binance: Binance
    commission = 0

    def __init__(self):

        config = configparser.ConfigParser()
        config.read('binance.ini')

        api_key = config.get('API', 'API_KEY')
        api_secret = config.get('API', 'API_SECRET')
        self.binance = Binance(
            API_KEY= api_key,
            API_SECRET= api_secret)

    #BUY ORDERS CHAPTER ---------------------------------------------------------------------------
    def buyMarketPrice(self):
        quantity = conf.getQuantity()
        type = 'MARKET'
        result = self.binance.createOrder(
            symbol = conf.getSymbol(),
            side = 'BUY',
            type = type,
            quantity = quantity
            )
        amount = 0
        commission = 0
        for fill in result['fills']:
            amount += float(fill['price']) * float(fill['qty'])
            commission += float(fill['commission'])
        price = amount / quantity
        profit = price * commission * (-1)
        self.commission = profit / price
        order = Order('buy', [result['orderId'], 0, type,'FILLED', quantity, price, profit, False])
        return order
    
    def buyLimitPrice(self, price):
        quantity = conf.getQuantity()
        type = 'LIMIT'
        result = self.binance.createOrder(
            symbol = conf.getSymbol(),
            side = 'BUY',
            type = type,
            timeInForce = 'GTC',
            price = round(price,2),
            quantity = quantity
            )
        order = Order('buy', [result['orderId'], 0, type, result['status'], quantity, result['price'], price*self.commission, False])
        return order
    
    #SELL ORDERS CHAPTER -------------------------------------------------------------------------
    def sellLimitPrice(self, price, profit):
        quantity = conf.getQuantity()
        type = 'LIMIT'
        result = self.binance.createOrder(
            symbol = conf.getSymbol(),
            side = 'SELL',
            type = type,
            timeInForce = 'GTC',
            price = round(price + profit, 2),
            quantity = quantity
            )
        order = Order('sell', [result['orderId'], 0, type, result['status'], quantity, result['price'], profit, 0])
        return order

    #COMMON ORDERS CHAPTER -----------------------------------------------------------------------
    def getOrder(self, orderId):
        result = self.binance.orderInfo(
            symbol = conf.getSymbol(),
            orderId = orderId
        )
        return result

    def getQuantity(self, currency):
        account = self.binance.account()
        json_balances = account['balances']
        for x in json_balances:
            if x['asset'] == currency:
                return float(x['free'])
        return 0
    
    def cancelOrder(self, orderId):
        result = self.binance.cancelOrder(
            symbol = conf.getSymbol(),
            orderId = orderId
        )
        return result

    def getPrice(self):
        result = self.binance.tickerPrice(symbol = conf.getSymbol())
        return float(result['price'])
