import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import dash
from dash import dcc, html, Input, Output
import threading
from Config import Configs
class Visualizerr:
    def __init__(self):
        self.app = dash.Dash(__name__)
        self.setup_layout()
        
    def create_price_chart(self, df, trades, current_price):
        """Create price chart with trade markers"""
        df = df
        print("Visualizer got df columns:", df.columns)
        print("Shape:", df.shape)
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            subplot_titles=('Price Chart', 'RSI'),
            row_width=[0.7, 0.3]
        )
        
        # Candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name='Price'
            ),
            row=1, col=1
        )
        
        # EMAs
        if 'ema_short' in df.columns:
            fig.add_trace(
                go.Scatter(x=df.index, y=df['ema_short'], name='EMA 20', line=dict(color='orange')),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(x=df.index, y=df['ema_long'], name='EMA 50', line=dict(color='blue')),
                row=1, col=1
            )
        
        # Trade markers
        for trade in trades:
            if trade.exit_time:
                # Entry marker
                fig.add_trace(
                    go.Scatter(
                        x=[trade.entry_time],
                        y=[trade.entry_price],
                        mode='markers',
                        marker=dict(
                            symbol='triangle-up' if trade.side == 'buy' else 'triangle-down',
                            size=15,
                            color='green' if trade.side == 'buy' else 'red'
                        ),
                        name=f'{trade.side.upper()} Entry',
                        showlegend=False
                    ),
                    row=1, col=1
                )
                
                # Exit marker
                fig.add_trace(
                    go.Scatter(
                        x=[trade.exit_time],
                        y=[trade.exit_price],
                        mode='markers',
                        marker=dict(
                            symbol='x',
                            size=12,
                            color='green' if trade.pnl > 0 else 'red'
                        ),
                        name=f'Exit (${trade.pnl:.2f})',
                        showlegend=False
                    ),
                    row=1, col=1
                )
        
        # RSI
        if 'rsi' in df.columns:
            fig.add_trace(
                go.Scatter(x=df.index, y=df['rsi'], name='RSI', line=dict(color='purple')),
                row=2, col=1
            )
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
        
        fig.update_layout(
            title=f'{Configs.SYMBOL} - Live Trading Bot',
            xaxis_rangeslider_visible=False,
            height=800
        )
        
        return fig
    
    def create_equity_curve(self, equity_curve):
        """Create equity curve chart"""
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                y=equity_curve,
                mode='lines',
                name='Portfolio Value',
                line=dict(color='blue', width=2)
            )
        )
        
        fig.update_layout(
            title='Portfolio Equity Curve',
            xaxis_title='Trade Number',
            yaxis_title='Portfolio Value (USDT)',
            height=400
        )
        
        return fig
    
    def setup_layout(self):
        """Setup Dash app layout"""
        self.app.layout = html.Div([
            html.H1("Crypto Trading Bot Dashboard", style={'textAlign': 'center'}),
            
            html.Div([
                html.Div(id='metrics-display'),
                dcc.Graph(id='price-chart'),
                dcc.Graph(id='equity-chart'),
                dcc.Interval(
                    id='interval-component',
                    interval=5000,  # Update every 5 seconds
                    n_intervals=0
                )
            ])
        ])