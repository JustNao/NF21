import pandas as pd

from charts import get_top_tracks
from genius import get_lyrics
from spotify import get_audio_features
from utils import printProgressBar

columns = ['title', 'artist', 'rank', 'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness',
           'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_ms', 'time_signature', 'lyrics', 'winter', 'spring', 'summer', 'autumn', 'id']
df = pd.DataFrame(columns=columns)

print("Fetching top tracks")
top_tracks = get_top_tracks("01/11/2021", "01/11/2022")

trackIdList = []
tracks = []
print("Fetching lyrics")
printProgressBar(0, len(top_tracks), prefix = 'Progress:', suffix = 'Complete', length = 50)
for index, top_track in enumerate(top_tracks):
    new_track_features = {}
    # print(f"Loading {top_track['title']} by {top_track['artist']}", )
    trackIdList.append(top_track['id'])
    track_lyrics = get_lyrics(f"{top_track['title']} {top_track['artist']}")
    new_track_features['lyrics'] = track_lyrics.replace(
        '\n', ' ').replace(',', '')
    top_track.update(new_track_features)
    tracks.append(top_track)
    printProgressBar(index + 1, len(top_tracks), prefix = 'Progress:', suffix = 'Complete', length = 50)

print("Fetching audio features")
for i in range(0, len(trackIdList), 100):
    start = i
    end = i + 100 if i + 100 < len(trackIdList) else len(trackIdList)
    audio_features = get_audio_features(','.join(trackIdList[start:end]))
    k = 0
    for j in range(start, end):
        if audio_features is None or audio_features[k] is None:
            df.loc[len(df.index)] = tracks[j]
        else:
            df.loc[len(df.index)] = tracks[j] | audio_features[k]
        k += 1

print("Saving data")
df.to_csv('top200.csv', index=False)
