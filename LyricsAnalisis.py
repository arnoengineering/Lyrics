from datetime import date, datetime
from lyricsgenius import Genius
import os
import pandas as pd


# save dir
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
file_pre = ' Songs'

# list of artist to search
artist_ls = ["Skillet", "Ledger", "Icon for Hire", "Lacey Sturm"]
album_ls = {}


class ReadSong:
    def __init__(self):
        self.artist = ''
        self.artist_dict = {}
        self.file_n = '{} Songs.json'.format('')  # todo fix for loop

    def init_artist(self, artist):
        self.artist = artist
        self.artist_dict = {}
        self.file_n = '{} Songs.json'.format(artist)

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
        descr = art_dic['raw']['description']  # song descriptions

        dps.append(
            (title, url, art, song_id, lyrics, year, upload_date, annotations, descr))  # append all to one tuple list
        self.artist_dict[title] = dps  # assign list to song dictionary entry named after song title

    def search_art(self):
        art_obj = genius.search_artist(self.artist, max_songs=3)  # max songs for debug
        # art_obj.save_lyrics(filename=self.file_n, overwrite=True) # todo Point?
        for song in art_obj.songs:
            self.collect_song_data(song)

    def write_csv(self):  # writes all songs for an artist
        df = pd.DataFrame.from_dict(self.artist_dict, orient='index')
        df.to_csv('{}{}.csv'.format(self.artist, file_pre), header=True, index=True)

    def test_csv(self):
        for a in artist_ls:
            if not os.path.exists(a):
                self.search_art()
                self.write_csv()

            else:  # todo change if not read first
                artist_c = pd.read_csv('{}{}.csv'.format(a, file_pre), index_col=0)  # reads jason of rand artist
                self.artist_dict = artist_c.to_dict(orient='index')  # will save dict of values

    # write_csv(artists, artist_dict)
    for artists in artist_ls:
        print("{} took {} seconds".format(artists, datetime.now() - r_time))  # how long per artist
        r_time = datetime.now()

    print("Total time: ", datetime.now() - start_time)  # todo return so I can mod data


def count_inst(song, phrase):
    cnt = song['Lyrics'].count(phrase)
    song['Count'] = cnt


def save_me(artist):
    for song in artist:
        count_inst(song, 'Save Me')
        alb = song['Album']
        if alb not in album_ls.keys():
            album_ls[alb] = 0
        album_ls[alb] += 1
    total = sum(album_ls.values())
    album_ls['Total'] = total
