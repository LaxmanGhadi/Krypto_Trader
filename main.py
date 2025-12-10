import asyncio
import time
import threading
from datetime import datetime
from GetData import Manage_data
# from strategy import TradingStrategy get model here
from Manage_orders import ExecutionEngine
from Logger import TradeLogger
from Visualizer import Visualizerr
from Config import Configs
import pickle
from FeatureExtract import Features
import pandas as pd


class CryptoTradingBot:
    def __init__(self):
        self.data_manager = Manage_data()
        self.execution_engine = ExecutionEngine()
        self.logger = TradeLogger()
        self.visualizer = Visualizerr()
        self.last_timestamp = None
        self.running = False
        self.Extractor = Features()
        self.feature_list  =[
        'price_change', 'price_change_5', 'pos_range_prc',
        'rsi', 'rsi_oversold', 'rsi_overbought',
        'price_above_smal_10', 'price_above_smal_20', 'sma_trend',
        'volume_high', 'high_volatility']
        self.position = None
        # self.test_df = df  # premade DataFrame
        with open("Weighted_model.pkl", "rb") as f:
            self.models = pickle.load(f)
        
    async def run_bot(self):
        """Main bot execution loop"""
        self.running = True
        
        print(f"Starting crypto trading bot for {Configs.SYMBOL}")
        print(f"Strategy: Random Forest ")
        print(f"Initial Balance: ${Configs.INIT_BALANCE}")
        print("-" * 50)
        
        while self.running:
            try:
                # Fetch latest data
                df = self.data_manager.fetch_ohlcv()
                df.index = pd.to_datetime(df.index , unit="ms")
                
                if df is None or len(df) < 50:
                    await asyncio.sleep(Configs.UPDATE_INTERVAL)
                    continue

                latest_ts = df.index[-1]

                if self.last_timestamp == latest_ts:
                    await asyncio.sleep(Configs.UPDATE_INTERVAL)
                    continue

                self.last_timestamp = latest_ts
                # Extract Features
                clean_df = df.dropna()
                Ext_Features = self.Extractor.fet_Ext(df=clean_df)
                feat_list  = self.Extractor.feature_list
                clean_df = Ext_Features[feat_list]

                #Get Model prediction
                
                self.signal  = self.models.predict(clean_df)                
                # # # Generate signal
                self.side = {-1:"sell",0:"hold",1:"buy"}
                
                # print(self.side[self.signal[0]])
                current_price = self.data_manager.current_price
                current_time = datetime.now()
                
                # Check exit conditions for existing position
                self.execution_engine.check_exit_conditions(current_price, current_time)
                
                # Execute new signal
                
                self.execution_engine.execute_signal(self.side[self.signal[0]], current_price, current_time)
                
                
                # Log completed trades
                if self.execution_engine.trades:
                    for trade in self.execution_engine.trades:
                        if trade not in [t for t in getattr(self, 'logged_trades', [])]:
                            self.logger.log_trade(trade)
                            if not hasattr(self, 'logged_trades'):
                                self.logged_trades = []
                            self.logged_trades.append(trade)
                
                # Display current status
                self.display_status(df, self.signal, current_price)
                
                # # Check if we have enough trades for metrics
                # if len(self.execution_engine.trades) >= Configs.MIN_TRADES_FOR_METRICS:
                #     metrics = self.logger.calculate_metrics(self.execution_engine.trades)
                #     print(f"\nCurrent Metrics:")
                #     print(f"Win Rate: {metrics['win_rate']:.1f}%")
                #     print(f"Total P&L: ${metrics['total_pnl']:.2f}")
                #     print(f"Trades: {metrics['total_trades']}")
                
                await asyncio.sleep(Configs.UPDATE_INTERVAL)
                
            except KeyboardInterrupt:
                print("\nBot stopped by user")
                break
            except Exception as e:
                print(f"Error in main loop: {e}")
                await asyncio.sleep(Configs.UPDATE_INTERVAL)
    
    def display_status(self, df, signal, price):
        """Display current bot status"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        rsi = df['rsi'].iloc[-1] if 'rsi' in df.columns else 0
        
        print(f"\n[{current_time}] Price: ${price:.2f} | RSI: {rsi:.1f} | Signal: {signal}")
        
        if self.execution_engine.position:
            pos = self.execution_engine.position
            unrealized_pnl = pos.calculate_pnl(price)
            print(f"Position: {pos.side.upper()} | Size: {pos.size:.4f} | Entry: ${pos.entry_price:.2f} | Unrealized P&L: ${unrealized_pnl:.2f}")
        
        print(f"Balance: ${self.execution_engine.balance:.2f} | Total Trades: {len(self.execution_engine.trades)}")
    
    def start_dashboard(self):
        """Start web dashboard in separate thread"""
        bot_ref = self
        def run_dash():
            # Setup callbacks for live updates
            @self.visualizer.app.callback(
                [Output('price-chart', 'figure'),
                 Output('equity-chart', 'figure'),
                 Output('metrics-display', 'children')],
                [Input('interval-component', 'n_intervals')]
            )
            def update_dashboard(n_intervals):
                # Get latest data

                print(f"Dashboard updating... iteration {n_intervals}") 
                
                df = bot_ref.current_df.copy() if hasattr(bot_ref, 'current_df') and bot_ref.current_df is not None else bot_ref.test_df.copy()
                df = bot_ref.Extractor.fet_Ext(df)
                
                # Create charts
                price_fig = self.visualizer.create_price_chart(
                    df, 
                    self.execution_engine.trades, 
                    df['close'].iloc[-1] if len(df) > 0 else 0
                )
                
                equity_fig = self.visualizer.create_equity_curve(
                    self.execution_engine.equity_curve
                )
                
                # Create metrics display
                if len(self.execution_engine.trades) > 0:
                    metrics = self.logger.calculate_metrics(self.execution_engine.trades)
                    metrics_div = html.Div([
                        html.H3("Performance Metrics"),
                        html.P(f"Win Rate: {metrics['win_rate']:.1f}%"),
                        html.P(f"Total P&L: ${metrics['total_pnl']:.2f}"),
                        html.P(f"Total Trades: {metrics['total_trades']}"),
                        html.P(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}"),
                        html.P(f"Max Drawdown: ${metrics['max_drawdown']:.2f}")
                    ])
                else:
                    metrics_div = html.Div([html.H3("Waiting for trades...")])
                
                return price_fig, equity_fig, metrics_div
            
            self.visualizer.app.run_server(debug=False, host='127.0.0.1', port=8050)
        
        dashboard_thread = threading.Thread(target=run_dash)
        dashboard_thread.daemon = True
        dashboard_thread.start()
        print("Dashboard started at http://127.0.0.1:8050")
    
    def stop(self):
        """Stop the trading bot"""
        self.running = False


if __name__ == "__main__":
    import os
    import numpy as np
    
    # Create bot instance
    bot = CryptoTradingBot()
    
    try:
        # Start dashboard
        bot.start_dashboard()
        
        # Wait a moment for dashboard to start
        time.sleep(2)
        
        # Run trading bot
        asyncio.run(bot.run_bot())
        
    except KeyboardInterrupt:
        print("\nShutting down bot...")
        bot.stop()