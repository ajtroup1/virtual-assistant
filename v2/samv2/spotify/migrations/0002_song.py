# Generated by Django 5.0.4 on 2024-05-14 18:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spotify', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Song',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uri', models.CharField(max_length=50)),
                ('name', models.CharField(max_length=50)),
                ('artist', models.CharField(max_length=50)),
            ],
        ),
    ]
