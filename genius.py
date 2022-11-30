import requests as rq
from bs4 import BeautifulSoup as bs
import urllib.parse

GENIUS_TOKEN = "8qfOR0OEWUh-SG3me7lhilbjVu8exI3vPxlkc8Nj2-CzZPjP7Yu4zAMfEsgpd9vQ"
GENIUS_API_URL = "https://api.genius.com"


def search(query: str):
    encoded_query = urllib.parse.quote(query)
    search_url = f"{GENIUS_API_URL}/search?q={encoded_query}"
    response = rq.get(search_url, headers={
        "Authorization": "Bearer " + GENIUS_TOKEN
    })
    response_json = response.json()
    return response_json


def get_song_lyrics_url(title: str) -> str:
    search_result = search(title)
    for hit in search_result['response']['hits']:
        if hit['result']['artist_names'].lower() != "spotify":
            return hit['result']['url']
    if len(search_result['response']['hits']) > 0:
        return search_result['response']['hits'][0]['result']['url']
    else:
        return None


def get_lyrics(title: str) -> str:
    lyrics_url = get_song_lyrics_url(title)
    if lyrics_url is None:
        return ""

    lyrics_page = rq.get(lyrics_url)
    soup = bs(lyrics_page.text, 'html.parser')
    data_container = soup.findAll('div', attrs={
        'data-lyrics-container': 'true'
    })
    if data_container is None:
        return ""

    lyrics = ""
    for div in data_container:
        lyrics += div.get_text(separator='\n')

    if len(lyrics) > 10000:
        return ""

    return lyrics
