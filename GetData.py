import ccxt
import pandas as pd
import numpy as np
import asyncio
import time
from datetime import datetime
from Config import Configs

class Manage_data:
    def __init__(self):
        self.exchange = self._init_exchange()
        self.current_price = 0
        self.ohlcv_data = pd.DataFrame()
        
    def _init_exchange(self):
        exchange_class = getattr(ccxt, 'binance')
        exchange = exchange_class({
            'apiKey': Configs.API_KEY,
            'secret': Configs.SECRET_KEY,
            'sandbox': Configs.SANDBOX,
            'enableRateLimit': True,
        })
        return exchange      
    
    def fetch_ohlcv(self, limit =100):
        try:
            ohlcv = self.exchange.fetch_ohlcv(
                "BTC/USDT",
                "1h",
                limit =limit
            )
            df = pd.DataFrame(ohlcv,columns=['timestamp','open','high','low','close','volume'])
            df.set_index('timestamp', inplace=True)
            self.ohlcv_data = df
            self.current_price = df['close'].iloc[-1]
            return df
        except Exception as e:
            print(e)
            return None
    def get_current_price(self):
        try :
            ticker = self.exchange.fetch_ticker(Configs.SYMBOL)
            self.current_price = ticker['last']
            return self.current_price
        except Exception as e:
            print(f" problem in get_current_price {e}")
            return self.current_price
    def get_balance(self):
        try:
            balance = self.exchange.fetch_balance()
            return  balance['USDT']['free'] if 'USDT' in balance else Configs.INIT_BALANCE
        except Exception as e:
            print( f" problem in get_balance {e}")
            return Configs.INIT_BALANCE