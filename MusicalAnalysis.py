from dotenv import load_dotenv
import nltk
import os
import pylyrics3
import spotipy
import string
import sys
import datetime

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

from spotipy.oauth2 import SpotifyClientCredentials

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

from wordcloud import WordCloud

CONTRACTION_STEMS = ["nt","do","ca","ai"]

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

def get_spotify_data(artist_name):
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
    df = pd.DataFrame([(i,j,album_features_dict[i][j]['valence'], album_features_dict[i][j]['danceability'], album_features_dict[i][j]['energy']) \
        for i in album_features_dict.keys() for j in album_features_dict[i].keys()], columns=["album", "song", "valence", "danceability", "energy"])
    return df

def musical_feature_scatter(artist_name, spotify_data, save_path):
    albums = spotify_data.album.unique()
    cmap = plt.get_cmap('viridis')
    colors = cmap(np.linspace(0, 1, len(albums)))
    groups = spotify_data.groupby("album")

    fig, ax = plt.subplots()
    curr_color = 0
    for name, group in groups:
        ax.plot(group.valence, group.energy, label=name, marker='o', linestyle='', c=colors[curr_color], ms=3.75)
        curr_color += 1
    ax.legend(bbox_to_anchor=(1.04,1), borderaxespad=0)
    fig.set_figheight(10)
    fig.set_figheight(6)
    plt.xlabel('valence')
    plt.ylabel('energy')
    replaced_artist_name = artist_name.replace(" ", "_")
    file_name = f"{replaced_artist_name}_scatter.png"
    plt.savefig(f'{save_path}/scatter/{file_name}', bbox_inches="tight")
    return f'{save_path}/scatter/{file_name}'

def rank_songs_by(spotify_data, attribute_to_rank, save_path):
    fig, ax = plt.subplots()
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)

    data_copy = spotify_data.copy()
    attributes = ["valence", "energy", "danceability"]
    for attribute in attributes:
        if attribute != attribute_to_rank:
            del data_copy[attribute]

    sorted_data_ascending = data_copy.sort_values(attribute_to_rank)
    sorted_data_descending = data_copy.sort_values(attribute_to_rank, ascending=False)

    ascending_html = sorted_data_ascending.head() \
    .style \
    .set_properties(**{'font-size': '9pt', 'font-family': 'Calibri'}) \
    .render(caption=f"bottom 5 songs by {attribute_to_rank}")

    descending_html = sorted_data_descending.head() \
    .style \
    .set_properties(**{'font-size': '9pt', 'font-family': 'Calibri'}) \
    .render(caption=f"top 5 songs by {attribute_to_rank}")

    ascending_path = f'{save_path}/rank/{attribute_to_rank}_ascending.html'
    descending_path = f'{save_path}/rank/{attribute_to_rank}_descending.html'
    with open(ascending_path, 'w+') as file:
        file.write(ascending_html)
    with open(descending_path, 'w+') as file:
        file.write(descending_html)
    return [ascending_path, descending_path]

def get_lyrics(artist_name): # Gets raw lyrics in lowercase.
    albums = {}

    artist_lyrics = pylyrics3.get_artist_lyrics(artist_name, albums=True)
    for album_key, album_val in artist_lyrics.items():
        albums[album_key] = {}
        for track_key, track_val in album_val.items():
            if track_val:
                albums[album_key][track_key] = track_val.lower()

    return albums

def generate_wordcloud(artist_name, albums, save_path):
    filter_out_artist_name = artist_name.lower().split(" ")
    stop_words = set(stopwords.words('english'))
    table = str.maketrans('', '', string.punctuation)
    paths = []

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
        cloud_path = f"{save_path}/wordcloud/{wordcloud_filename}"
        plt.savefig(cloud_path, dpi=350)
        paths.append(cloud_path)
    return paths

def lexical_diversity(artist_name, albums, save_path):
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
    replaced_artist_name = artist_name.replace(" ", "_")
    file_name = f"{replaced_artist_name}_lex.png"
    plt.savefig(f"{save_path}/lexdiv/{file_name}")
    return f"{save_path}/lexdiv/{file_name}"

def setup_dirs():
    dir_name = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    save_path = os.path.join('static', dir_name)
    if not os.path.exists('static'):
        os.mkdir('static')
    os.mkdir(save_path)
    os.mkdir(os.path.join(save_path, 'lexdiv'))
    os.mkdir(os.path.join(save_path, 'wordcloud'))
    os.mkdir(os.path.join(save_path, 'rank'))
    os.mkdir(os.path.join(save_path, 'scatter'))
    return save_path

def musical_analysis(artist_name):
    save_path = setup_dirs()
    spotify_data = get_spotify_data(artist_name)
    lyric_data = get_lyrics(artist_name)
    paths = []
    paths.append(lexical_diversity(artist_name, lyric_data, save_path))
    paths.append(generate_wordcloud(artist_name, lyric_data, save_path))
    paths.append(musical_feature_scatter(artist_name, spotify_data, save_path))
    paths.append(rank_songs_by(spotify_data, "valence", save_path))
    paths.append(rank_songs_by(spotify_data, "energy", save_path))
    return paths
