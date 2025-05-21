import yfinance as yf
from .models import CryptoPrice
from datetime import datetime
import pandas as pd

import matplotlib.pyplot as plt
import io


def fetch_and_store(symbol='BTC-USD', period='60d'):
    data = yf.download(symbol, period=period, interval='1d')
    for date, row in data.iterrows():
        CryptoPrice.objects.update_or_create(
            symbol=symbol.replace('-USD', ''),
            date=date.date(),
            defaults={
                'open_price': row['Open'],
                'high': row['High'],
                'low': row['Low'],
                'close': row['Close'],
                'volume': row['Volume'],
            }
        )


def plot_prediction(actual_prices, predicted_prices, symbol):
    plt.figure(figsize=(10, 6))
    plt.plot(range(len(actual_prices)), actual_prices, label='Actual Prices')
    plt.plot(range(len(actual_prices), len(actual_prices) + len(predicted_prices)), predicted_prices, label='Predicted Prices', linestyle='--')
    plt.title(f"{symbol} Narxlari: Haqiqiy va Bashorat")
    plt.xlabel('Kunlar')
    plt.ylabel('Narx')
    plt.legend()
    plt.grid(True)

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return buf
