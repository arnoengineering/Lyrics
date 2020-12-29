import numpy
import matplotlib.pyplot as plt
from scipy import stats


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

