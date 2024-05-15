from bs4 import BeautifulSoup
import requests
import spotipy
import os
from dotenv import load_dotenv
import json

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = 'http://example.com'
scopes = "playlist-modify-private user-read-private user-read-currently-playing"

# Scraping Billboard 100
URL = "https://www.billboard.com/charts/hot-100/"

date = input("Which year you would like to travel? Type the date in this format: YYYY-MM-DD: ")

response = requests.get(URL + date)
songs_page = response.text
soup = BeautifulSoup(songs_page, "html.parser")
selected_place = soup.select(".o-chart-results-list-row-container")
top_100_songs = [item.select_one("h3").text.strip() for item in selected_place]


sp = spotipy.oauth2.SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scopes,
    cache_path="token.txt",  # If we don't specify cache_path then it will create .cache file instead.
    username="Mert"
)
# This is for creating spotify token, it will create a token.txt file for authentication.
sp.get_access_token(as_dict=True)

year = date.split("-")[0]
song_uris = []

with open("token.txt", "r") as f:
    data = f.readline()
    token_info = json.loads(data)
    access_token = token_info["access_token"]  # Access the "access_token" key
    client = spotipy.client.Spotify(auth=access_token)

    for song in top_100_songs:
        result = client.search(q=f"track:{song} year:{year}", type="track")
        print(result)
        try:
            uri = result["tracks"]["items"][0]["uri"]
            song_uris.append(uri)
        except IndexError:
            print(f"{song} doesn't exist in Spotify. Skipped.")

    my_playlist = client.user_playlist_create(user=os.getenv("USER_ID"), name=f"{date} Billboard 100", public=False)

    client.playlist_add_items(playlist_id=my_playlist["id"], items=song_uris)
