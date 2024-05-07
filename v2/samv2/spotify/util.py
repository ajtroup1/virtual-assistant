from .models import SpotifyToken
from django.utils import timezone
from datetime import timedelta
from .credentials import CLIENT_ID, CLIENT_SECRET
from requests import post, put, get


BASE_URL = "https://api.spotify.com/v1/me/"


def get_user_tokens():
    user_tokens = SpotifyToken.objects.filter()

    if user_tokens.exists():
        return user_tokens[0]
    else:
        return None


def update_or_create_user_tokens(access_token, token_type, expires_in, refresh_token):
    tokens = get_user_tokens()
    expires_in = timezone.now() + timedelta(seconds=expires_in)

    if tokens:
        tokens.access_token = access_token
        tokens.refresh_token = refresh_token
        tokens.expires_in = expires_in
        tokens.token_type = token_type
        tokens.save(update_fields=['access_token',
                                   'refresh_token', 'expires_in', 'token_type'])
    else:
        tokens = SpotifyToken(access_token=access_token,
                              refresh_token=refresh_token, token_type=token_type, expires_in=expires_in)
        tokens.save()


def is_spotify_authenticated():
    tokens = get_user_tokens()
    if tokens:
        expiry = tokens.expires_in
        if expiry <= timezone.now():
            refresh_spotify_token()

        return True

    return False


def refresh_spotify_token():
    refresh_token = get_user_tokens().refresh_token

    response = post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }).json()

    access_token = response.get('access_token')
    token_type = response.get('token_type')
    expires_in = response.get('expires_in')

    update_or_create_user_tokens(
        access_token, token_type, expires_in, refresh_token)


def execute_spotify_api_request(endpoint, post_=False, put_=False):
    tokens = get_user_tokens()
    headers = {'Content-Type': 'application/json',
               'Authorization': "Bearer " + tokens.access_token}
    
    # print(tokens.access_token)

    if post_:
        post(BASE_URL + endpoint, headers=headers)
    if put_:
        put(BASE_URL + endpoint, headers=headers)

    # print('url: ',BASE_URL + endpoint)

    response = get(BASE_URL + endpoint, {}, headers=headers)
    try:
        return response.json()
    except:
        return {'Error': 'Issue with request'}

def play_song():
    return execute_spotify_api_request("player/play", put_=True)

def pause_song():
    return execute_spotify_api_request("player/pause", put_=True)

def skip_song():
    return execute_spotify_api_request("player/next", post_=True)

def rewind_song():
    return execute_spotify_api_request( "player/previous", post_=True)

def set_volume(val):
    return execute_spotify_api_request(f"player/volume?volume_percent={val}", put_=True)