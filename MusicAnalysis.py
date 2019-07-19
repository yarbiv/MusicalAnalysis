from dotenv import load_dotenv
import nltk
import os
import pylyrics3
import spotipy
import string
import sys

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from spotipy.oauth2 import SpotifyClientCredentials

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

from wordcloud import WordCloud

CONTRACTION_STEMS = ["nt","do","ca","ai"]

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

def get_spotify_info(artist_name):
    client_credentials_manager = SpotifyClientCredentials(client_id = CLIENT_ID, client_secret = CLIENT_SECRET)
    spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    search_artist_name = spotify.search(q='artist:' + artist_name, type='artist')['artists']['items']
    if len(search_artist_name) == 0:
        print("Error: couldn't find anything by {}".format(artist_name))
        exit()
    artist_uri = search_artist_name[0]["uri"]
    results = spotify.artist_albums(artist_uri, album_type='album', country="CA")
    album_results = results['items']
    album_names = [x['name'] for x in album_results]
    albums = []


    for i, album in enumerate(album_results):
        album_pair = [album_names[i], spotify.album_tracks(album['uri'])["items"]]
        albums.append(album_pair)

    album_features_dict = {}

    for album in albums:
        album_name = album[0]
        if album_name not in album_features_dict:
            album_features_dict[album_name] = {}
        else:
            pass
        for track in album[1]:
            track_name = track['name']
            album_features_dict[album_name][track_name] = {}
            features = spotify.audio_features(track['uri'])
            energy = [x['energy'] for x in features]
            valence = [x['valence'] for x in features]
            danceability = [x['danceability'] for x in features]
            album_features_dict[album_name][track_name]['valence'] = valence[0]
            album_features_dict[album_name][track_name]['danceability'] = danceability[0]
            album_features_dict[album_name][track_name]['energy'] = energy[0]
    df = pd.DataFrame([(i,j,album_features_dict[i][j]['valence'], album_features_dict[i][j]['danceability'], album_features_dict[i][j]['energy']) for i in album_features_dict.keys() for j in album_features_dict[i].keys()], columns=["album", "song", "valence", "danceability", "energy"])
    return df


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
        stripped_tokens = [w for w in stripped_tokens if w not in CONTRACTION_STEMS] # Remove contraction stems

        filtered_list = []
        for w in stripped_tokens: # Remove stopwords
            if w not in stop_words and w not in filter_out_artist_name:
                filtered_list.append(w)

        filtered_string = " ".join(str(x) for x in filtered_list) # Turn a list into a string.

        wordcloud = WordCloud(collocations=False, background_color='white', max_words=70, max_font_size=40).generate(filtered_string)
        plt.figure()
        plt.title(album_key)
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        wordcloud_filename = album_key.replace(' ', '_') + "_wordcloud.png"
        cloud_path = os.path.join('files', wordcloud_filename)
        print(cloud_path)
        plt.savefig(cloud_path, dpi=350)


def lexical_diversity(artist_name, albums):
    plt.figure(figsize=(10,6))
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
    df = pd.DataFrame([(i,j,lexical_diversity_albums[i][j]) for i in lexical_diversity_albums.keys() for j in lexical_diversity_albums[i].keys()], columns=["album", "song", "lexical_diversity"])
    sns.set_style("whitegrid")
    ax = sns.boxplot(x="album", y="lexical_diversity", data=df)
    ax = sns.stripplot(x="album", y="lexical_diversity", data=df, edgecolor='black', linewidth=0.2)
    plt.ylabel('lexical diversity by song')
    plt.title('Lexical diversity by album')
    plt.gcf().autofmt_xdate(rotation=20)
    plt.savefig(f'files/{artist_name.replace(" ", "_")}_lex.png')

def main():
    artist_name = input("Artist name: ")
    get_spotify_info(artist_name)
    lyric_data = get_lyrics(artist_name)
    lexical_diversity(artist_name, lyric_data)
    generate_wordcloud(artist_name, lyric_data)

main()
