import numpy
import collections
import matplotlib.pyplot as plt
from scipy import stats
from GrabArtist import ReadArtist


class ArtistAn:
    def __init__(self, artist, sort, num=1):
        self.artist = artist
        self.art_dict = {}
        self.stats_ls = ['Count', 'Total', 'Ave', 'Mode', 'Se', 'SD']
        self.sort = sort

        self.phrase = 'Save Me'
        self.plt_num = num

    def song_2_alb(self):
        temp_dict = collections.defaultdict(list)
        for song in self.artist.values():
            try:
                song_sort = song.pop(self.sort)
            except KeyError:
                continue
            temp_dict[song_sort].append(song)

        s_dict = {a: {'Songs': s} for a, s in temp_dict.items()}
        type_x = lambda x: type(x) == float
        if all([type_x(x) for x in s_dict.items()]):
            self.art_dict = {x: y for x, y in sorted(s_dict.items())}
        else:
            self.art_dict = s_dict

    def count_inst(self, song):
        cnt = song['Lyrics'].lower().count(self.phrase.lower())
        song['Count'] = cnt
        del song['Lyrics']

    def save_me(self):  # for song, artist
        temp_dict = {}
        for alb in self.art_dict.keys():
            if alb == float:
                if numpy.isnan(alb):
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

            temp_dict[str(alb)] = self.art_dict[alb]  # only correct get passed

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

    def plot_form(self, info):
        string = 'Stats:\n'
        t_in = {x: info[x] for x in self.stats_ls}
        for x, y in t_in.items():
            string += f'{x}: {y}\n'
        plt.figtext(0.5, 0, string)

    def names_list(self, ls):
        n_list = [a[0:2] for a in ls.keys() if a not in self.stats_ls]
        d_no_e = {x: y for x, y in ls.items() if x not in self.stats_ls}
        return n_list, d_no_e

    def plot_artist(self):
        tot_ls = ['Total', 'Ave', 'Count']  # todo if in, creat temp dict to plot
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
                plt.figure(self.plt_num)
                self.plot_form(songs)
                self.plt_num += 1
                # rem alb ex
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


def stats_alb(ls):
    cnt = len(ls)
    tot = sum(ls)
    mode = stats.mode(ls)[0][0]
    av = numpy.average(ls)
    sd = numpy.std(ls)
    sem = stats.sem(ls)
    return [cnt, tot, av, mode, sd, sem]


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
