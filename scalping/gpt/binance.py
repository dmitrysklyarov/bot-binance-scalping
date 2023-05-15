from binance.client import Client
from binance.exceptions import BinanceAPIException
from decimal import Decimal
import time

class Binance:
    def __init__(self, config):
        self.config = config
        self.client = Client(self.config.get('binance', 'api_key'), self.config.get('binance', 'api_secret'))

    def get_price(self, symbol):
        try:
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            return Decimal(ticker['price'])
        except BinanceAPIException as e:
            print(f'Failed to get {symbol} price: {e}')
            return None

    def buy_limit(self, symbol, quantity, price):
        try:
            order = self.client.order_limit_buy(
                symbol=symbol,
                quantity=quantity,
                price=price
            )
            return order['orderId']
        except BinanceAPIException as e:
            print(f'Failed to place buy order: {e}')
            return None

    def sell_limit(self, symbol, quantity, price):
        try:
            order = self.client.order_limit_sell(
                symbol=symbol,
                quantity=quantity,
                price=price
            )
            return order['orderId']
        except BinanceAPIException as e:
            print(f'Failed to place sell order: {e}')
            return None

    def get_order(self, symbol, order_id):
        try:
            order = self.client.get_order(symbol=symbol, orderId=order_id)
            return Decimal(order['price']), Decimal(order['origQty'])
        except BinanceAPIException as e:
            print(f'Failed to get order: {e}')
            return None, None
