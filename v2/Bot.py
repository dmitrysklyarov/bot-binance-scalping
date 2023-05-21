import DB
import Config
from Binance import Binance
from Order import Order
import time

class Bot:
    def __init__(self, base, quote):
        self.base = base
        self.quote = quote
        self.symbol = base + quote
        self.binance = Binance(
            API_KEY = Config.i.API_KEY,
            API_SECRET = Config.i.API_SECRET)
    
    def __getOrder(self, orderId):
        result = self.binance.orderInfo(
            symbol = self.symbol,
            orderId = orderId
        )
        return result
    
    def __placeOrder(self, price, quantity, side):
        result = self.binance.createOrder(
            symbol = self.symbol,
            side = side,
            type = 'LIMIT',
            timeInForce = 'GTC',
            price = round(price, 1),
            quantity = quantity
            )
        return result
    
    def __placeBuyOrder(self, quantity):
        result = self.binance.createOrder(
            symbol = self.symbol,
            side = 'BUY',
            type = 'MARKET',
            quantity = quantity
            )
        return result
    
    def getQuantity(self, currency):
        account = self.binance.account()
        json_balances = account['balances']
        for x in json_balances:
            if x['asset'] == currency:
                return float(x['free'])
        return 0

    def __updateNewOrders(self, side):
        DB.i.curs.execute("SELECT id FROM orders WHERE side = '{0}' and status = 'NEW' or status = 'PARTIALLY_FILLED'".format(side))
        results = DB.i.curs.fetchall()
        newSellOrdersCount = 0
        for result in results:
            order = Order()
            order.load(result[0])
            result = self.__getOrder(order.id)
            order.status = result['status']
            if order.status == 'CANCELLED':
                order.remove()
                continue
            elif order.status == 'NEW' or order.status == 'PARTIALLY_FILLED':
                newSellOrdersCount += 1
            elif 'FILLED':
                i = 0
            order.save()
        return newSellOrdersCount > 0
    
    def __cancelOrder(self, orderId):
        result = self.binance.cancelOrder(
            symbol = self.symbol,
            orderId = orderId
        )
        return result
    
    def __createNewSellOrder(self, buyOrderId):
        order = Order()
        order.load(buyOrderId)
        if order.quantity > self.getQuantity(self.base):
            DB.i.addLog('TRADE', "Not enough base:{0} to get profit from buy order {1}, removing it".format(self.base, order.id))
            order.remove()
            return
    
        profitPcice = order.price + Config.i.profit - (order.profit / order.quantity)*2
        result = self.__placeOrder(profitPcice, order.quantity, 'sell')
        order.ref_id = result['orderId']
        order.save()
        order.insert(order.ref_id, 'sell', 'NEW', order.quantity, profitPcice, (profitPcice - order.price) * order.quantity, order.id)
        #TODO if sold immediatelly then add one more


    def __replaceSellIfNewBuy(self):
        #select open sell order
        DB.i.curs.execute("SELECT id FROM orders WHERE side = 'sell' and status = 'NEW' or status = 'PARTIALLY_FILLED'")
        results = DB.i.curs.fetchone()
        if results == None:
            #if no open order, exit
            return
        
        #select corresponding buy price for the opened sell order
        DB.i.curs.execute("SELECT price FROM orders WHERE side = 'buy' and ref_id = {0}".format(results[0]))
        sellPrice = DB.i.curs.fetchone()

        #select new buy with lower price
        DB.i.curs.execute("SELECT id, price FROM orders WHERE side = 'buy' and status = 'FILLED' AND ref_id = 0 ORDER BY price ASC")
        buyIdPrice = DB.i.curs.fetchone()

        if buyIdPrice == None:
            return
        if buyIdPrice[1] >= sellPrice[0]:
            return
        order = Order()
        order.load(results[0])
        order.status = self.__getOrder(order.id)['status']
        if order.status == 'NEW' or order.status == 'PARTIALLY_FILLED':
            order.status = self.__cancelOrder(order.id) ['status']
        if order.status == 'CANCELED':
            order.remove()
        else:
            order.save()
        self.__createNewSellOrder(buyIdPrice[0])
    
    def tryToSell(self):
        if self.__updateNewOrders('sell'):
            self.__replaceSellIfNewBuy()
            return

        DB.i.curs.execute("SELECT id FROM orders WHERE side = 'buy' AND ref_id = 0 AND status = 'FILLED' ORDER BY price ASC")
        result = DB.i.curs.fetchone()
        if result == None:
            DB.i.addLog('TRADE', "There is no corresponding byu order, need to by first")
            self.__replaceBuyIfNewSell(True)
            #TODO buy right now
            return

        self.__createNewSellOrder(result[0])

    def __getMinPrice(self):
        DB.i.curs.execute("SELECT ref_id FROM orders WHERE side = 'sell' AND (status = 'NEW' or status = 'PARTIALLY_FILLED') ORDER BY price ASC")
        result = DB.i.curs.fetchone()
        if result != None:
            DB.i.curs.execute("SELECT price FROM orders WHERE id = {0}".format(result[0]))
            minPrice = float(DB.i.curs.fetchone()[0])
            return minPrice
        
        DB.i.curs.execute("SELECT price FROM orders WHERE side = 'buy' and ref_id = 0 ORDER BY price ASC")
        result = DB.i.curs.fetchone()
        if result != None:
            return float(result[0])
        else:
            return 0
    
    def getPrice(self):
        result = self.binance.tickerPrice(symbol = self.symbol)
        return float(result['price'])
    
    def __getLastBuyCount(self):
        DB.i.curs.execute("SELECT side FROM orders WHERE status = 'FILLED' ORDER by date DESC LIMIT 10")
        sides = DB.i.curs.fetchall()
        count = 1
        for side in sides:
            if side[0] == 'sell':
                break
            if side[0] == 'buy':
                count += 1
        return count

    def __createNewBuyOrder(self):
        
        currentPrice = self.getPrice()
        minPrice = self.__getMinPrice()

        minstep = Config.i.minstep * self.__getLastBuyCount()

        if Config.i.quantity > (self.getQuantity(self.quote) / currentPrice * 1.01):
            DB.i.addLog('TRADE', "Not enough quote:{0} to buy, waiting".format(self.quote))
            time.sleep(30)
            return

        order = Order()
        result = None
        if minPrice != 0 and minPrice - currentPrice < minstep:
            order.price = minPrice - minstep
            result = self.__placeOrder(order.price, Config.i.quantity, 'buy')
            order.status = 'NEW'
            order.profit = 0
        else:
            result = self.__placeBuyOrder(Config.i.quantity)
            amount = 0
            commission = 0
            for fill in result['fills']:
                amount += float(fill['price']) * float(fill['qty'])
                commission += float(fill['commission'])
            order.price = amount / (Config.i.quantity)
            order.profit = order.price * commission * (-1)
            order.status = 'FILLED'
        order.insert(result['orderId'], 'buy', order.status, Config.i.quantity, order.price, order.profit, 0)

    def __replaceBuyIfNewSell(self, forceBuy):
        DB.i.curs.execute("SELECT id, price FROM orders WHERE side = 'buy' and status = 'NEW' or status = 'PARTIALLY_FILLED'")
        buyIdPrice = DB.i.curs.fetchone()
        if buyIdPrice == None or buyIdPrice[1] == None:
            return

        DB.i.curs.execute("SELECT price FROM orders WHERE side = 'sell' and status = 'NEW' or status = 'PARTIALLY_FILLED'")
        sellPrice = DB.i.curs.fetchone()
        if forceBuy == False and (sellPrice == None or sellPrice[0] == None):
            return        

        step = Config.i.minstep * self.__getLastBuyCount()
        if forceBuy == False and buyIdPrice[1] >= sellPrice[0] - step - Config.i.profit:
            return
        
        order = Order()
        order.load(buyIdPrice[0])        
        order.status = self.__cancelOrder(order.id) ['status']
        if order.status == 'CANCELED':
            order.remove()
        else:
            order.save()

        self.__createNewBuyOrder()

    def tryToBuy(self):
        if self.__updateNewOrders('buy'):
            self.__replaceBuyIfNewSell(False)
            return
        
        self.__createNewBuyOrder()

