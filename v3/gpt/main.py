import time
import datetime
from decimal import Decimal
from config.config import Config
from price.price import Price
from db.db import DB
from binance.binance import Binance

config = Config()
price = Price(config)
db = DB(config)
binance = Binance(config)

while True:
    try:
        buy_price = price.calculate_buy_price()
        buy_value = price.calculate_buy_value(buy_price)
        sell_price = price.calculate_sell_price(buy_price)

        balance = binance.client.get_asset_balance(asset='TUSD')
        balance = Decimal(balance['free'])

        if balance >= buy_value:
            order_id = binance.buy_limit(symbol=config.get('symbol'), quantity=str(buy_value / buy_price), price=str(buy_price))

            if order_id is not None:
                created_at = datetime.datetime.now()
                db.insert_buy_order(order_id, created_at, buy_price, buy_value, 'open')

        time.sleep(60)
    except KeyboardInterrupt:
        break
    except Exception as e:
        print(e)
