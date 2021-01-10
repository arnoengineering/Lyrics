from datetime import datetime
from Creds import token, csv_pre

from lyricsgenius import Genius
import os
import pandas as pd

genius = Genius(token, timeout=10)
path = 'Songs/'
# genius formatting
genius.remove_section_headers = True
genius.skip_non_songs = True
genius.excluded_terms = ["(Remix)"]


class ReadArtist:
    def __init__(self, artist):
        self.time = datetime.now()
        self.artist = artist
        self.artist_dict = {}
        self.file_n = path + artist + csv_pre
        self.artist_time = {}

    def collect_song_data(self, song_obj):

        song_dict = song_obj.to_dict()

        song_dict['artist'] = self.artist
        if type(song_dict['year']) == float:
            str(song_dict['year'])
        if song_dict['year'] == 'nan':
            float(song_dict['year'])
        if type(song_dict['year']) == str:
            song_dict['year'] = song_dict['year'].split('-')[0]  # only year not day
            song_dict['year'] = song_dict['year'].split('.')[0]

        med = song_obj.media  # list of media
        if med is not None:
            for m in med:
                if m['provider'] == 'spotify':  # adds url to list
                    url = m['url']
                    song_dict['url'] = url

        if type(song_dict['album']) == float:
            del song_dict['album']
        # assign list to song dictionary entry named after song title
        self.artist_dict[song_dict['title']] = {x.title(): y for x, y in song_dict.items()}

    def search_art(self):
        art_obj = genius.search_artist(self.artist)  # max songs for debug
        for song in art_obj.songs:
            self.collect_song_data(song)

        art_time = datetime.now() - self.time
        per_song = art_time / len(self.artist_dict)
        print("{} took: {} seconds; {} songs at: {} per song".format(self.artist, art_time,
                                                                     len(self.artist_dict), per_song))
        self.artist_time = {'Time': art_time, 'Songs': len(self.artist_dict), ' Time per Song': per_song}

    def write_csv(self):  # writes all songs for an artist_d
        df = pd.DataFrame.from_dict(self.artist_dict, orient='index')
        df.to_csv(self.file_n, header=True, index=True)

    def test_csv(self):
        if not os.path.exists(self.file_n):
            self.search_art()
            self.write_csv()

        else:
            artist_c = pd.read_csv(self.file_n, index_col=0)  # reads jason of rand artist_d
            self.artist_dict = artist_c.to_dict(orient='index')  # will save dict of values


def genius_find(title, artist, full=False):
    gen_obj = genius.search_song(title, artist, get_full_info=full)
    gen = ReadArtist(artist)
    gen.collect_song_data(gen_obj)
    return gen.artist_dict
