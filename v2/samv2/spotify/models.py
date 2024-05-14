from django.db import models


class SpotifyToken(models.Model):
    user = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    refresh_token = models.CharField(max_length=150)
    access_token = models.CharField(max_length=150)
    expires_in = models.DateTimeField()
    token_type = models.CharField(max_length=50)

class Song(models.Model):
    uri = models.CharField(max_length=50, null=False)
    name = models.CharField(max_length=50, unique=False)
    artist = models.CharField(max_length=50, unique=False)
    