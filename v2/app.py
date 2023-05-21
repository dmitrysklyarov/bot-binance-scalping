#pip install flask
#python3 -c "import flask; print(flask.__version__)"

#export FLASK_APP=web
#flask run

#gunicorn --workers 1 --bind 127.0.0.1:8000 wsgi:app

import DB
from flask import Flask
import json

app = Flask(__name__)

def addToFile(data):
    with open("data.txt", "a") as text_file:
        text_file.write(str(data) + "\n")

@app.route('/profit')
def profit():
    DB.i.curs.execute("SELECT sum(profit) FROM orders WHERE date > now() - interval '24 hour'")
    profit24 = DB.i.curs.fetchone()[0]
    addToFile(profit24)
    DB.i.curs.execute("SELECT sum(profit) FROM orders WHERE date > now() - interval '1 hour'")
    profit1 = DB.i.curs.fetchone()[0]
    addToFile(profit1)
    DB.i.curs.execute("SELECT now()")
    now = DB.i.curs.fetchone()[0]
    addToFile(now)
    DB.i.conn.commit()
    j = json.dumps({"profit24" : profit24, "profit1" : profit1})
    return j