import numpy

import matplotlib.pyplot as plt
from scipy import stats


class ArtistAn:
    def __init__(self, artist, num=1):
        self.artist = artist
        self.art_dict = {}
        self.phrase = 'Save Me'
        self.plt_num = num

    def song_2_alb(self, sort):
        ls = []
        self.art_dict = {song['Album']: {'Songs': ls.append(song.remove(sort))}
                         for song in self.artist.values()}

    def count_inst(self, song):
        cnt = song['Lyrics'].count(self.phrase)
        song['Count'] = cnt
        del song['Lyrics']

    def save_me(self):  # for song, artist
        for alb in self.artist.keys():
            songs = alb['Songs']
            for song in songs:
                self.count_inst(song)

            cnt_ls = [x['Count'] for x in songs.keys()]

            alb['Total'] = sum(cnt_ls)
            alb['Song Count'] = len(songs)
            alb['Ave'] = sum(cnt_ls) / len(songs)
            alb['Mode'], alb['Sd'], alb['St Er'] = stats_alb(cnt_ls)

            plot_songs(songs, self.plt_num + 1)

        total_cnt = [x['Total'] for x in self.artist.keys()]
        plot_artist(self.artist, self.plt_num)
        self.plt_num += 1
        self.artist['Total'] = sum(total_cnt)
        self.artist['Ave'] = numpy.average(total_cnt)
        self.artist['Mode'], self.artist['Sd'], self.artist['Se'] = stats_alb(total_cnt)


def plot_artist(artist, num):
    plt.figure(num)
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


art = {}  # readcsv 'Skillet'
lst = ['Album', 'Year']
ret_num = 1
for x in lst:
    alb_s = ArtistAn(art, ret_num)
    alb_s.song_2_alb(x)
    alb_s.save_me()
    ret_num = alb_s.plt_num
plt.show()
