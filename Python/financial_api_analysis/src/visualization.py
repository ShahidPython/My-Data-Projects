import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import logging
from config import settings

logger = logging.getLogger(__name__)
plt.style.use(settings.CHART_STYLE)

class FinancialVisualizer:
    def __init__(self):
        self.output_path = settings.OUTPUT_CHARTS
        self.color_palette = settings.COLOR_PALETTE
        
    def create_price_trend_chart(self, df, symbol):
        try:
            symbol_data = df[df['symbol'] == symbol].copy()
            if symbol_data.empty:
                return None
            
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=settings.FIG_SIZE, 
                                          gridspec_kw={'height_ratios': [3, 1]})
            
            ax1.plot(symbol_data['date'], symbol_data['Close'], 
                    label='Close Price', linewidth=2, color=self.color_palette[0])
            ax1.plot(symbol_data['date'], symbol_data['ma_20'], 
                    label='20-Day MA', linewidth=1.5, color=self.color_palette[1], alpha=0.7)
            ax1.plot(symbol_data['date'], symbol_data['ma_50'], 
                    label='50-Day MA', linewidth=1.5, color=self.color_palette[2], alpha=0.7)
            
            ax1.set_title(f'{symbol} Price Analysis', fontsize=14, fontweight='bold')
            ax1.set_ylabel('Price (USD)', fontsize=10)
            ax1.legend(loc='upper left')
            ax1.grid(True, alpha=0.3)
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            
            ax2.bar(symbol_data['date'], symbol_data['Volume'], 
                   color=self.color_palette[3], alpha=0.6, width=0.8)
            ax2.set_ylabel('Volume', fontsize=10)
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            filename = self.output_path / f"price_trend_{symbol}_{datetime.now().strftime('%Y%m%d')}.png"
            plt.savefig(filename, dpi=settings.DPI, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Created price trend chart for {symbol}")
            return filename
            
        except Exception as e:
            logger.error(f"Error creating price chart for {symbol}: {str(e)}")
            return None
    
    def create_correlation_heatmap(self, df):
        try:
            pivot_data = df.pivot_table(index='date', columns='symbol', values='Close')
            returns_data = pivot_data.pct_change().dropna()
            correlation_matrix = returns_data.corr()
            
            mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))
            
            plt.figure(figsize=(8, 6))
            sns.heatmap(correlation_matrix, annot=True, fmt='.2f', cmap='coolwarm',
                       mask=mask, center=0, square=True, linewidths=1,
                       cbar_kws={'shrink': 0.8})
            
            plt.title('Equity Returns Correlation Matrix', fontsize=14, fontweight='bold')
            plt.tight_layout()
            
            filename = self.output_path / f"correlation_heatmap_{datetime.now().strftime('%Y%m%d')}.png"
            plt.savefig(filename, dpi=settings.DPI, bbox_inches='tight')
            plt.close()
            
            logger.info("Created correlation heatmap")
            return filename
            
        except Exception as e:
            logger.error(f"Error creating correlation heatmap: {str(e)}")
            return None
    
    def create_macro_economic_chart(self, df):
        try:
            unique_series = df['series_id'].unique()
            
            fig, axes = plt.subplots(len(unique_series), 1, 
                                    figsize=(settings.FIG_SIZE[0], 3*len(unique_series)),
                                    squeeze=False)
            
            for idx, series_id in enumerate(unique_series):
                series_data = df[df['series_id'] == series_id]
                series_name = series_data['series_name'].iloc[0]
                
                monthly_avg = series_data.groupby(pd.Grouper(key='date', freq='ME'))['series_value'].mean()
                
                axes[idx, 0].plot(monthly_avg.index, monthly_avg.values, 
                                 marker='o', linewidth=2, color=self.color_palette[idx % len(self.color_palette)])
                axes[idx, 0].set_title(f'{series_name} ({series_id})', fontsize=12, fontweight='bold')
                axes[idx, 0].set_ylabel('Value', fontsize=9)
                axes[idx, 0].grid(True, alpha=0.3)
                axes[idx, 0].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            
            plt.tight_layout()
            
            filename = self.output_path / f"macro_economic_{datetime.now().strftime('%Y%m%d')}.png"
            plt.savefig(filename, dpi=settings.DPI, bbox_inches='tight')
            plt.close()
            
            logger.info("Created macroeconomic chart")
            return filename
            
        except Exception as e:
            logger.error(f"Error creating macroeconomic chart: {str(e)}")
            return None
    
    def create_volatility_comparison(self, df):
        try:
            volatility_data = df.groupby('symbol')['volatility'].mean().sort_values(ascending=False)
            
            plt.figure(figsize=(10, 6))
            bars = plt.bar(volatility_data.index, volatility_data.values * 100,
                          color=self.color_palette[:len(volatility_data)])
            
            plt.axhline(y=volatility_data.mean() * 100, color='red', 
                       linestyle='--', linewidth=1.5, alpha=0.7, label='Average Volatility')
            
            for bar, value in zip(bars, volatility_data.values * 100):
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                        f'{value:.1f}%', ha='center', va='bottom', fontsize=9)
            
            plt.title('Annualized Volatility Comparison (%)', fontsize=14, fontweight='bold')
            plt.ylabel('Volatility (%)', fontsize=10)
            plt.legend()
            plt.grid(True, alpha=0.3, axis='y')
            
            filename = self.output_path / f"volatility_comparison_{datetime.now().strftime('%Y%m%d')}.png"
            plt.savefig(filename, dpi=settings.DPI, bbox_inches='tight')
            plt.close()
            
            logger.info("Created volatility comparison chart")
            return filename
            
        except Exception as e:
            logger.error(f"Error creating volatility chart: {str(e)}")
            return None
    
    def generate_all_visualizations(self, df):
        chart_paths = {}
        
        for symbol in df['symbol'].unique():
            chart_path = self.create_price_trend_chart(df, symbol)
            if chart_path:
                chart_paths[f'price_trend_{symbol}'] = chart_path
        
        chart_paths['correlation_heatmap'] = self.create_correlation_heatmap(df)
        chart_paths['macro_economic'] = self.create_macro_economic_chart(df)
        chart_paths['volatility_comparison'] = self.create_volatility_comparison(df)
        
        return {k: v for k, v in chart_paths.items() if v is not None}