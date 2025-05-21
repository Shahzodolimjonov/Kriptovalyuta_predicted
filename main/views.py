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


class CryptoPredictionPlotView(APIView):
    def get(self, request):
        symbol = request.GET.get('symbol', 'BTC')

        df = pd.DataFrame(list(CryptoPrice.objects.filter(symbol=symbol).order_by('date').values()))
        actual_prices = df['close'].tail(30).tolist()

        predicted_prices = train_and_predict(symbol=symbol, look_back=30, predict_days=15)

        img_buf = plot_prediction(actual_prices, predicted_prices, symbol)

        return HttpResponse(img_buf, content_type='image/png')


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