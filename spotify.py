import requests as rq

SPOTIFY_AUTH_URL = 'https://accounts.spotify.com/api/token'
SPOTIFY_API_URL = "https://api.spotify.com/v1"

def get_token() -> str:
    client_secret = "MTY0NjM3MmVlMzA3NDIxMTkzYWYyNDhkZWM0NzdlMDk6MmZmY2FmOTc5MTI0NGI2MDk2Mzk3YzNjYmM5YjcxOTI"
    auth_response = rq.post(SPOTIFY_AUTH_URL, {
        'grant_type': 'client_credentials',
    },
        headers={
        'Authorization': 'Basic ' + client_secret,
        'Content-Type': 'application/x-www-form-urlencoded',
    })
    auth_response_data = auth_response.json()
    access_token = auth_response_data['access_token']
    return access_token

SPOTIFY_TOKEN = get_token()

def get_track(track_id: str, access_token: str = SPOTIFY_TOKEN):
    track_url = f"{SPOTIFY_API_URL}/tracks/{track_id}"
    response = rq.get(track_url, headers={
        "Authorization": "Bearer " + access_token
    })
    response_json = response.json()
    return response_json

def get_tracks(track_ids: str, access_token: str = SPOTIFY_TOKEN):
    track_url = f"{SPOTIFY_API_URL}/tracks?ids={track_ids}"
    response = rq.get(track_url, headers={
        "Authorization": "Bearer " + access_token
    })
    response_json = response.json()
    return response_json

def get_albums(album_ids: str, access_token: str = SPOTIFY_TOKEN):
    track_url = f"{SPOTIFY_API_URL}/albums?ids={album_ids}"
    response = rq.get(track_url, headers={
        "Authorization": "Bearer " + access_token
    })
    response_json = response.json()
    return response_json

def get_artists(artist_ids: str, access_token: str = SPOTIFY_TOKEN):
    track_url = f"{SPOTIFY_API_URL}/artists?ids={artist_ids}"
    response = rq.get(track_url, headers={
        "Authorization": "Bearer " + access_token
    })
    response_json = response.json()
    if 'artists' in response_json:
        artists = response_json['artists']
    else:
        artists = []
    return artists


def get_audio_features(track_id: str, access_token: str = SPOTIFY_TOKEN):
    track_url = f"{SPOTIFY_API_URL}/audio-features?ids={track_id}"
    response = rq.get(track_url, headers={
        "Authorization": "Bearer " + access_token
    })
    response_json = response.json()
    if len(response_json['audio_features']) == 1:
        return response_json['audio_features'][0]
    return response_json['audio_features']
