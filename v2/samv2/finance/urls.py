from django.urls import path
from .views import *

urlpatterns = [
    path('run-scraper/<str:symbol>', RunScraper.as_view()),
    path('stocks', GetStocks.as_view()),
    path('stock/<str:symbol>', GetStockByID.as_view()),
    path('historical-data', GetHistoricalData.as_view()),
    path('historical-data/<str:symbol>', GetHistoricalDataByStock.as_view()),
]