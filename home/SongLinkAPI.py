import requests
from django.contrib import messages
from django.core.exceptions import BadRequest
def spotify_youtube(spotify_link):
    response_json = requests.get("https://api.song.link/v1-alpha.1/links?url={}".format(spotify_link)).json()
    song_channels = list(response_json['entitiesByUniqueId'].keys())
    youtube_channel = "".join(channel if "YOUTUBE_VIDEO" in channel else '' for channel in song_channels)
    return "https://www.youtube.com/watch?v="+ (response_json['entitiesByUniqueId'][youtube_channel]['id'])

def apple_music_spotify(request,apple_music_link):
    response_json = requests.get("https://api.song.link/v1-alpha.1/links?url={}".format(apple_music_link)).json()
    try:
        song_channels = response_json['linksByPlatform']
        spotify_lnk = song_channels['spotify']['url']
    except:
        messages.warning(request,"Wrong Apple Music Link Detected")
        raise BadRequest
    else:
        return spotify_lnk