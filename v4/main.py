#nohup python3 -u main.py &

import traceback
import time
import signal
import calculator
import settings
import logging

from trade import Trade
from datetime import datetime

def signal_handler(sig, frame):
    settings.isContinue = False
signal.signal(signal.SIGTERM, signal_handler)

def wait(seconds):
    for i in range(seconds):
        if settings.isContinue:
            time.sleep(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    logging.info('start main()')
    while settings.isContinue:
        try:
            with Trade() as trade:
                #1. Select NEW or PARTIALLY_FILLED buy limit order from the database
                openedBuyLimitOrder = trade.getOpenedBuyLimitOrder()
                if openedBuyLimitOrder is None:
                    #2. Calculate buy_price
                    buy_price = calculator.calculateBuyPrice(trade.getNotSatisfiedOrder(False))
                    buy_value = calculator.calculateBuyValue()
                    if buy_price == 0:
                        #3. Create buy market order with buy_value
                        openedBuyLimitOrder = trade.createBuyMarketOrder(buy_value)
                    else:
                        #4. Create new buy limit order with buy_price and buy_value
                        openedBuyLimitOrder = trade.createBuyLimitOrder(buy_price, buy_value)
                    if openedBuyLimitOrder is None:
                        # If not enough quote, then check settings, whether we need to sell top order
                        if settings.getSellTopOrder():
                            # Need to sell, then sell top order
                            sellMarketOrder = trade.createSellMarketOrder(trade.getNotSatisfiedOrder(True))
                            if sellMarketOrder is None:
                                wait(60)
                                raise Exception("Nothing to sell and not enough quote")
                            else:
                                sellMarketOrder.insert()
                                sellMarketOrder.update()#in order to set up satisfaction to buy order
                        else:
                            # No need to sell, then just wait
                            wait(60)
                    else:
                        # Otherwise, insert buy order to database (price, status = FILLED, average amount)
                        openedBuyLimitOrder.insert()
                else:
                    #5. Get the opened buy limit order status from Binance
                    openedBuyLimitOrder = trade.updateLimitOrder(openedBuyLimitOrder)
                    openedBuyLimitOrder.update()
                    if openedBuyLimitOrder._status == "FILLED":
                        continue
                    #6. Calculate buy_price
                    buy_price = calculator.calculateBuyPrice(trade.getNotSatisfiedOrder(False))
                    if buy_price == 0 or buy_price != openedBuyLimitOrder._price:
                        #7. Cancel the buy limit order
                        openedBuyLimitOrder = trade.cancelLimitOrder(openedBuyLimitOrder)
                        if openedBuyLimitOrder._status == "CANCELED" and openedBuyLimitOrder._filled == 0:
                            #8. Delete the buy limit order from database
                            openedBuyLimitOrder.delete()
                        else:
                            #9. Save buy limit order to database (status = FILLED, filled amount)
                            openedBuyLimitOrder._status = "FILLED"
                            openedBuyLimitOrder.update()
                    else:
                        #10. Select NEW or PARTIALLY_FILLED sell limit order from the database
                        openedSellLimitOrder = trade.getOpenedSellLimitOrder()
                        if openedSellLimitOrder is None:
                            #11. Calculate sell_price
                            correspondingBuyOrder, sell_price = calculator.calculateSellPrice(trade.getNotSatisfiedOrder(False), trade._commission_ratio)
                            if sell_price == 0 or correspondingBuyOrder is None:
                                continue
                            #12. Create new sell limit order with sell_price
                            openedSellLimitOrder = trade.createSellLimitOrder(sell_price, correspondingBuyOrder)
                            if openedSellLimitOrder is None:
                                #If not enough base then delete corresponding buy limit order from the database
                                trade.cleanAllNotSatisfiedBuyOrders()
                            else:
                                #otherwise insert the sell limit order to database
                                openedSellLimitOrder.insert()
                        else:
                            #13. Get the curerent sell limit order status from Binance
                            openedSellLimitOrder = trade.updateLimitOrder(openedSellLimitOrder)
                            openedSellLimitOrder.update()
                            if openedSellLimitOrder._status == "FILLED":
                                continue

                            #PROBLEM getLowestNotSatisfiedOrder or correspondingBuyOrder
                            correspondingBuyOrder, sell_price = calculator.calculateSellPrice(trade.getNotSatisfiedOrder(False), trade._commission_ratio)
                            if sell_price == 0 or correspondingBuyOrder is None:
                                continue

                            if openedSellLimitOrder._price == sell_price:
                                wait(1)
                                settings.increaseWaitCounter()
                                continue

                            #17. Cancel the current sell limit order
                            openedSellLimitOrder = trade.cancelLimitOrder(openedSellLimitOrder)
                            if openedSellLimitOrder._status == "CANCELED" and openedSellLimitOrder._filled == 0:
                                #18. Delete the sell limit order from database
                                openedSellLimitOrder.delete()
                            else:
                                #19. Save sell limit order to database (status = FILLED, filled amount, profit based on filled)
                                openedSellLimitOrder._status = "FILLED"
                                openedSellLimitOrder.update()
        except Exception as err:
            with open("error.log", "a") as text_file:
                text_file.write(datetime.now().strftime("%d/%m/%y %H:%M:%S: ------------------------------"))
                text_file.write(traceback.format_exc())
                text_file.write(str(err) + "\n\n")
            wait(10)
    
    #clean up orders on exist
    order = trade.getOpenedBuyLimitOrder()
    if order is not None:
        trade.cancelLimitOrder(order)
        order.delete()
    order = trade.getOpenedSellLimitOrder()
    if order is not None:
        trade.cancelLimitOrder(order)
        order.delete()

if __name__ == "__main__":
    main()
