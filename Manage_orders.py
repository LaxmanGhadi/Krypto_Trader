import time
from datetime import datetime
from enum import Enum
from GetData import Manage_data
from Config import Configs

class OrderStatus(Enum):
    PENDING = "pending"
    FILLED  = "filled"
    CANCELLED   = "cancelled"

class Trade :
    def __init__(self,side,entry_price,size,timestamp):
        self.side  =  side
        self.entry_price= entry_price
        self.exit_price = None
        self.size = size
        self.entry_time  = timestamp
        self.exit_time = None
        self.pnl = 0
        self.status= OrderStatus.PENDING
        self.stop_loss = None
        self.take_profit = None

    def set_exit_levels(self):
        if self.side =='buy':
            self.stop_loss = self.entry_price * (1-Configs.STOP_LOSS_PCT)
            self.take_profit  = self.entry_price *(1+Configs.TAKE_PROFIT_PCT)
        else:
            self.stop_loss = self.entry_price * (1+Configs.STOP_LOSS_PCT)
            self.take_profit  = self.entry_price *(1-Configs.TAKE_PROFIT_PCT)

    def calculate_pnl(self,exit_price):
        if self.side  == 'buy':
            self.pnl = (exit_price - self.entry_price)*self.size
        else :
            self.pnl = (self.entry_price - exit_price)*self.size
        return self.pnl
    


class ExecutionEngine:
    def __init__(self):
        self.data_manager = Manage_data
        self.balance  = Configs.INIT_BALANCE
        self.position = None
        self.trades  = []
        self.equity_curve = [Configs.INIT_BALANCE]
    
    def execute_signal(self,signal,price,timestamp):
        if signal == 'hold':
            return None
        
        if self.position and signal != self.position.side:
            self.close_position(price, timestamp)

        
        if not self.position and signal in ['buy', 'sell']:
            return self.open_position(signal, price, timestamp)
        
        return None
    
    def calculate_position_size(self, balance, price):
        """Calculate position size based on risk management"""
        risk_amount = balance * Configs.RISK_PER_TRADE
        position_size = risk_amount / (price * Configs.STOP_LOSS_PCT)
        return min(position_size, balance * 0.95 / price)  # Max 95% of balance

    def open_position(self, side, price, timestamp):
        """Open a new position"""
        # from strategy import TradingStrategy
        # strategy = TradingStrategy()
        size = self.calculate_position_size(self.balance, price)
        if size * price < 10:  # Minimum order size
            return None
            
        trade = Trade(side, price, size, timestamp)
        trade.set_exit_levels()
        self.position = trade
        
        print(f"OPENED {side.upper()} position: {size:.4f} @ ${price:.2f}")
        return trade
    
    def close_position(self, price, timestamp, reason="signal"):
        """Close current position"""
        if not self.position:
            return None
            
        self.position.exit_price = price
        self.position.exit_time = timestamp
        self.position.status = OrderStatus.FILLED
        
        pnl = self.position.calculate_pnl(price)
        self.balance += pnl
        self.equity_curve.append(self.balance)
        
        self.trades.append(self.position)
        
        print(f"CLOSED {self.position.side.upper()} position: @ ${price:.2f} | P&L: ${pnl:.2f} | Reason: {reason}")
        
        closed_trade = self.position
        self.position = None
        return closed_trade
    
    def check_exit_conditions(self, current_price, timestamp):
        """Check stop loss and take profit conditions"""
        if not self.position:
            return
            
        if self.position.side == 'buy':
            if current_price <= self.position.stop_loss:
                self.close_position(current_price, timestamp, "stop_loss")
            elif current_price >= self.position.take_profit:
                self.close_position(current_price, timestamp, "take_profit")
        else:  # sell
            if current_price >= self.position.stop_loss:
                self.close_position(current_price, timestamp, "stop_loss")
            elif current_price <= self.position.take_profit:
                self.close_position(current_price, timestamp, "take_profit")



