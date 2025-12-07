import numpy as np 
import pandas as pd 
import talib

class Features:

    feature_list = [
        'price_change', 'price_change_5', 'pos_range_prc',
        'rsi', 'rsi_oversold', 'rsi_overbought',
        'price_above_smal_10', 'price_above_smal_20', 'sma_trend',
        'volume_high', 'high_volatility']
    def fet_Ext(self,df):
        df = df.copy()
        df['price_change'] =  df['close'].pct_change()#15 min change 
        df['price_change_5'] =  df['close'].pct_change(5)#change in 75 mins
        df['pos_range_prc'] = df['close']-df['low'].rolling(14).min()/df['high'].rolling(14).max()-df['low'].rolling(14).min()
        
        df['rsi'] = talib.RSI(df['close'].values,14)
        df['rsi_oversold'] = (df['rsi'] < 30).astype(int)# stock sold too much will rise
        df['rsi_overbought'] = (df['rsi'] > 80).astype(int)# stock bought too much will fall

        #moving AVGS
        df['smal_10'] = df['close'].rolling(10).mean()# Short term mean
        df['smal_20'] = df['close'].rolling(20).mean()# Long term mean
        df['price_above_smal_10'] = (df['close']>df['smal_10']).astype(int)
        df['price_above_smal_20'] = (df['close']>df['smal_20']).astype(int)
        df['sma_trend'] = (df['smal_10'] > df['smal_20']).astype(int)

        df['volume_avg'] = df['volume'].rolling(20).mean()
        df['volume_high'] = (df['volume'] > df['volume_avg'] * 1.5).astype(int)

        df['volatility'] = df['price_change'].rolling(10).std()
        df['high_volatility'] = (df['volatility'] > df['volatility'].rolling(50).mean()).astype(int)

        df['future_return'] = df['price_change'].shift(-1)
        df['target'] = np.where(df['future_return'] > 0.002, 1, 
                               np.where(df['future_return'] < -0.002, -1, 0))
        
        return df.fillna(0)





