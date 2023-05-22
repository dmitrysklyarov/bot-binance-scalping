import conf
import traceback
import time

from datetime import datetime
from database import Database
from order import Order
from trade import Trade

def wait(seconds):
    for i in range(seconds):
        if conf.isContinue():
            time.sleep(1)

db = Database()
while conf.isContinue():
    try:
        trade = Trade()

        #BUY PART ---------------------------------------------------------------------------------------------------
        openOrder = Order('buy', db.getOpenBuyOrder())
        currentPrice = trade.getPrice()
        prices = []
        for result in db.getNotSatisfiedPrices():
            prices.append(float(result[0]))

        if openOrder.side == None:
            #no open orders
            currentQuote = trade.getQuantity(conf.getQuote())
            if currentPrice * conf.getQuantity() * 1.1 > currentQuote:
                #not enough quote to buy
                db.addLog('warning', 'not enough quote {0} to buy with price {1}'.format(currentQuote, currentPrice))
                wait(60)
            else:
                #enough quote to buy
                if len(prices) == 0:
                    #there are no not satisfied orders in database
                    openOrder = trade.buyMarketPrice()
                    db.saveOrder(openOrder)
                    db.addLog('info', 'market buy order #{0} with price {1}'.format(openOrder.id, openOrder.price))
                else:
                    #there are not satifsied buy orders in database
                    ident = conf.getIndent() * db.getIdentMultiplier()
                    if currentPrice > max(prices) + ident:
                        openOrder = trade.buyMarketPrice()
                    elif currentPrice < min(prices) - ident:
                        openOrder = trade.buyMarketPrice()
                    else:
                        openOrder = trade.buyLimitPrice(min(prices) - ident)
                        db.addLog('warning', 'open buy order #{0} with price {1} than is lower than market price {2}'.format(openOrder.id, openOrder.price, currentPrice))

                    db.saveOrder(openOrder)
                    db.addLog('info', 'buy order #{0} with price {1}'.format(openOrder.id, openOrder.price))
        else:
            #there is an open order in database, need to update it's status
            orderInfo = trade.getOrder(openOrder.id)
            openOrder.status = orderInfo['status']
            db.saveOrder(openOrder)
            if openOrder.status == 'NEW':
                #if order from db is still opened
                if len(prices) == 0 or currentPrice - openOrder.price > conf.getIndent() and min(prices) > openOrder.price + conf.getIndent():
                    #if price went higher (above profit) then need to replace buy order with a new one
                    result = trade.cancelOrder(openOrder.id)
                    if result['status'] == 'CANCELED':
                        db.removeOrder('buy', openOrder.id)
                        db.addLog('info', 'remove buy order #{0}'.format(openOrder.id))
                    else:
                        db.saveOrder(openOrder)
                        db.addLog('warning', 'try to cancel buy order #{0}, but it is already filled'.format(openOrder.id))
        
        #SELL PART---------------------------------------------------------------------------------------------------------
        #get current open sell order
        openOrder = Order('sell', db.getOpenSellOrder())
        if openOrder.side == None:
            #if there is no open sell order
            buyOrder = Order('buy', db.getLowestNotSatisfiedOrder())
            if buyOrder.side != None:
                #there is a not satisfied orders
                currentBase = trade.getQuantity(conf.getBase())
                if currentBase < buyOrder.quantity:
                    #not enough base to sell
                    db.addLog('warning', 'not enough base {0} to sell #{1}, add satisfaction'.format(currentBase, buyOrder.id))
                    buyOrder.satisfied = True
                    db.saveOrder(buyOrder)
                else:
                    #enough base to sell
                    profit = conf.getProfit() * (1 - buyOrder.profit * 2)
                    openOrder = trade.sellLimitPrice(buyOrder.price, profit)
                    openOrder.buy_id = buyOrder.id
                    openOrder.profit = conf.getProfit() * openOrder.quantity
                    db.saveOrder(openOrder)
                    db.addLog('info', 'sell limit #{0} for buy order #{1} with price {2}'.format(openOrder.id, openOrder.buy_id, openOrder.price))
                    if openOrder.status == 'FILLED':
                        #if limit order filled immediatelly
                        db.setSafisfaction(openOrder.buy_id)
        else:
            #there is sell order in db
            orderInfo = trade.getOrder(openOrder.id)
            openOrder.status = orderInfo['status']
            db.saveOrder(openOrder)
            if openOrder.status == 'NEW':
                #order is still open
                buyOrder = Order('buy', db.getLowestNotSatisfiedOrder())
                if openOrder.buy_id != buyOrder.id:
                    result = trade.cancelOrder(openOrder.id)
                    if result['status'] == 'CANCELED':
                        db.removeOrder('sell', openOrder.id)
                        db.addLog('info', 'remove sell order #{0}'.format(openOrder.id))
                    else:
                        db.saveOrder(openOrder)
                        db.addLog('warning', 'try to cancel sell order #{0}, but it is already filled'.format(openOrder.id))
            elif openOrder.status == 'FILLED':
                db.setSafisfaction(openOrder.buy_id)
        wait(1)
    except Exception as err:
        with open("error.log", "a") as text_file:
            text_file.write(datetime.now().strftime("%d/%m/%y %H:%M:%S: ------------------------------"))
            text_file.write(traceback.format_exc())
            text_file.write(str(err))
        wait(10)
db.conn.close()
        