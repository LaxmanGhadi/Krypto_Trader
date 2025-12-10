import pandas as pd
import numpy as np
import talib

from Config import Configs

class TradingStrategy:
    def __init__(self):
        self.name = "Strategy"
        self.signal = []
    
    def calculate_indicator(self,df):
        # if len(df)<max(Configur.RSI_PERIOD,Configur.EMA_LONG):
        #     return df
        df['rsi'] =  talib.RSI(df['close'].values, timeperiod=Configs.RSI_PERIOD)
        # EMAs
        df['ema_short'] = talib.EMA(df['close'].values, timeperiod=Configs.EMA_SHORT)
        df['ema_long'] = talib.EMA(df['close'].values, timeperiod=Configs.EMA_LONG)
        
        # Additional indicators
        df['bb_upper'], df['bb_middle'], df['bb_lower'] = talib.BBANDS(
            df['close'].values, timeperiod=20, nbdevup=2, nbdevdn=2
        )
        
        return df
    def buy_sell(self,df):
        if len(df)<2:
            return 'hold'
        current  =df.iloc[-1]
        previous =df.iloc[-2]

        # Buy conditions
        buy_conditions = [
            current['rsi'] < Configs.RSI_OVERSOLD,  # RSI oversold
            current['ema_short'] > current['ema_long'],  # Uptrend
            current['close'] > current['bb_lower'],  # Above lower BB
            previous['rsi'] >= Configs.RSI_OVERSOLD  # RSI was higher before
        ]
        
        # Sell conditions
        sell_conditions = [
            current['rsi'] > Configs.RSI_OVERBOUGHT,  # RSI overbought
            current['ema_short'] < current['ema_long'],  # Downtrend
            current['close'] < current['bb_upper'],  # Below upper BB
            previous['rsi'] <= Configs.RSI_OVERBOUGHT  # RSI was lower before
        ]
        
        if all(buy_conditions):
            return 'buy'
        elif all(sell_conditions):
            return 'sell'
        else:
            return 'hold'
