
import os
from dotenv import load_dotenv

load_dotenv()
class Configs:
    EXCHANGE  = "binance"
    SYMBOL = "BTC/USDT"
    TIMEFRAME = "1h"


    API_KEY = ""
    SECRET_KEY = ""
    SANDBOX = True

    INIT_BALANCE = 10000
    RISK_PER_TRADE = 0.01
    STOP_LOSS_PCT  = 0.02
    TAKE_PROFIT_PCT  = 0.04
    # Strategy Parameters
    RSI_PERIOD = 14
    RSI_OVERSOLD = 30
    RSI_OVERBOUGHT = 70
    EMA_SHORT = 20
    EMA_LONG = 50
    RISK_PER_TRADE = 0.01
    # Execution Settings
    MIN_TRADES_FOR_METRICS = 50
    UPDATE_INTERVAL = 60  # seconds
    

    # For model training
    MIN_DATA_POINTS = 300
    LOOKBACK_DAYS = 7
    # RETRAIN_HOURS = 6

    # Logging
    LOG_FILE = 'trades.csv'
    DB_FILE = 'trading_bot.db'

