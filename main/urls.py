from django.urls import path
from .views import CryptoPredictionView, CryptoPredictionDataView, CryptoPricesByDateView, PortfolioSimulationView

urlpatterns = [
    path("predict/", CryptoPredictionView.as_view(), name="predict"),
    path('predict-plot/', CryptoPredictionDataView.as_view(), name='crypto-predict-plot'),
    path('predict-graf/', CryptoPricesByDateView.as_view(), name='crypto-predict-graf'),
    path('portfolio-simulation/', PortfolioSimulationView.as_view(), name='portfolio-simulation'),
]
