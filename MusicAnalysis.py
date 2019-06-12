from dotenv import load_dotenv
import nltk
import os
import pylyrics3
import spotipy
import string
import sys

import matplotlib.pyplot as plt

from spotipy.oauth2 import SpotifyClientCredentials

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

from wordcloud import WordCloud

load_dotenv()
CLIENT_ID = os.getenv(CLIENT_ID)
CLIENT_SECRET = os.getenv(CLIENT_SECRET)

def get_spotify_info(artist_name):
    #TODO: Break this up into several functions. One to get data, then we can do fun stuff with the data in separate functions
    #TODO: Ideally, a scatter plot of valence vs energy. This can show us the happiest, saddest, angriest songs etc.
    client_credentials_manager = SpotifyClientCredentials(client_id = CLIENT_ID, client_secret = CLIENT_SECRET)
    spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    search_artist_name = spotify.search(q='artist:' + artist_name, type='artist')
    artist_uri = search_artist_name['artists']['items'][0]["uri"]
    results = spotify.artist_albums(artist_uri, album_type='album', country="CA")
    album_results = results['items']
    album_names = [x['name'] for x in album_results]
    albums = []


    for i, album in enumerate(album_results):
        album_pair = [album_names[i], spotify.album_tracks(album['uri'])["items"]]
        albums.append(album_pair)

    for album in albums:
        valence_sum = 0
        energy_sum = 0
        danceability_sum = 0
        sonic_score_sum = 0
        for track in album[1]:
            track_name = track['name']
            features = spotify.audio_features(track['uri'])
            energy = [x['energy'] for x in features]
            valence = [x['valence'] for x in features]
            danceability = [x['danceability'] for x in features]
            valence_sum += valence[0]
            energy_sum += energy[0]
            danceability_sum += danceability[0]
        print("album name: " + str(album[0]))
        print('avg energy: ' + str(energy_sum / len(album[1])))
        print('avg valence: ' +  str(valence_sum / len(album[1])))
        print('avg danceability: ' + str(danceability_sum / len(album[1])))


def get_lyrics(artist_name): # Gets raw lyrics in lowercase.
    albums = {}

    artist_lyrics = pylyrics3.get_artist_lyrics(artist_name, albums=True)
    for album_key, album_val in artist_lyrics.items():
        albums[album_key] = {}
        for track_key, track_val in album_val.items():
            if track_val:
                albums[album_key][track_key] = track_val.lower()

    return albums

def generate_wordcloud(artist_name, albums):
    filter_out_artist_name = artist_name.lower().split(" ")
    stop_words = set(stopwords.words('english'))
    table = str.maketrans('', '', string.punctuation)

    for album_key, album_val in albums.items():
        album_text = ""
        for track_key, track_val in album_val.items():
            album_text += track_val
        word_tokens = word_tokenize(album_text) # Tokenize text
        stripped_tokens = [w.translate(table) for w in word_tokens] # strip punctuation
        stripped_tokens = [w for w in stripped_tokens if w.isalpha()] # only alphabetic tokens
        stripped_tokens = [w for w in stripped_tokens if w != "nt"] # Remove 'nt' contraction stems

        filtered_list = []
        for w in stripped_tokens: # Remove stopwords
            if w not in stop_words and w not in filter_out_artist_name:
                filtered_list.append(w)

        filtered_string = " ".join(str(x) for x in filtered_list) # Turn a list into a string.

        #TODO: add artist name/album name to each wordcloud
        wordcloud = WordCloud(collocations=False, background_color='white', max_words=100, max_font_size=40).generate(filtered_string)
        plt.figure()
        plt.imshow(wordcloud)
        plt.axis("off")
        plt.savefig(album_key + " wordcloud.png") # TODO: don't save this to the root!


def lexical_diversity(artist_name, albums):
    lexical_diversity_albums = {}
    filter_out_artist_name = artist_name.lower().split(" ")
    table = str.maketrans('', '', string.punctuation)

    for album_key, album_val in albums.items():
        lexical_diversity_albums[album_key] = {}
        for track_key, track_val in album_val.items():
            word_tokens = word_tokenize(track_val) # Tokenize text
            stripped_tokens = [w.translate(table) for w in word_tokens] # strip punctuation
            stripped_tokens = [w for w in stripped_tokens if w.isalpha()] # only alphabetic tokens
            stripped_tokens = [w for w in stripped_tokens if w not in filter_out_artist_name] # Remove artist name (Sometimes lyric pages have this!)
            lexical_diversity_index = len(set(stripped_tokens)) / len(stripped_tokens)
            lexical_diversity_albums[album_key][track_key] = lexical_diversity_index

    # TODO: Create box plot showing each album's average lexical diversity per track.

def main():
    artist_name = input("Artist name: ")
    get_spotify_info(artist_name)
    lyric_data = get_lyrics(artist_name)
    lexical_diversity(artist_name, lyric_data)
    generate_wordcloud(artist_name, lyric_data)

main()
