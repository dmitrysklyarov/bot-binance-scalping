import sys
import time
import DB
import Config
from datetime import datetime

from Bot import Bot

base = 'ETH'
quote = 'USDT'
if len(sys.argv) > 2:
    base = sys.argv[1]
    quote = sys.argv[2]

restarted = True
bot: Bot

while True:
    try:
        Config.i.reloadConfig(base)
        if Config.i.exit:
            DB.i.conn.close()
            exit()
 
        if restarted:
            bot = Bot(base, quote)
            restarted = False

        bot.tryToSell()
        bot.tryToBuy()
                
        time.sleep(1)
        
    except Exception as err:
        try:
            DB.i.addLog("ERROR", err)
        except Exception as e:
            with open("error.txt", "a") as text_file:
                log = datetime.now().strftime('%H:%M:%S: ')
                log += str(err) + "\n"
                text_file.write(log)
        restarted = True
        time.sleep(10)