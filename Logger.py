import pandas as pd
import sqlite3
import json
from datetime import datetime
from Config import Configs
import os 
import numpy as np

class TradeLogger:
    def __init__(self):
        self.trades_df = pd.DataFrame()
        self.init_database()
        
    def init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(Configs.DB_FILE)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY,
                side TEXT,
                entry_price REAL,
                exit_price REAL,
                size REAL,
                entry_time TEXT,
                exit_time TEXT,
                pnl REAL,
                status TEXT,
                stop_loss REAL,
                take_profit REAL
            )
        ''')
        conn.close()
    
    def log_trade(self, trade):
        """Log completed trade"""
        trade_data = {
            'side': trade.side,
            'entry_price': trade.entry_price,
            'exit_price': trade.exit_price,
            'size': trade.size,
            'entry_time': trade.entry_time.isoformat(),
            'exit_time': trade.exit_time.isoformat() if trade.exit_time else None,
            'pnl': trade.pnl,
            'status': trade.status.value,
            'stop_loss': trade.stop_loss,
            'take_profit': trade.take_profit
        }
        
        # Save to CSV
        df = pd.DataFrame([trade_data])
        if not os.path.exists(Configs.LOG_FILE):
            df.to_csv(Configs.LOG_FILE, index=False)
        else:
            df.to_csv(Configs.LOG_FILE, mode='a', header=False, index=False)
        
        # Save to database
        conn = sqlite3.connect(Configs.DB_FILE)
        df.to_sql('trades', conn, if_exists='append', index=False)
        conn.close()
        
        print(f"Trade logged: {trade.side} | P&L: ${trade.pnl:.2f}")
    
    def calculate_metrics(self, trades):
        """Calculate trading performance metrics"""
        if len(trades) == 0:
            return {}
            
        pnls = [t.pnl for t in trades]
        wins = [p for p in pnls if p > 0]
        
        metrics = {
            'total_trades': len(trades),
            'winning_trades': len(wins),
            'win_rate': len(wins) / len(trades) * 100,
            'total_pnl': sum(pnls),
            'avg_win': np.mean(wins) if wins else 0,
            'avg_loss': np.mean([p for p in pnls if p < 0]) if any(p < 0 for p in pnls) else 0,
            'profit_factor': sum(wins) / abs(sum([p for p in pnls if p < 0])) if any(p < 0 for p in pnls) else float('inf'),
            'sharpe_ratio': np.mean(pnls) / np.std(pnls) if np.std(pnls) != 0 else 0,
            'max_drawdown': self._calculate_max_drawdown(pnls)
        }
        
        return metrics
    
    def _calculate_max_drawdown(self, pnls):
        """Calculate maximum drawdown"""
        cumulative = np.cumsum(pnls)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = cumulative - running_max
        return abs(min(drawdown)) if len(drawdown) > 0 else 0