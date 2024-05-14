from django.shortcuts import render
from .credentials import KEY
from rest_framework.views import APIView
from requests import Request, post
from rest_framework import status
from rest_framework.response import Response
import requests

BASE_URL = 'http://api.weatherapi.com/v1/'

# Create your views here.
class GetWeatherForLocation(APIView):
    def get(self, request, location):
        params = {
            "key": KEY,
            "q": location
        }

        endpoint = 'current.json'

        response = requests.post(BASE_URL + endpoint, params=params)

        if response.status_code == 200:
            weather_data = response.json()
            loc_data = weather_data['location']
            curr_data = weather_data['current']
            data = {
                "name": loc_data.get('name'),
                "region": loc_data.get('region'),
                "country": loc_data.get('country'),
                "temp_f": curr_data.get('temp_f'),
                "is_day": curr_data.get('is_day'),
                "condition": curr_data['condition'].get('text'),
                "precip": curr_data.get('precip_in'),
                "humidity": curr_data.get('humidity')
            }

            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response({"Error": "Failed to fetch weather data"}, status=response.status_code)