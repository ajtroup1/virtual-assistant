
from django.shortcuts import render, redirect
from .credentials import REDIRECT_URI, CLIENT_SECRET, CLIENT_ID
from rest_framework.views import APIView
from requests import Request, post
from rest_framework import status
from rest_framework.response import Response
from .util import *
from .models import *


class AuthURL(APIView):
    def get(self, request, fornat=None):
        scopes = 'user-read-playback-state user-modify-playback-state user-read-currently-playing'

        url = Request('GET', 'https://accounts.spotify.com/authorize', params={
            'scope': scopes,
            'response_type': 'code',
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID
        }).prepare().url

        return Response({'url': url}, status=status.HTTP_200_OK)


def spotify_callback(request, format=None):
    code = request.GET.get('code')
    error = request.GET.get('error')

    response = post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }).json()

    access_token = response.get('access_token')
    token_type = response.get('token_type')
    refresh_token = response.get('refresh_token')
    expires_in = response.get('expires_in')
    error = response.get('error')

    if not request.session.exists(request.session.session_key):
        request.session.create()

    update_or_create_user_tokens(access_token, token_type, expires_in, refresh_token)

    return redirect('frontend:')


class IsAuthenticated(APIView):
    def get(self, request, format=None):
        is_authenticated = is_spotify_authenticated()
        return Response({'status': is_authenticated}, status=status.HTTP_200_OK)


class CurrentSong(APIView):
    def get(self, request, format=None):
        endpoint = "player/currently-playing"
        response = execute_spotify_api_request(endpoint)

        if 'error' in response or 'item' not in response:
            return Response({}, status=status.HTTP_204_NO_CONTENT)

        item = response.get('item')
        duration = item.get('duration_ms')
        progress = response.get('progress_ms')
        album_cover = item.get('album').get('images')[0].get('url')
        is_playing = response.get('is_playing')
        song_id = item.get('id')

        artist_string = ""

        for i, artist in enumerate(item.get('artists')):
            if i > 0:
                artist_string += ", "
            name = artist.get('name')
            artist_string += name

        song = {
            'title': item.get('name'),
            'artist': artist_string,
            'duration': duration,
            'time': progress,
            'image_url': album_cover,
            'is_playing': is_playing,
            'id': song_id
        }

        return Response(song, status=status.HTTP_200_OK)
    
class PauseSong(APIView):
    def put(self, request, format=None):
        pause_song()
        return Response({}, status=status.HTTP_204_NO_CONTENT)
    
class PlaySong(APIView):
    def put(self, request, format=None):
        play_song()
        return Response({}, status=status.HTTP_204_NO_CONTENT)
       
class SkipSong(APIView):
    def post(self, request, format=None):
        skip_song()
        return Response({}, status=status.HTTP_204_NO_CONTENT)
    
class RewindSong(APIView):
    def post(self, request, format=None):
        rewind_song()
        return Response({}, status=status.HTTP_204_NO_CONTENT)
    
class CurrentDevice(APIView):
    def get(self, request, format=None):
        endpoint = "player/devices"
        response = execute_spotify_api_request(endpoint)

        if 'error' in response:
            return Response({}, status=status.HTTP_204_NO_CONTENT)

        devices = response.get('devices')
        device = devices[0]

        return Response(device, status=status.HTTP_200_OK)
    
class SetVolume(APIView):
    def put(self, request, volume, format=None):
        set_volume(volume)
        return Response({}, status=status.HTTP_204_NO_CONTENT)
