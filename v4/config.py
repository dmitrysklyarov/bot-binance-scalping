import configparser

def __getConfigParser():
    config = configparser.ConfigParser()
    return config.read('config.ini')

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

def getMinIndent():
    cp = __getConfigParser()
    return cp.getfloat(getBase(), 'min_indent')

def getMaxIndent():
    cp = __getConfigParser()
    return cp.getfloat(getBase(), 'max_indent')

def getProfit():
    cp = __getConfigParser()
    return cp.getfloat(getBase(), 'profit')