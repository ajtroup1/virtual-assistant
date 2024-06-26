# Generated by Django 5.0.4 on 2024-05-13 21:28

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stock_symbol', models.CharField(max_length=100)),
                ('date', models.CharField(default='N/A', max_length=100)),
                ('open', models.CharField(max_length=100)),
                ('high', models.CharField(max_length=100)),
                ('low', models.CharField(max_length=100)),
                ('close', models.CharField(max_length=100)),
                ('volume', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Stock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('stock_symbol', models.CharField(max_length=100)),
                ('previous_price', models.CharField(max_length=100)),
                ('current_price', models.CharField(max_length=100)),
                ('fiftytwo_week_range', models.CharField(max_length=100)),
                ('market_cap', models.CharField(max_length=100)),
                ('pe_ratio', models.CharField(max_length=100)),
                ('earnings_date', models.CharField(max_length=100)),
                ('sector', models.CharField(max_length=100)),
                ('industry', models.CharField(max_length=100)),
                ('full_time_employees', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('photo_url', models.CharField(default='#', max_length=100)),
            ],
        ),
    ]
