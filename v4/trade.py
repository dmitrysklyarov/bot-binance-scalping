import configparser
import psycopg2
import database
import config

from binance import Binance
from order import Order

class Trade:
    _binance:Binance = None
    _conn:psycopg2.extensions.connection = None
    _curs:psycopg2.extensions.cursor = None

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('secret.conf')

        api_key = config.get('binance', 'API_KEY')
        api_secret = config.get('binance', 'API_SECRET')
        self._binance = Binance(
            API_KEY= api_key,
            API_SECRET= api_secret)

    def __enter__(self):
        self._conn = database.connect()
        self._curs = self._conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._curs is not None:
            self._curs.close()
        if self._conn is not None:
            self._conn.close()

    def getMarketPrice(self):
        result = self._binance.tickerPrice(symbol = config.getSymbol())
        return float(result['price'])

    def getOpenedBuyLimitOrder(self):
        self._curs.execute("SELECT * FROM buy WHERE status = 'NEW' OR status = 'PARTIALLY_FILLED'")
        result = self._curs.fetchone()
        return None

    def getOpenedSellLimitOrder(self):
        return None
    
    def createBuyMarketOrder(self, buy_value):
        return None

    def createBuyLimitOrder(self, buy_price, buy_value):
        return None

    def updateTopLimitOrderToCurrentPrice(self):
        return self

    def getOpenedSellLimitOrder(self):
        return None

    def createSellLimitOrder(self, sell_price):
        return None