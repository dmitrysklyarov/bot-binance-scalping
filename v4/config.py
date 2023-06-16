import configparser
import settings

def __getValue(section, option, type):
    cp = configparser.ConfigParser()
    cp.read('main.conf')
    return type(cp.get(section, option))

def getBase():
    return __getValue('MAIN', 'base', str)

def getQuote():
    return __getValue('MAIN', 'quote', str)

def getWait():
    return __getValue('MAIN', 'wait', int)

def getSymbol():
    return getBase() + getQuote()

def getQuantity():
    return __getValue(getBase(), 'quantity', float)

def getCommission():
    return __getValue(getBase(), 'commission', float)

def getStep():
    return __getValue(getBase(), 'step', float)

def getIndent():
    indent = __getValue(getBase(), 'indent', float)
    #indent = indent - settings.waitCounter / getWait() * getStep()
    #indent = indent if indent > getMinIndent() else getMinIndent()
    return indent

def getMinIndent():
    return __getValue(getBase(), 'min_indent', float)

def getMaxIndent():
    return __getValue(getBase(), 'max_indent', float)

def getProfit():
    return __getValue(getBase(), 'profit', float)

def getMinProfit():
    return __getValue(getBase(), 'min_profit', float)

def getMaxProfit():
    return __getValue(getBase(), 'max_profit', float)

def __getSecretValue(section, option, type):
    cp = configparser.ConfigParser()
    cp.read('secret.conf')
    return type(cp.get(section, option))

def getDBPassword():
    return __getSecretValue('database', 'password', str)

def getAPIKey():
    return __getSecretValue('binance', 'API_KEY', str)

def getAPISecret():
    return __getSecretValue('binance', 'API_SECRET', str)
