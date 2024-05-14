from django.shortcuts import render
from .financescraper import RunFinanceScraper
from .models import *
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Create your views here.
class RunScraper(APIView):
    def post(self, request, symbol):
        RunFinanceScraper(stock_id=symbol)
        return Response({f"{symbol} scraped"}, status=status.HTTP_200_OK)
        

class GetStocks(APIView):
    def get(self, request):
        stocks = Stock.objects.all()  # Retrieve all stock objects from the database
        serializer = StockSerializer(stocks, many=True)  # Serialize the stock objects
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class GetStockByID(APIView):
    def get(self, request, symbol):
        stock = Stock.objects.filter(stock_symbol=symbol)  # Retrieve all stock objects from the database
        if len(stock) == 0:
            return Response({f"Didn't find stock {symbol}"}, status=status.HTTP_404_NOT_FOUND)
        else:
            stock = stock[0]
        serializer = StockSerializer(stock)  # Serialize the stock objects
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class GetHistoricalData(APIView):
    def get(self, request):
        data = HistoricalData.objects.all()  # Retrieve all stock objects from the database
        serializer = HistoricalDataSerializer(data, many=True)  # Serialize the stock objects
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class GetHistoricalDataByStock(APIView):
    def get(self, request, symbol):
        data = HistoricalData.objects.filter(stock_symbol=symbol)  # Retrieve all stock objects from the database where stock=symbol
        if len(data) == 0:
            return Response({f"No data found for {symbol}"}, status=status.HTTP_204_NO_CONTENT)
        serializer = HistoricalDataSerializer(data, many=True)  # Serialize the stock objects
        return Response(serializer.data, status=status.HTTP_200_OK)