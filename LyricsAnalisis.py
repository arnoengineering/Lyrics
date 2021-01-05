import numpy
from logging import INFO
import logging
import collections
import matplotlib.pyplot as plt
from scipy import stats
from GrabArtist import ReadArtist
logging.basicConfig(filename='log.log', level=INFO)


class ArtistAn:
    def __init__(self, artist, sort, num=1, lots_info=True):

        self.artist = artist  # initial dict
        self.art_dict = {}  # dict that gets edited
        self.stats_ls = ['Count', 'Total', 'Ave', 'Mode', 'Se', 'SD']
        self.sort = sort  # by what to sort data
        self.lots_info = lots_info  # if songs to be plotted

        self.phrase = 'Save Me'  # phrase to search for
        self.plt_num = num  # num to hold figure

    def song_2_alb(self):
        # temp dict to switch keys
        temp_dict = collections.defaultdict(list)
        for song in self.artist.values():
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

    def save_me(self):  # for song, artist
        temp_dict = {}
        for alb in self.art_dict.keys():
            if alb == 'nan':
                continue
            print(alb)
            songs = self.art_dict[alb]['Songs']
            for song in songs:
                if type(song['Lyrics']) == float:
                    songs.remove(song)
                    continue
                self.count_inst(song)

            if len(songs) == 0:
                continue
            cnt_ls = [x['Count'] for x in songs]
            self.art_dict[alb]['Total'] = sum(cnt_ls)

            self.plot_in(cnt_ls, self.art_dict[alb])  # one box

            temp_dict[alb] = self.art_dict[alb]  # only correct get passed

        self.art_dict = temp_dict
        total_cnt = [self.art_dict[x]['Total'] for x in self.art_dict.keys()]
        if len(total_cnt) > 0:
            self.plot_in(total_cnt, self.art_dict)
            self.plot_artist()
            self.plot_songs()

    def plot_in(self, ls, var):  # todo one box
        if len(ls) > 0:
            for x, y in zip(self.stats_ls, stats_alb(ls)):
                var[x] = y
        else:
            for x in self.stats_ls:
                var[x] = 0

    def plot_form(self, info, ax=None):
        string = 'Stats:\n'
        t_in = {x: info[x] for x in self.stats_ls}
        for x, y in t_in.items():
            string += f'{x}: {y :.3f}\n'
        if ax is None:
            plt.figtext(0.5, 0, string)
        else:
            ax.text(0.5, 0, string)

    def names_list(self, ls):
        n_list = [a[0:2] for a in ls.keys() if a not in self.stats_ls]
        d_no_e = {x: y for x, y in ls.items() if x not in self.stats_ls}
        return n_list, d_no_e

    def plot_artist(self):
        tot_ls = ['Total', 'Ave', 'Count']
        names, temp_d = self.names_list(self.art_dict)
        plt.figure(self.plt_num)
        plt.title(f'Album stats: {self.sort}')
        for num, v in enumerate(tot_ls, start=311):  # lists to plot
            ax = plt.subplot(num)
            ax.set_title(f'{v} per alb')
            ax.set_xlabel('Albums')
            ax.set_ylabel(v)
            ax.bar(names, [temp_d[x][v] for x in temp_d.keys()])
        self.plot_form(self.art_dict)
        self.plt_num += 1

    def plot_songs(self,):  # subplots
        alb_len = len(self.art_dict)
        si, rem = divmod(alb_len, 6)  # 3x2
        size = si * 6
        t_d = {x: y for x, y in self.art_dict.items() if x not in self.stats_ls}

        for num, alb in enumerate(t_d, start=0):

            songs = self.art_dict[alb]

            song_d = {s['Title']: s['Count'] for s in songs['Songs']}
            names, temp_d = self.names_list(song_d)
            n = num % 6

            if n == 0:
                # save_p()
                plt.figure(self.plt_num)
                self.plt_num += 1
                # rem alb ex
                # t =
                plt.title('Count vs song:\n Alb:{}-{}'.format(num, num + 6))
            if num <= size:
                dim = 321 + n
            else:
                dim = rem * 100 + 11 + n

            ax = plt.subplot(dim)
            ax.set_title(alb)
            ax.set_xlabel('Songs')
            ax.set_ylabel(f'Counts: {self.phrase}')
            ax.bar(names, list(temp_d.values()))  # names
            self.plot_form(songs, ax=ax)


def stats_alb(ls):
    cnt = len(ls)
    tot = sum(ls)
    mode = stats.mode(ls)[0][0]
    av = numpy.average(ls)
    sd = numpy.std(ls)
    sem = stats.sem(ls)
    return [cnt, tot, av, mode, sd, sem]


def save_p(pl):
    name = pl.title + '.png'
    # name = os.path.join(path, name)
    plt.savefig(name)


art = ReadArtist('Skillet')
art.test_csv()


lst = ['Album', 'Year']
ret_num = 1
for li in lst:
    print('\n\n')
    art.test_csv()
    a_d = art.artist_dict
    alb_s = ArtistAn(a_d, li, ret_num)
    alb_s.song_2_alb()
    alb_s.save_me()
    ret_num = alb_s.plt_num

plt.show()
