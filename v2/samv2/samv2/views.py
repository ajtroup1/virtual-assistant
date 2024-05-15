from rest_framework.views import APIView
from .youtubescraper import RunYoutubeScraper
from .pricescraper import RunScraper
from rest_framework import status
from rest_framework.response import Response

class YoutubeScraper(APIView):
    def post(self, request, query):
        RunYoutubeScraper(query=query)
        return Response({"Navigated successfully"}, status=status.HTTP_204_NO_CONTENT)
    
class PriceScraper(APIView):
    def post(self, request, query):
        items = RunScraper(search_val=query)
        return Response(items, status=status.HTTP_200_OK)