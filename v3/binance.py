#https://bablofil.com/binance-api/
#https://binance-docs.github.io/apidocs/spot/en/
#https://binance-docs.github.io/apidocs/spot/en/#market-data-endpoints

import ssl
import time
import json
import urllib
import hmac, hashlib
import requests

from urllib.parse import urlparse, urlencode
from urllib.request import Request, urlopen

class Binance():

    methods = {
            # public methods
            'ping':             {'url':'api/v3/ping', 'method': 'GET', 'private': False},#getPing
            'time':             {'url':'api/v3/time', 'method': 'GET', 'private': False},#getTime
            'exchangeInfo':     {'url':'api/v3/exchangeInfo', 'method': 'GET', 'private': False},#getExchangeInfo
            'depth':            {'url': 'api/v3/depth', 'method': 'GET', 'private': False},#getMarketPrice
            'trades':           {'url': 'api/v3/trades', 'method': 'GET', 'private': False},#getTrades
            'historicalTrades': {'url': 'api/v3/historicalTrades', 'method': 'GET', 'private': False},#doesn't work
            'aggTrades':        {'url': 'api/v3/aggTrades', 'method': 'GET', 'private': False},#don't need
            'klines':           {'url': 'api/v3/klines', 'method': 'GET', 'private': False},
            'ticker24hr':       {'url': 'api/v3/ticker/24hr', 'method': 'GET', 'private': False},
            'tickerPrice':      {'url': 'api/v3/ticker/price', 'method': 'GET', 'private': False},#getTicketPrice
            'tickerBookTicker': {'url': 'api/v3/ticker/bookTicker', 'method': 'GET', 'private': False},
            # private methods
            'createOrder':      {'url': 'api/v3/order', 'method': 'POST', 'private': True},#placeBuyOrder, placeSellOrder
            'testOrder':        {'url': 'api/v3/order/test', 'method': 'POST', 'private': True},
            'orderInfo':        {'url': 'api/v3/order', 'method': 'GET', 'private': True},
            'cancelOrder':      {'url': 'api/v3/order', 'method': 'DELETE', 'private': True},
            'openOrders':       {'url': 'api/v3/openOrders', 'method': 'GET', 'private': True},
            'allOrders':        {'url': 'api/v3/allOrders', 'method': 'GET', 'private': True},
            'account':          {'url': 'api/v3/account', 'method': 'GET', 'private': True},
            'myTrades':         {'url': 'api/v3/myTrades', 'method': 'GET', 'private': True},
            # wapi
            'depositAddress':   {'url': 'wapi/v3/depositAddress.html', 'method':'GET', 'private':True},
            'withdraw':         {'url': 'wapi/v3/withdraw.html', 'method':'POST', 'private':True},
            'depositHistory':   {'url': 'wapi/v3/depositHistory.html', 'method':'GET', 'private':True},
            'withdrawHistory':  {'url': 'wapi/v3/withdrawHistory.html', 'method':'GET', 'private':True},
            'assetDetail':      {'url': 'wapi/v3/assetDetail.html', 'method':'GET', 'private':True},
            'tradeFee':         {'url': 'wapi/v3/tradeFee.html', 'method':'GET', 'private':True},
            'accountStatus':    {'url': 'wapi/v3/accountStatus.html', 'method':'GET', 'private':True},
            'systemStatus':     {'url': 'wapi/v3/systemStatus.html', 'method':'GET', 'private':True},
            'assetDust':        {'url': 'sapi/v1/asset/dust', 'method':'POST', 'private':True},
            'dustLog':          {'url': 'wapi/v3/userAssetDribbletLog.html', 'method':'GET', 'private':True},
            'assetAssetDividend': {'url': 'sapi/v1/asset/assetDividend', 'method':'GET', 'private':True},
            #sapi
            'marginTransfer':   {'url': 'sapi/v1/margin/transfer', 'method': 'POST', 'private':True},
            'marginLoan':       {'url': 'sapi/v1/margin/loan', 'method': 'POST', 'private': True},
            'marginLoanGet':    {'url': 'sapi/v1/margin/loan', 'method': 'GET', 'private': True},
            'marginRepay':      {'url': 'sapi/v1/margin/repay', 'method': 'POST', 'private': True},
            'marginRepayGet':   {'url': 'sapi/v1/margin/repay', 'method': 'GET', 'private': True},
            'marginCreateOrder': {'url': 'sapi/v1/margin/order', 'method': 'POST', 'private':True},
            'marginCancelOrder': {'url': 'sapi/v1/margin/order', 'method': 'DELETE', 'private':True},
            'marginOrderInfo':  {'url': 'sapi/v1/margin/order', 'method': 'GET', 'private':True},
            'marginAccount':    {'url': 'sapi/v1/margin/account', 'method': 'POST', 'private':True},
            'marginOpenOrders': {'url': 'sapi/v1/margin/openOrders', 'method': 'GET', 'private':True},
            'marginAllOrders':  {'url': 'sapi/v1/margin/allOrders', 'method': 'GET', 'private':True},
            'marginAsset':      {'url': 'sapi/v1/margin/asset', 'method': 'POST', 'private':True},
            'marginPair':       {'url': 'sapi/v1/margin/pair', 'method': 'POST', 'private':True},
            'marginPriceIndex': {'url': 'sapi/v1/margin/priceIndex', 'method': 'POST', 'private':True},
            'marginMyTrades':   {'url': 'sapi/v1/margin/myTrades', 'method': 'GET', 'private':True},
            'marginMaxBorrowable': {'url': 'sapi/v1/margin/maxBorrowable', 'method': 'GET', 'private':True},
            'marginmaxTransferable': {'url': 'sapi/v1/margin/maxTransferable', 'method': 'GET', 'private':True},
            #futures
            'futuresExchangeInfo':      {'url': 'fapi/v1/exchangeInfo', 'method': 'GET', 'private': False, 'futures': True},
            'futuresKlines':            {'url': 'fapi/v1/klines', 'method': 'GET', 'private': False, 'futures': True},
            'futuresCreateOrder':       {'url': 'fapi/v1/order', 'method': 'POST', 'private': True, 'futures': True},
            'futuresAccount':           {'url': 'fapi/v1/account', 'method': 'POST', 'private': True, 'futures': True},
            'futuresBalance':           {'url': 'fapi/v1/balance', 'method': 'GET', 'private': True, 'futures': True},
            'futuresSymbolPriceTicker': {'url': 'fapi/v1/ticker/price', 'method': 'GET', 'private': True, 'futures': True},
            'futuresOrderInfo':         {'url': 'fapi/v1/order', 'method': 'GET', 'private': True, 'futures': True},
            'futuresCancelOrder':       {'url': 'fapi/v1/order', 'method': 'DELETE', 'private': True, 'futures': True},
   }
    
    def __init__(self, API_KEY, API_SECRET):
        self.API_KEY = API_KEY
        self.API_SECRET = bytearray(API_SECRET, encoding='utf-8')
        self.shift_seconds = 0

    def __getattr__(self, name):
        def wrapper(*args, **kwargs):
            kwargs.update(command=name)
            return self.call_api(**kwargs)
        return wrapper

    def set_shift_seconds(self, seconds):
        self.shift_seconds = seconds
        
    def call_api(self, **kwargs):

        command = kwargs.pop('command')

        base_url = 'https://api.binance.com/'
        #base_url = 'https://testnet.binance.vision/'
        
        if self.methods[command].get('futures'):
            base_url = 'https://fapi.binance.com/' 
        api_url = base_url  + self.methods[command]['url']

        payload = kwargs
        headers = {}
        
        payload_str = urllib.parse.urlencode(payload)
        if self.methods[command]['private']:
            payload.update({'timestamp': int(time.time() + self.shift_seconds) * 1000})
            payload_str = urllib.parse.urlencode(payload).encode('utf-8')
            sign = hmac.new(
                key=self.API_SECRET,
                msg=payload_str,
                digestmod=hashlib.sha256
            ).hexdigest()

            payload_str = payload_str.decode("utf-8") + "&signature="+str(sign) 
            headers = {"X-MBX-APIKEY": self.API_KEY, "Content-Type":"application/x-www-form-urlencoded"}

        if self.methods[command]['method'] == 'GET' or self.methods[command]['url'].startswith('sapi'):
            api_url += '?' + payload_str

        response = requests.request(method=self.methods[command]['method'], url=api_url, data="" if self.methods[command]['method'] == 'GET' else payload_str, headers=headers)
            
        if 'code' in response.text:
            raise Exception(response.text)

        return response.json()