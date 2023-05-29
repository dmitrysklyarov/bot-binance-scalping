#pip install flask
#python3 -c "import flask; print(flask.__version__)"
#export FLASK_APP=web
#flask run

#nohup gunicorn --workers 1 wsgi:app &

import psycopg2
import config
from flask import Flask
import json

app = Flask(__name__)

@app.route('/profit')
def profit():
    conn =  psycopg2.connect(database="botv4", host="127.0.0.1", port="5432", user="ubuntu", password=config.getDBPassword())
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
    quantity = round(float(curs.fetchone()[0]), 4)

    conn.commit()
    curs.close()
    conn.close()

    j = json.dumps({"profit24" : profit24, 
                    "profit1" : profit1, 
                    "profit7" : profit7, 
                    "profit30" : profit30,
                    "quantity" : quantity})
    return j