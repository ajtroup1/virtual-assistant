from django.urls import path
from .views import *

urlpatterns = [
    path('get-auth-url', AuthURL.as_view()),
    path('redirect', spotify_callback),
    path('is-authenticated', IsAuthenticated.as_view()),
    path('current-song', CurrentSong.as_view()),
    path('pause', PauseSong.as_view()),
    path('play', PlaySong.as_view()),
    path('skip', SkipSong.as_view()),
    path('rewind', RewindSong.as_view()),
    path('get-device', CurrentDevice.as_view()),
    path('set-volume/<int:volume>', SetVolume.as_view()),
    path('favorite', AddToFavorites.as_view()), # adds the CURRENTLY PLAYING song to favorites
    path('favorites', GetFavorites.as_view()),
    path('clear-favorites', ClearFavorites.as_view()),
    path('queue-artist/<str:artist>', QueueByArtist.as_view()),
    path('queue-id/<int:id>', QueueByID.as_view()),
]