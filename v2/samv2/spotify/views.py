
from django.shortcuts import render, redirect
from .credentials import REDIRECT_URI, CLIENT_SECRET, CLIENT_ID
from rest_framework.views import APIView
from requests import Request, post
from rest_framework import status
from rest_framework.response import Response
from .util import *
from .models import *
import requests
from .serializers import *
import random


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
    
class AddToFavorites(APIView):
    def post(self, request):
        response = requests.get('http://127.0.0.1:8000/spotify/current-song')

        # Check if the request was successful
        if response.status_code == 200:
            song_data = response.json()
            title = song_data.get('title')
            artist = song_data.get('artist')
            uri = song_data.get('id')

            # Check if the song is already favorited
            if Song.objects.filter(uri=uri).exists():
                return Response({"message": "Song is already favorited"}, status=status.HTTP_204_NO_CONTENT)

            # If not favorited, add it to favorites
            song = Song(uri=uri, name=title, artist=artist)
            song.save()

            # Serialize the Song object
            serializer = SongSerializer(song)

            return Response({"Added to favorites": serializer.data}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"Error fetching current song"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class QueueByID(APIView):
    def post(self, request, id):
        song_by_id = Song.objects.filter(id=id)[0]

        # get deivce id for song queue
        response = requests.get('http://127.0.0.1:8000/spotify/get-device')
        device = response.json()
        device_id = device.get('id')

        # get song uri for song queue
        uri = song_by_id.uri

        response = queue_song(device_id=device_id, uri=uri)

        print(response)

        return Response({"Queued Song"}, status=status.HTTP_204_NO_CONTENT)

class QueueByArtist(APIView):
    def post(self, request, artist):
        songs = Song.objects.all()
        songs_by_artist = []
        for song in songs:
            if artist.upper() in song.artist.upper():
                songs_by_artist.append(song)
        print('len.....',len(songs_by_artist))
        i = random.randint(1, len(songs_by_artist))
        print(i)
        uri = songs_by_artist[i-1].uri

        # get deivce id for song queue
        response = requests.get('http://127.0.0.1:8000/spotify/get-device')
        device = response.json()
        device_id = device.get('id')

        response = queue_song(device_id=device_id, uri=uri)

        return Response({"Queued Song"}, status=status.HTTP_204_NO_CONTENT)

class GetFavorites(APIView):
    def get(self, request):
        songs = Song.objects.all()
        serializer = SongSerializer(songs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class ClearFavorites(APIView):
    def delete(self, request):
        songs = Song.objects.all()
        songs.delete()
        return Response({"Deleted successfully"}, status=status.HTTP_200_OK)
    
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
