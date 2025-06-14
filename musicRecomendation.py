import pandas as pd
import numpy as np
import re
import os
import json
import requests
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import euclidean_distances
from umap import UMAP


YOUTUBE_API_KEY = "AIzaSyB36xMPo5-pv2vF8eZM2dJFqwvXDTH3KN8"


CACHE_FILE = "youtube_cache.json"
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r") as f:
        youtube_cache = json.load(f)
else:
    youtube_cache = {}


def save_cache():
    with open(CACHE_FILE, "w") as f:
        json.dump(youtube_cache, f, indent=2)



random_state = 42
np.random.seed(random_state)


df = pd.read_csv("dataset/data.csv")


df = df.drop_duplicates(subset=["artists", "name"])
df = df[df["name"].str.contains("[a-zA-Z]+")]
df["artists_main"] = df["artists"].apply(
    lambda i: re.search(r"'([^']+)'", i).group(1) if re.search(r"'([^']+)'", i) else i
)
df["artists_num"] = df["artists"].str.count("'")
artist_counts = df["artists_main"].value_counts()
df["artists_main_encoded"] = df["artists_main"].map(artist_counts)

features = [
    "valence",
    "year",
    "acousticness",
    "danceability",
    "duration_ms",
    "energy",
    "artists_num",
    "instrumentalness",
    "liveness",
    "loudness",
    "popularity",
    "speechiness",
    "tempo",
    "artists_main_encoded",
]

scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(df[features])

kmeans = KMeans(n_clusters=5, n_init=10, random_state=random_state)
df["Cluster"] = kmeans.fit_predict(X_scaled)

X_pca = PCA(n_components=10, random_state=random_state).fit_transform(X_scaled)
X_umap = UMAP(n_components=2, random_state=random_state).fit_transform(X_pca)
df["umap_1"] = X_umap[:, 0]
df["umap_2"] = X_umap[:, 1]
df["features"] = list(X_umap)


mood_presets = {
    "happy": {"valence": 0.8, "energy": 0.7},
    "calm": {"valence": 0.4, "energy": 0.3},
    "sad": {"valence": 0.2, "energy": 0.3},
    "party": {"valence": 0.9, "energy": 0.9, "danceability": 0.8},
}



def get_direct_youtube_link(artist, title):
    query = f"{artist} {title}".lower()

   
    if query in youtube_cache:
        return youtube_cache[query]

    
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "key": YOUTUBE_API_KEY,
        "type": "video",
        "maxResults": 1,
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
        if "items" in data and data["items"]:
            video_id = data["items"][0]["id"]["videoId"]
            link = f"https://www.youtube.com/watch?v={video_id}"
            youtube_cache[query] = link
            save_cache()
            return link
    except Exception as e:
        print(f"YouTube API Error: {e}")

    youtube_cache[query] = None
    save_cache()
    return None



def recommend_by_song(song_name, top_n=10):
    song_name = song_name.lower()
    df["name_lower"] = df["name"].str.lower()

    matches = df[df["name_lower"].str.contains(song_name)]
    if matches.empty:
        return []

    ref_song = matches.iloc[0]
    song_vec = np.array(ref_song["features"]).reshape(1, -1)

    df["distance"] = euclidean_distances(df["features"].tolist(), song_vec)

    similar_songs = (
        df[df["name"] != ref_song["name"]].sort_values("distance").head(top_n)
    )

    result = [
        {
            "artist": ref_song["artists_main"],
            "title": ref_song["name"],
            "link": get_direct_youtube_link(ref_song["artists_main"], ref_song["name"]),
        }
    ] + [
        {
            "artist": row["artists_main"],
            "title": row["name"],
            "link": get_direct_youtube_link(row["artists_main"], row["name"]),
        }
        for _, row in similar_songs.iterrows()
    ]

    return result


def recommend_by_artist(artist_name, top_n=100):
    artist_name = artist_name.lower()
    df["artist_lower"] = df["artists_main"].str.lower()

    if artist_name not in df["artist_lower"].values:
        return []

    recs = (
        df[df["artist_lower"] == artist_name]
        .sort_values("popularity", ascending=False)
        .head(top_n)
    )

    return [
        {
            "artist": row["artists_main"],
            "title": row["name"],
            "link": get_direct_youtube_link(row["artists_main"], row["name"]),
        }
        for _, row in recs.iterrows()
    ]


def recommend_by_mood(mood, top_n=10, max_distance=0.25):
    if mood not in mood_presets:
        return []

    mood_vec = np.array(
        [mood_presets[mood].get(f, 0.5) for f in ["valence", "energy", "danceability"]]
    )
    song_vecs = df[["valence", "energy", "danceability"]].fillna(0.5).values
    df["distance"] = euclidean_distances(song_vecs, mood_vec.reshape(1, -1))

    # Filter lagu yang benar-benar dekat
    close_songs = df[df["distance"] <= max_distance]

    recs = close_songs.sort_values("distance").head(top_n)

    return [
        {
            "artist": row["artists_main"],
            "title": row["name"],
            "link": get_direct_youtube_link(row["artists_main"], row["name"]),
        }
        for _, row in recs.iterrows()
    ]
