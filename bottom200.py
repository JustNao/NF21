import pandas as pd

from genius import get_lyrics
from spotify import get_albums, get_audio_features, get_tracks
from utils import printProgressBar

df = pd.read_csv('top200.csv')
ids = df['id'].tolist()
seasons = {
    1: "winter",
    2: "spring",
    3: "summer",
    4: "autumn"
}

# Getting all track data from the top 200
print("Getting all track data from the top 200 ...", end=' ')
track_data = []
for i in range(0, len(ids), 50):
    start = i
    end = i + 50 if i + 50 < len(ids) else len(ids)
    batch = get_tracks(','.join(ids[start:end]))['tracks']
    for track in batch:
        track_data.append(track)
print("OK")

# Getting all album ids from the top 200
print("Getting all album ids from the top 200 ...", end=' ')
album_ids = []
for track in track_data:
    album = track['album']['uri'].split(':')[-1]
    album_ids.append(album)
print("OK")

# Getting all album data from the top 200
print("Getting all album data from the top 200 ...", end=' ')
albums = []
for i in range(0, len(album_ids), 20):
    start = i
    end = i + 20 if i + 20 < len(album_ids) else len(album_ids)
    batch = get_albums(','.join(album_ids[start:end]))['albums']
    for album in batch:
        albums.append(album)
print("OK")

# Passing track season to album season
for index, track in df.iterrows():
    for season in seasons.values():
        albums[index][season] = track[season]

# Gettings all track ids from all albums
print("Getting all track ids from all albums ...", end=' ')
track_ids = []
for album in albums:
    for track in album['tracks']['items']:
        track_ids.append(track['uri'].split(':')[-1])
print("OK")

# Getting all track data from all albums
print("Getting all track data from all albums ...", end=' ')
tracks = []
for i in range(0, len(track_ids), 50):
    start = i
    end = i + 50 if i + 50 < len(track_ids) else len(track_ids)
    batch = get_tracks(','.join(track_ids[start:end]))['tracks']
    for track in batch:
        tracks.append(track)
print("OK")

# Format all tracks with album id
print("Format all tracks with album id ...", end=' ')
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
print("OK")

# Keep worst 3 tracks from each album
final_tracks = []
for album_id in formatted_tracks:
    formatted_tracks[album_id].sort(key=lambda x: x['popularity'])
    cleaned_album = filter(lambda track: \
        track['duration_ms'] > 60000 and \
        'intro' not in track['name'].lower() and \
        'interlude' not in track['name'].lower() \
        , formatted_tracks[album_id])
    cleaned_album = list(cleaned_album)
    if len(cleaned_album) > 3:
        for track in cleaned_album[:3]:
            final_tracks.append(track)

# Passing album season to track season
for track in final_tracks:
    album_id = track['album']['id']
    for album in albums:
        if album['id'] == album_id:
            for season in seasons.values():
                track[season] = album[season]
            break
    if 'winter' not in track:
        print(f"ERROR: Track {track['name']} not found in albums")

print("Getting all lyrics ...")
printProgressBar(0, len(final_tracks), prefix = 'Progress:', suffix = 'Complete', length = 50)
track_id_list = []
for index, bottom_track in enumerate(final_tracks):
    new_track_features = {}
    bottom_track['title'] = bottom_track['name']
    bottom_track['artist'] = bottom_track['artists'][0]['name']
    # print(f"Loading {bottom_track['name']} by {bottom_track['artists'][0]['name']}", )
    track_id_list.append(bottom_track['id'])
    track_lyrics = get_lyrics(f"{bottom_track['name']} {bottom_track['artists'][0]['name']}")
    new_track_features['lyrics'] = track_lyrics.replace(
        '\n', ' ').replace(',', '')
    bottom_track.update(new_track_features)
    tracks.append(bottom_track)
    printProgressBar(index + 1, len(final_tracks), prefix = 'Progress:', suffix = 'Complete', length = 50)

columns = ['title', 'artist', 'rank', 'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness',
           'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_ms', 'time_signature', 'lyrics', 'winter', 'spring', 'summer', 'autumn', 'id']
output_df = pd.DataFrame(columns=columns)

print("Fetching audio features ...", end=' ')
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
print("OK")

print("Saving data")
output_df.to_csv('bottom200.csv', index=False, encoding='utf-8')