from django.db import models

# Create your models here.
class Stock(models.Model):
    name = models.CharField(max_length=100, null=False)
    stock_symbol = models.CharField(max_length=100, null=False)
    previous_price = models.CharField(max_length=100, null=False)
    current_price = models.CharField(max_length=100, null=False)
    fiftytwo_week_range = models.CharField(max_length=100, null=False)
    market_cap = models.CharField(max_length=100, null=False)
    pe_ratio = models.CharField(max_length=100, null=False)
    earnings_date = models.CharField(max_length=100, null=False)
    sector = models.CharField(max_length=100, null=False)
    industry = models.CharField(max_length=100, null=False)
    full_time_employees = models.CharField(max_length=100, null=False)
    description = models.TextField(null=False)
    photo_url = models.CharField(max_length=100, default="#")

class HistoricalData(models.Model):
    stock_symbol = models.CharField(max_length=100, null=False)
    date = models.CharField(max_length=100, null=False, default='N/A')
    open = models.CharField(max_length=100, null=False)
    high = models.CharField(max_length=100, null=False)
    low = models.CharField(max_length=100, null=False)
    close = models.CharField(max_length=100, null=False)
    volume = models.CharField(max_length=100, null=False)