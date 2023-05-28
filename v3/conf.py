import configparser
import os

def __getConfigParser():
    cp = configparser.ConfigParser()
    cp.read("trade.conf")
    print(os.getcwd())
    return cp

def isContinue():
    cp = __getConfigParser()
    return cp.getboolean('MAIN', 'continue')

def getBase():
    cp = __getConfigParser()
    return cp.get('MAIN', 'base')

def getQuote():
    cp = __getConfigParser()
    return cp.get('MAIN', 'quote')

def getSymbol():
    return getBase() + getQuote()

def getQuantity():
    cp = __getConfigParser()
    return cp.getfloat(getBase(), 'quantity')

def getIndent():
    cp = __getConfigParser()
    return cp.getfloat(getBase(), 'indent')

def getProfit():
    cp = __getConfigParser()
    return cp.getfloat(getBase(), 'profit')
