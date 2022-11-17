import requests as rq
import json
from datetime import datetime as dt, timedelta
from time import sleep

CHARTS_API_URL = "https://charts-spotify-com-service.spotify.com/auth/v0/charts/regional-fr-weekly"
CHARTS_TOKEN_URL = "http://everstone.ddns.net:1000/api/charts?auth=nao"
response = rq.get(CHARTS_TOKEN_URL)
CHARTS_TOKEN = response.json()["token"]

def get_latest():
    headers = {
        "Authorization": f"Bearer {CHARTS_TOKEN}"
    }
    response = rq.get(CHARTS_API_URL + "/latest", headers=headers)
    try:
        latest_list = response.json()
    except rq.exceptions.JSONDecodeError:
        print("Charts token is out of date")
        return []
    return latest_list["entries"]


def get_weekly(week: str):
    headers = {
        "Authorization": f"Bearer {CHARTS_TOKEN}"
    }
    response = rq.get(f"{CHARTS_API_URL}/{week}", headers=headers)
    try:
        latest_list = response.json()
    except rq.exceptions.JSONDecodeError:
        print("Charts token is out of date")
        return []
    return latest_list["entries"]


def _get_top(start: str, end: str = dt.now().strftime("%d/%m/%Y")):
    start_date = dt.strptime(start, "%d/%m/%Y")
    end_date = dt.strptime(end, "%d/%m/%Y")
    while start_date.weekday() != 3:
        start_date += timedelta(days=1)

    top_tracks = []
    while start_date <= end_date:
        week = start_date.strftime("%Y-%m-%d")
        print(f"Getting charts for week of {week}")
        weekly_top = get_weekly(week)
        top_tracks += weekly_top
        sleep(0.5)
        start_date += timedelta(days=7)

    return top_tracks


seasons = {
    1: "winter",
    2: "spring",
    3: "summer",
    4: "autumn"
}

def get_top_tracks(start: str, end: str = dt.now().strftime("%d/%m/%Y")):
    top_tracks = _get_top(start, end)
    mean = {}
    start_date = dt.strptime(start, "%d/%m/%Y")
    month = start_date.month
    for track in top_tracks:
        id = track["trackMetadata"]['trackUri'].split(":")[-1]
        if id not in mean:
            mean[id] = {
                "title": track["trackMetadata"]["trackName"],
                "artist": track["trackMetadata"]["artists"][0]["name"],
                "total_streams": int(track["chartEntryData"]["rankingMetric"]["value"]),
                "count": 1
            }
        else:
            mean[id]["total_streams"] += int(track["chartEntryData"]["rankingMetric"]["value"])
            mean[id]["count"] += 1
    result = []
    for id in mean:
        print(f"month: {month} -> {seasons[((month - 1)%12 // 3) + 1]}")
        track = {
            "id": id,
            "streams": mean[id]["total_streams"] / mean[id]["count"],
            "title": mean[id]["title"],
            "artist": mean[id]["artist"],
        }
        current_season = ((month - 1)%12 // 3) + 1
        for season in seasons:
            track[seasons[season]] = 1 if season == current_season else 0
        result.append(track)
    result = sorted(result, key=lambda x: x["streams"], reverse=True)
    for i in range(len(result)):
        result[i]["rank"] = i + 1
    return result
