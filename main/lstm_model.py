import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler
from .models import CryptoPrice
import pandas as pd


def train_and_predict(symbol='BTC', look_back=30, predict_days=5):
    df = pd.DataFrame(list(CryptoPrice.objects.filter(symbol=symbol).order_by('date').values()))
    close_prices = df['close'].values.reshape(-1, 1)

    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(close_prices)

    X, y = [], []
    for i in range(look_back, len(scaled_data) - predict_days):
        X.append(scaled_data[i - look_back:i])
        y.append(scaled_data[i:i+predict_days])

    X, y = np.array(X), np.array(y)

    model = Sequential()
    model.add(LSTM(units=50, return_sequences=True, input_shape=(X.shape[1], 1)))
    model.add(LSTM(units=50))
    model.add(Dense(predict_days))
    model.compile(loss='mean_squared_error', optimizer='adam')
    model.fit(X, y, epochs=30, batch_size=32, verbose=0)

    recent_data = scaled_data[-look_back:]
    recent_data = np.reshape(recent_data, (1, look_back, 1))
    prediction = model.predict(recent_data)

    predicted_prices = scaler.inverse_transform(prediction).flatten()
    return predicted_prices.tolist()
