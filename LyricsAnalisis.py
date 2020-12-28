import sys
from datetime import date, datetime

import numpy
from lyricsgenius import Genius
import os
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats


# save dir
os.chdir(os.path.dirname(sys.argv[0]))
path = os.getcwd()

# tokens
with open('pass.txt', 'r') as f:
    file = f.readlines()
    token = file[1]
    usr = file[3]
    password = file[5]
    receivers = file[7].split(',')  # list of all receivers
genius = Genius(token, timeout=10)

# sets day of week to run on sunday, and timing
start_time = datetime.now()
r_time = start_time
day = date.today()
weekday = day.weekday()

# genius formatting
genius.remove_section_headers = True
genius.skip_non_songs = True
genius.excluded_terms = ["(Remix)"]

# list of artist to search
artist_ls = ["Skillet", "Ledger", "Icon for Hire", "Lacey Sturm"]
album_ls = {}


class ReadSong:
    def __init__(self, artist):
        self.time = datetime.now()
        self.artist = artist
        self.artist_dict = {}
        self.file_n = artist + ' Songs.csv'
        self.csv = True

        # self.test_csv()

    def collect_song_data(self, art_dic):
        dps = []
        title = art_dic['title']  # song title
        url = art_dic['raw']['url']  # spotify url
        art = art_dic['artist']  # artist name(sub_lines)
        song_id = art_dic['raw']['id']  # spotify id
        lyrics = art_dic['lyrics']  # song lyrics
        year = art_dic['year']  # release date
        upload_date = art_dic['raw']['description_annotation']['annotatable']['client_timestamps'][
            'lyrics_updated_at']  # lyrics upload date
        annotations = art_dic['raw']['annotation_count']  # total no. of annotations
        desc = art_dic['raw']['description']  # song descriptions

        dps.append(
            (title, url, art, song_id, lyrics, year, upload_date, annotations, desc))  # append all to one tuple list
        self.artist_dict[title] = dps  # assign list to song dictionary entry named after song title

    def search_art(self):
        art_obj = genius.search_artist(self.artist)  # max songs for debug
        for song in art_obj.songs:
            self.collect_song_data(song)

    def write_csv(self):  # writes all songs for an artist
        df = pd.DataFrame.from_dict(self.artist_dict, orient='index')
        df.to_csv(self.file_n, header=True, index=True)

    def test_csv(self):
        if not os.path.exists(self.file_n):
            self.csv = False
            self.search_art()
            self.write_csv()

        else:
            artist_c = pd.read_csv(self.artist, index_col=0)  # reads jason of rand artist
            self.artist_dict = artist_c.to_dict(orient='index')  # will save dict of values

        print("{} took {} seconds".format(self.artist, datetime.now() - self.time))  # how long per artist


def song_2_alb(artist):
    ls = []
    a_dict = {song['Album']: {'Songs': ls.append({'Title': song['Title'], 'Lyrics': song['Lyrics']})}
              for song in artist.values()}
    return a_dict


def count_inst(song, phrase):
    cnt = song['Lyrics'].count(phrase)
    song['Count'] = cnt
    del song['Lyrics']


def save_me(artist):
    for num, alb in enumerate(artist.keys()):
        songs = alb['Songs']
        for song in songs:
            count_inst(song, 'Save Me')

        cnt_ls = [x['Count'] for x in songs.keys()]

        alb['Total'] = sum(cnt_ls)
        alb['Song Count'] = len(songs)
        alb['Ave'] = sum(cnt_ls) / len(songs)
        alb['Mode'], alb['Sd'], alb['St Er'] = stats_alb(cnt_ls)

        plot_songs(songs, num + 2)

    total_cnt = [x['Total'] for x in artist.keys()]
    plot_artist(artist)

    artist['Total'] = sum(total_cnt)
    artist['Ave'] = numpy.average(total_cnt)
    artist['Mode'], artist['Sd'], artist['Se'] = stats_alb(total_cnt)


def plot_artist(artist):  # if not[:] [x[tot] for x in art]
    plt.figure(1)
    plt.subplot(311).bar(list(artist.keys()), [x['Total'] for x in artist.keys()])  # lists to plot
    plt.subplot(312).bar(list(artist.keys()), [x['Ave'] for x in artist.keys()])  # lists to plot
    plt.subplot(313).bar(list(artist.keys()), [x['Song count'] for x in artist.keys()])


def plot_songs(songs, fig):  #
    plt.figure(fig)
    plt.bar(list(songs.keys()), list(songs.values()))


def stats_alb(ls):
    mode = stats.mode(ls)
    sd = numpy.std(ls)
    sem = stats.sem(ls)
    return mode, sd, sem


sk = ReadSong('Skillet')
sk.search_art()
