import numpy
from logging import INFO
import logging
import collections
import matplotlib.pyplot as plt
from scipy import stats
from GrabArtist import ReadArtist
import os

# start
logging.basicConfig(filename='log.log', level=INFO)
path = os.getcwd()
plot_dir = os.path.join(path, 'Plots')  # create dir for plots
if not os.path.exists(plot_dir):
    os.mkdir(plot_dir)

artists = ['Skillet']
sort_ls = ['Album', 'Year']


class ArtistAn:
    def __init__(self, art_name, artist_d, sort, num=1, lots_info=True):

        self.artist_d_in = artist_d  # initial dict
        self.art_name = art_name
        self.art_dict = {}  # dict that gets edited
        self.stats_ls = ['Count', 'Total', 'Ave', 'Mode', 'Se', 'SD']
        self.sort = sort  # by what to sort data
        self.lots_info = lots_info  # if songs to be plotted

        self.phrase = 'Save Me'  # phrase to search for
        self.plt_num = num  # num to hold figure

    def song_2_alb(self):
        # temp dict to switch keys
        temp_dict = collections.defaultdict(list)
        for song in self.artist_d_in.values():
            try:
                song_sort = song.pop(self.sort)
            except KeyError:
                continue
            temp_dict[song_sort].append(song)

        s_dict = {str(a): {'Songs': s} for a, s in temp_dict.items()}  # sorting

        self.art_dict = {x: s_dict[x] for x in sorted(s_dict.keys())}

    def count_inst(self, song):
        cnt = song['Lyrics'].lower().count(self.phrase.lower())
        song['Count'] = cnt
        del song['Lyrics']

    def save_me(self):  # for song, artist_d
        temp_dict = {}
        for alb in self.art_dict.keys():  # skip songs with no data
            if alb == 'nan':
                continue
            print(alb)
            songs = self.art_dict[alb]['Songs']

            for song in songs:  # skip songs with no data
                if type(song['Lyrics']) == float:
                    songs.remove(song)
                    continue
                self.count_inst(song)

            if len(songs) != 0:
                cnt_ls = [x['Count'] for x in songs]
                self.art_dict[alb]['Total'] = sum(cnt_ls)

                self.get_stats(cnt_ls, self.art_dict[alb])  # one box
                temp_dict[alb] = self.art_dict[alb]  # only correct get passed

        self.art_dict = temp_dict
        total_cnt = [self.art_dict[x]['Total'] for x in self.art_dict.keys()]  # only plot if data
        if len(total_cnt) > 0:
            self.get_stats(total_cnt, self.art_dict)
            self.plot_alb()
            self.plot_songs()

    def get_stats(self, ls, var):  # gets extra stats or saves as 0
        if len(ls) > 0:  # if elements in list get stats
            for x, y in zip(self.stats_ls, stats_alb(ls)):
                var[x] = y
        else:
            for x in self.stats_ls:
                var[x] = 0

    def plot_form(self, info, ax=None):  # formats plots
        string = 'Stats:\n'
        t_in = {x: info[x] for x in self.stats_ls}
        for x, y in t_in.items():
            string += f'{x}: {y :.3f}\n'

        # if no ax is given then save each then plot global
        if ax is None:
            plt.figtext(0.5, 0, string)
        else:
            ax.text(0.5, 0, string)

    def names_list(self, ls):
        n_list = [a[0:2] for a in ls.keys() if a not in self.stats_ls]
        d_no_e = {x: y for x, y in ls.items() if x not in self.stats_ls}
        return n_list, d_no_e

    def plot_alb(self):  # plot data for total album
        tot_ls = ['Total', 'Ave', 'Count']
        names, temp_d = self.names_list(self.art_dict)
        plt.figure(self.plt_num)
        tit = f'Album stats: {self.sort}'
        plt.title(tit)

        for num, v in enumerate(tot_ls, start=311):  # lists to plot
            ax = plt.subplot(num)
            ax.set_title(f'{v} per alb')
            ax.set_xlabel('Albums')
            ax.set_ylabel(v)
            ax.bar(names, [temp_d[x][v] for x in temp_d.keys()])
        self.plot_form(self.art_dict)
        self.save_p(tit.split(':')[0])
        self.plt_num += 1

    def save_p(self, ti):
        f_dir = os.path.join(plot_dir, self.sort, self.art_name)  # dir per art

        if not os.path.exists(f_dir):
            os.mkdir(f_dir)

        name = ti + '.png'
        name = os.path.join(f_dir, name)

        try:
            plt.savefig(name)
        except FileExistsError:
            print(ti, ' Already exists')

    def plot_songs(self,):  # subplots
        alb_len = len(self.art_dict)
        si, rem = divmod(alb_len, 6)  # 3x2
        size = si * 6  # sizing
        t_d = {x: y for x, y in self.art_dict.items() if x not in self.stats_ls}
        tit = 'Alb'

        for num, alb in enumerate(t_d, start=0):

            songs = self.art_dict[alb]

            song_d = {s['Title']: s['Count'] for s in songs['Songs']}
            names, temp_d = self.names_list(song_d)
            tit = 'Count vs song:\n Alb:{}-{}'.format(num, num + 6)  # title to reference later
            n = num % 6

            if n == 0:
                if num != 0:  # saves all plots
                    self.save_p(tit.split('\n')[1].replace(':', ' '))
                plt.figure(self.plt_num)
                self.plt_num += 1
                # rem alb ex
                # t =
                plt.title(tit)
            if num <= size:
                dim = 321 + n
            else:
                dim = rem * 100 + 11 + n

            ax = plt.subplot(dim)  # formatting
            ax.set_title(alb)
            ax.set_xlabel('Songs')
            ax.set_ylabel(f'Counts: {self.phrase}')
            ax.bar(names, list(temp_d.values()))  # names
            self.plot_form(songs, ax=ax)
        self.save_p(tit.split('\n')[1].replace(':', ' '))  # saves last


def stats_alb(ls):
    cnt = len(ls)
    tot = sum(ls)
    mode = stats.mode(ls)[0][0]
    av = numpy.average(ls)
    sd = numpy.std(ls)
    sem = stats.sem(ls)
    return [cnt, tot, av, mode, sd, sem]


def plot_art(ar, r_num):
    art = ReadArtist(ar)
    art.test_csv()
    for li in sort_ls:
        print('\n\n')
        art.test_csv()
        a_d = art.artist_dict
        alb_s = ArtistAn(ar, a_d, li, r_num)
        alb_s.song_2_alb()
        alb_s.save_me()
        r_num = alb_s.plt_num

        # saves
        art.artist_dict = alb_s.art_dict
        art.file_n = f'Stats, Art: {ar}, {li}.csv'
        art.write_csv()


ret_num = 1
for arti in artists:
    plot_art(arti, ret_num)

show = input('Show Plots? (y/n)')
if show.lower() == 'y':
    plt.show()
