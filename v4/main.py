import config
import traceback
import time
import signal
import calculator

from trade import Trade
from order import Order
from datetime import datetime

isContinue = True
def signal_handler(sig, frame):
    global isContinue
    isContinue = False
signal.signal(signal.SIGTERM, signal_handler)

def wait(seconds):
    for i in range(seconds):
        if isContinue:
            time.sleep(1)

def main():
    global isContinue
    while isContinue:
        try:
            with Trade() as trade:
                #1. Select NEW or PARTIALLY_FILLED buy limit order from the database
                openedBuyLimitOrder = trade.getOpenedBuyLimitOrder()
                if openedBuyLimitOrder is None:
                    #2. Calculate buy_price
                    buy_price = calculator.calculateBuyPrice()
                    buy_value = calculator.calculateBuyValue()
                    buyOrder:Order = None
                    if buy_price == 0:
                        #3. Create buy market order with buy_value
                        buyOrder = trade.createBuyMarketOrder(buy_value)
                    else:
                        #4. Create new buy limit order with buy_price and buy_value
                        buyOrder = trade.createBuyLimitOrder(buy_price, buy_value)
                    if buyOrder is None:
                        # If not enough quote, then updated top limit order to the current price
                        trade.updateTopLimitOrderToCurrentPrice()
                    else:
                        # Otherwise, save buy order to database (price, status = FILLED, average amount)
                        buyOrder.save()
                else:
                    #5. Get the opened buy limit order status from Binance
                    openedBuyLimitOrder.update()
                    openedBuyLimitOrder.save()
                    if openedBuyLimitOrder.status == "FILLED":
                        continue
                    #6. Calculate buy_price
                    buy_price = calculator.calculateBuyPrice()
                    if buy_price == 0 or buy_price != openedBuyLimitOrder.price:
                        #7. Cancel the buy limit order
                        openedBuyLimitOrder.cancel()
                        if openedBuyLimitOrder.status == "CANCELED" and openedBuyLimitOrder.filled == 0:
                            #8. Delete the buy limit order from database
                            openedBuyLimitOrder.delete()
                        else:
                            #9. Save buy limit order to database (status = FILLED, filled amount)
                            openedBuyLimitOrder.status = "FILLED"
                            openedBuyLimitOrder.save()
                    else:
                        #10. Select NEW or PARTIALLY_FILLED sell limit order from the database
                        openedSellLimitOrder = trade.getOpenedSellLimitOrder()
                        if openedSellLimitOrder is None:
                            #11. Calculate sell_price
                            buyOrder, sell_price = calculator.calculateSellPrice()
                            if sell_price == 0 or buyOrder is None:
                                continue
                            #12. Create new sell limit order with sell_price
                            openedSellLimitOrder = trade.createSellLimitOrder(sell_price)
                            if openedSellLimitOrder is None:
                                #If not enough base then delete corresponding buy limit order from the database
                                buyOrder.delete()
                            else:
                                #otherwise save the sell limit order to database
                                openedSellLimitOrder.save()
                        else:
                            #13. Get the curerent sell limit order status from Binance
                            openedSellLimitOrder.update()
                            openedSellLimitOrder.save()
                            if openedSellLimitOrder.status == "FILLED":
                                continue

                            buyOrder, sell_price = calculator.calculateSellPrice()
                            if sell_price == 0 or buyOrder is None:
                                if (openedSellLimitOrder.price == sell_price):
                                    wait(1)
                                continue

                            #17. Cancel the current sell limit order
                            openedSellLimitOrder.cancel()
                            if openedSellLimitOrder.status == "CANCELED" and openedSellLimitOrder.filled == 0:
                                #18. Delete the sell limit order from database
                                openedSellLimitOrder.delete()
                            else:
                                #19. Save sell limit order to database (status = FILLED, filled amount, profit based on filled)
                                openedSellLimitOrder.status = "FILLED"
                                openedSellLimitOrder.save()
                wait(1)
        except Exception as err:
            with open("error.log", "a") as text_file:
                text_file.write(datetime.now().strftime("%d/%m/%y %H:%M:%S: ------------------------------"))
                text_file.write(traceback.format_exc())
                text_file.write(str(err))
            wait(10)

if __name__ == "__main__":
    main()
