import pandas as pd
from spotify import get_tracks, get_albums, get_audio_features
from genius import get_lyrics

df = pd.read_csv('top200.csv')
ids = df['id'].tolist()

# Getting all track data from the top 200
track_data = []
for i in range(0, len(ids), 50):
    start = i
    end = i + 50 if i + 50 < len(ids) else len(ids)
    batch = get_tracks(','.join(ids[start:end]))['tracks']
    for track in batch:
        track_data.append(track)

# Getting all album ids from the top 200
album_ids = []
for track in track_data:
    if track['album']['album_type'] != "single":
        album = track['album']['uri'].split(':')[-1]
        album_ids.append(album)

# Getting all album data from the top 200
albums = []
for i in range(0, len(album_ids), 20):
    start = i
    end = i + 20 if i + 20 < len(album_ids) else len(album_ids)
    batch = get_albums(','.join(album_ids[start:end]))['albums']
    for album in batch:
        albums.append(album)

# Gettings all track ids from all albums
track_ids = []
for album in albums:
    for track in album['tracks']['items']:
        track_ids.append(track['uri'].split(':')[-1])

# Getting all track data from all albums
tracks = []
for i in range(0, len(track_ids), 50):
    start = i
    end = i + 50 if i + 50 < len(track_ids) else len(track_ids)
    batch = get_tracks(','.join(track_ids[start:end]))['tracks']
    for track in batch:
        tracks.append(track)

# Format all tracks with album id
formatted_tracks = {}
for track in tracks:
    album_id = track['album']['id']
    if album_id not in formatted_tracks:
        formatted_tracks[album_id] = [track]
    else:
        track_found = False
        for added_track in formatted_tracks[album_id]:
            if added_track['id'] == track['id']:
                track_found = True
                break
        if not track_found:
            formatted_tracks[album_id].append(track)

# Keep worst 3 tracks from each album
final_tracks = []
for album_id in formatted_tracks:
    formatted_tracks[album_id].sort(key=lambda x: x['popularity'])
    for track in formatted_tracks[album_id][:3]:
        final_tracks.append(track)

track_id_list = []
for bottom_track in final_tracks:
    new_track_features = {}
    bottom_track['title'] = bottom_track['name']
    bottom_track['artist'] = bottom_track['artists'][0]['name']
    print(f"Loading {bottom_track['name']} by {bottom_track['artists'][0]['name']}", )
    track_id_list.append(bottom_track['id'])
    track_lyrics = get_lyrics(f"{bottom_track['name']} {bottom_track['artists'][0]['name']}")
    new_track_features['lyrics'] = track_lyrics.replace(
        '\n', ' ').replace(',', '')
    bottom_track.update(new_track_features)
    tracks.append(bottom_track)

columns = ['title', 'artist', 'rank', 'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness',
           'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_ms', 'time_signature', 'lyrics', 'id']
output_df = pd.DataFrame(columns=columns)

print("Fetching audio features")
for i in range(0, len(track_id_list), 100):
    start = i
    end = i + 100 if i + 100 < len(track_id_list) else len(track_id_list)
    audio_features = get_audio_features(','.join(track_id_list[start:end]))
    k = 0
    for j in range(start, end):
        if audio_features[k] is None:
            output_df.loc[len(output_df.index)] = final_tracks[j]
        else:
            output_df.loc[len(output_df.index)] = final_tracks[j] | audio_features[k]
        k += 1

print("Saving data")
output_df.to_csv('bottom200.csv', index=False)