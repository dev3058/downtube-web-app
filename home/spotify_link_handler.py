import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from django.conf import settings
def SpotifyLinkHandler(link : str) -> str:
    spotify_dict = {}
    artist_list = []
    auth_manager = SpotifyClientCredentials(client_id = settings.SPOTIFY_CLIENT_ID,
                                        client_secret = settings.SPOTIFY_CLIENT_SECRET)
    sp = spotipy.Spotify(auth_manager = auth_manager)
    track_info = sp.track(link)
    spotify_dict["name"] = track_info["name"]
    spotify_dict["album"] = track_info["album"]["name"]
    for artist in track_info["artists"]:
        artist_list.append(artist["name"])
    spotify_dict["artists_list"] = artist_list
    spotify_dict["song_image"] = track_info["album"]["images"][0]["url"]
    spotify_dict["release_date"] = track_info["album"]["release_date"]
    length = track_info["duration_ms"]
    minutes  = length // 60000
    seconds = (length / 60000) - minutes
    total_seconds = round(seconds*60)
    spotify_dict["length"] = f"{minutes}:{total_seconds:02d}"

    return spotify_dict 




