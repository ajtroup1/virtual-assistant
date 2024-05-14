from django.urls import path
from .views import *

urlpatterns = [
    path('currentfor/<str:location>', GetWeatherForLocation.as_view())
]