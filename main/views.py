from rest_framework.response import Response
from collections import defaultdict

from django.http import HttpResponse
from .lstm_model import train_and_predict
from .models import CryptoPrice
from .utils import plot_prediction
import pandas as pd

from rest_framework.views import APIView


class CryptoPredictionView(APIView):
    def get(self, request):
        symbol = request.GET.get('symbol', 'BTC')

        df = pd.DataFrame(list(CryptoPrice.objects.filter(symbol=symbol).order_by('date').values()))
        last_date = pd.to_datetime(df['date'].max())
        print(f"{last_date} date time")

        predict_days = 5
        predicted_prices = train_and_predict(symbol=symbol, look_back=30, predict_days=predict_days)

        predict_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=predict_days)

        predicted_with_dates = [
            {"date": date.strftime('%Y-%m-%d'), "price": round(price, 2)}
            for date, price in zip(predict_dates, predicted_prices)
        ]

        return Response({
            "symbol": symbol,
            "predicted": predicted_with_dates
        })


class CryptoPredictionDataView(APIView):
    def get(self, request):
        symbol = request.GET.get('symbol', 'BTC')
        look_back = 30
        predict_days = int(request.GET.get('days', 15))

        df = pd.DataFrame(list(CryptoPrice.objects.filter(symbol=symbol).order_by('date').values()))
        if df.empty:
            return Response({"error": f"No data found for symbol {symbol}"}, status=404)

        df['date'] = pd.to_datetime(df['date'])
        actual_data = df.tail(look_back)
        actual_prices = actual_data['close'].tolist()
        actual_dates = actual_data['date'].dt.strftime('%Y-%m-%d').tolist()

        predicted_prices = train_and_predict(symbol=symbol, look_back=look_back, predict_days=predict_days)
        last_date = pd.to_datetime(df['date'].max())
        predicted_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=predict_days)
        predicted_dates = predicted_dates.strftime('%Y-%m-%d').tolist()

        result = {
            "symbol": symbol,
            "actual": [
                {"date": date, "price": round(price, 6)}
                for date, price in zip(actual_dates, actual_prices)
            ],
            "predicted": [
                {"date": date, "price": round(price, 6)}
                for date, price in zip(predicted_dates, predicted_prices)
            ]
        }

        return Response(result)


class CryptoPricesByDateView(APIView):
    def get(self, request):
        prices = CryptoPrice.objects.all().order_by('date', 'symbol').values('date', 'symbol', 'open_price')

        data_by_date = defaultdict(list)

        for entry in prices:
            date_str = entry['date'].strftime('%Y-%m-%d')
            data_by_date[date_str].append({entry['symbol']: entry['open_price']})

        result = []
        for date, amounts in data_by_date.items():
            result.append({
                "date": date,
                "amounts": amounts
            })

        return Response(result)


class PortfolioSimulationView(APIView):
    def get(self, request):
        symbol = request.GET.get('symbol', 'BTC')
        amount = float(request.GET.get('initial_amount', 100))
        days = int(request.GET.get('days', 5))
        look_back = 30

        df = pd.DataFrame(list(CryptoPrice.objects.filter(symbol=symbol).order_by('date').values()))
        if df.empty:
            return Response({"error": f"No data found for symbol {symbol}"}, status=404)

        last_price = df['close'].iloc[-1]

        predicted_prices = train_and_predict(symbol=symbol, look_back=look_back, predict_days=days)
        final_price = predicted_prices[-1]

        coins_bought = amount / last_price
        predicted_value = coins_bought * final_price

        result = {
            "symbol": symbol,
            "initial_amount": amount,
            "days": days,
            "last_price": round(last_price, 2),
            "predicted_final_price": round(final_price, 2),
            "predicted_value": round(predicted_value, 2),
            "profit": round(predicted_value - amount, 2)
        }
        return Response(result)

