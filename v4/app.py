#pip install flask
#python3 -c "import flask; print(flask.__version__)"
#export FLASK_APP=web
#flask run

#nohup gunicorn --workers 1 wsgi:app &

import psycopg2
import conf
from flask import Flask, request
import json
from trade import Trade

app = Flask(__name__)

def getConnection():
    conn =  psycopg2.connect(database="botv4", host="127.0.0.1", port="5432", user="ubuntu", password=conf.getDBPassword())
    return conn

@app.route('/profit')
def profit():
    conn =  getConnection()
    curs = conn.cursor()

    curs.execute("SELECT sum(profit) FROM sell WHERE date > now() - interval '24 hour'")
    profit24 = round(float(curs.fetchone()[0]), 4)

    curs.execute("SELECT sum(profit) FROM sell WHERE date > now() - interval '7 day'")
    profit7 = round(float(curs.fetchone()[0]), 4)

    curs.execute("SELECT sum(profit) FROM sell WHERE date > now() - interval '30 day'")
    profit30 = round(float(curs.fetchone()[0]), 4)

    curs.execute("SELECT sum(profit) FROM sell WHERE date > now() - interval '1 hour'")
    profit1 = curs.fetchone()[0]
    if profit1 is None:
        profit1 = 0
    profit1 = round(float(profit1), 4)

    curs.execute("SELECT sum(quantity) FROM buy WHERE not satisfied")
    inorders = float(curs.fetchone()[0])

    curs.execute("SELECT price FROM buy WHERE not satisfied ORDER BY price DESC LIMIT 1")
    topprice = round(float(curs.fetchone()[0]))

    curs. execute('''SELECT price FROM 
                        (SELECT price, date FROM buy
                        UNION ALL
                        SELECT price, date FROM sell) AS combined_table
                    ORDER BY date DESC
                    LIMIT 1;''')
    currentprice = round(float(curs.fetchone()[0]))

    bottomprice = 0
    quote = 0
    base = 0
    with Trade() as trade:
        quote, base = trade.getQuantity((conf.getQuote(), conf.getBase()))
        quote = round(quote)
        base = round(base * currentprice)
        bottomprice = round(currentprice - conf.getIndent() *  quote / (conf.getQuantity() * currentprice))
        inorders = round(currentprice * inorders)

    conn.commit()
    curs.close()
    conn.close()

    j = json.dumps({"profit24" : profit24, 
                    "profit1" : profit1, 
                    "profit7" : profit7, 
                    "profit30" : profit30,
                    "inorders" : inorders,
                    "quote" : quote,
                    "base" : base,
                    "topprice" : topprice,
                    'currentprice' : currentprice,
                    'bottomprice' : bottomprice})
    return j

@app.route('/statistics')
def statistics():
    conn =  getConnection()
    curs = conn.cursor()

    curs.execute("SELECT sum(quantity) FROM buy WHERE not satisfied")
    baseInOrders = float(curs.fetchone()[0])
    
    curs.execute("SELECT price FROM buy WHERE not satisfied ORDER BY price DESC LIMIT 1")
    topPrice = round(float(curs.fetchone()[0]))

    curs. execute('''SELECT price FROM 
                        (SELECT price, date FROM buy
                        UNION ALL
                        SELECT price, date FROM sell) AS combined_table
                    ORDER BY date DESC
                    LIMIT 1;''')
    currentPrice = round(float(curs.fetchone()[0]))

    bottomPrice = 0
    quote = 0
    base = 0
    with Trade() as trade:
        quote, base = trade.getQuantity((conf.getQuote(), conf.getBase()))
        quote = round(quote)
        base = round(base * currentPrice)
        bottomPrice = round(currentPrice - conf.getIndent() *  quote / (conf.getQuantity() * currentPrice))
        baseInOrders = round(currentPrice * baseInOrders)

    j = json.dumps({"baseInOrders" : baseInOrders,
                        "quote" : quote,
                        "base" : base,
                        "topPrice" : topPrice,
                        "currentPrice" : currentPrice,
                        "bottomPrice" : bottomPrice,
                        "hourlyProfit" : getInterval('hour', 24, curs),
                        "dailyProfit" : getInterval('day', 30, curs),
                        "weeklyProfit" : getInterval('week', 30, curs)
                    })
    conn.commit()
    curs.close()
    conn.close()

    return j

def getInterval(duration, amount, curs):
    curs.execute(f'''SELECT
                        DATE_TRUNC('{duration}', date) as {duration},
                        sum(profit) as profit_summary
                    FROM 
                        sell 
                    WHERE 
                        date > now() - interval '{amount} {duration}'
                    GROUP BY
                        {duration}
                    ORDER BY
                        {duration} DESC
                    LIMIT {amount}
                    ''')
    data = curs.fetchall()
    if len(data) < amount:
        data.extend([[0,0]] * (amount - len(data)))
    return [row[1] for row in data]

@app.route('/orders')
def orders():
    conn =  getConnection()
    curs = conn.cursor()
    j = json.dumps({"lastOrders" : getLastOrders(curs)})
    conn.commit()
    curs.close()
    conn.close()
    return j

def getLastOrders(curs):
    curs.execute('''SELECT 'sell' as direction, date, quantity, price, profit FROM sell
                    WHERE status = 'FILLED'
                    UNION 
                    SELECT 'buy' as direction, date, quantity, price, profit FROM buy 
                    WHERE status = 'FILLED'
                    ORDER BY date DESC LIMIT 100''')
    data = curs.fetchall()
    dataArray = []
    for i in range(len(data)):
        dataArray.append({"direction":data[i][0], 
                          "time":data[i][1].strftime('%H:%M:%S'), 
                          "filled":data[i][2], 
                          "price":int(round(data[i][3], 0)),
                          "profit":data[i][4]})
    return dataArray
