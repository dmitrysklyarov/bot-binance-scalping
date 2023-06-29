import conf
from order import Order

def calculateBuyPrice(buyOrder:Order):
    if buyOrder is None:
        return 0
    else:
        return round(buyOrder._price - conf.getIndent(), 2)

def calculateBuyValue():
    return conf.getQuantity()

def calculateSellPrice(buyOrder:Order, commission_ratio):
    sell_price = buyOrder._price + conf.getProfit() #required profit
    sell_price += commission_ratio * sell_price #sell order comission
    sell_price += buyOrder._price * buyOrder._commission * buyOrder._quantity #buy order comission

    return buyOrder, round(sell_price, 2)