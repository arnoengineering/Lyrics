import sys
from datetime import date, datetime
from lyricsgenius import Genius
import os
import pandas as pd
import matplotlib.pyplot as plt


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
genius = Genius(token)

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
            self.search_art()
            self.write_csv()

        else:
            artist_c = pd.read_csv(self.artist, index_col=0)  # reads jason of rand artist
            self.artist_dict = artist_c.to_dict(orient='index')  # will save dict of values

            if 'Album' not in self.artist_dict.keys():  # gets full data if not available
                self.search_art()
                self.write_csv()

        print("{} took {} seconds".format(self.artist, datetime.now() - self.time))  # how long per artist


def count_inst(song, phrase):
    cnt = song['Lyrics'].count(phrase)
    song['Count'] = cnt


def save_me(artist):
    cnt = 0
    total_cnt = 0

    for song in artist:
        count_inst(song, 'Save Me')
        alb = song['Album']
        album_ls[alb][song['Title']] = song['Count']
    for alb in album_ls:
        cnt = sum(album_ls[alb].values())
        album_ls[alb]['Total'] = cnt
        album_ls[alb]['Song Count'] = len(artist)
        album_ls[alb]['Ave'] = cnt / len(artist)

    total_cnt += cnt
    album_ls['Total'] = total_cnt


def plot_artist(artist):
    cnt_ls = {'Totals': [], 'Song Count': [], 'Ave': []}

    for alb in artist.keys():  # creates lists that are able to be ploted
        cnt_ls['Totals'].append(artist[alb]['Total'])
        cnt_ls['Song Count'].append(artist[alb]['Song Count'])
        cnt_ls['Ave'].append(artist[alb]['Ave'])

    plt.figure(1)
    plt.subplot(311).bar(list(artist.keys()), cnt_ls['Totals'])  # lists to plot
    plt.subplot(312).bar(list(artist.keys()), cnt_ls['Ave'])  # lists to plot
    plt.subplot(313).bar(list(artist.keys()), cnt_ls['Song Count'])


def plot_songs(album):  #
    songs = {}
    for song in album.keys():
        if song != 'Total' and song != 'Song Count' and song != 'Ave':
            songs[song['Title']] = song['Count']

    plt.figure(2)
    plt.bar(list(songs.keys()), list(songs.values()))


def stats_alb():
    pass
