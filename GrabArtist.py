import sys
from datetime import date, datetime
from Lyrics import time_dict, token

from lyricsgenius import Genius
import os
import pandas as pd


# save dir
os.chdir(os.path.dirname(sys.argv[0]))
path = os.getcwd()

genius = Genius(token)

# sets day of week to run on sunday, and timing
start_time = datetime.now()
day = date.today()
weekday = day.weekday()

# genius formatting
genius.remove_section_headers = True
genius.skip_non_songs = True
genius.excluded_terms = ["(Remix)"]


class ReadSong:
    def __init__(self, artist, do_all=False):
        self.time = datetime.now()
        self.artist = artist
        self.artist_dict = {}
        self.file_n = artist + ' Songs.csv'

        if do_all:
            self.search_art()
        else:
            self.test_csv()

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
        art_time = datetime.now() - self.time
        per_song = art_time / len(self.artist_dict)
        print("{} took: {} seconds; {} songs at: {} per song".format(self.artist, art_time,
                                                                     len(self.artist_dict), per_song))
        time_dict[self.artist] = {'Time': art_time, 'Songs': len(self.artist_dict), ' Time per Song': per_song}

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

