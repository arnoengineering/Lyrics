import numpy
import collections
import matplotlib.pyplot as plt
from scipy import stats
from GrabArtist import ReadArtist


class ArtistAn:
    def __init__(self, artist, sort, num=1):
        self.artist = artist
        self.art_dict = {}
        self.stats_ls = ['Mode', 'Se', 'SD']
        self.sort = sort

        self.phrase = 'Save Me'
        self.plt_num = num

    def song_2_alb(self, sort):
        temp_dict = collections.defaultdict(list)
        for song in self.artist.values():
            try:
                song_sort = song.pop(sort)
            except KeyError:
                continue
            temp_dict[song_sort].append(song)

        self.art_dict = {a: {'Songs': s} for a, s in temp_dict.items()}

        # self.art_dict = {song['Album']: {'Songs': ls.append(song.remove(sort))}
        #                  for song in self.artist.values()}

    def count_inst(self, song):
        cnt = song['Lyrics'].lower().count(self.phrase.lower())
        song['Count'] = cnt
        del song['Lyrics']

    def save_me(self):  # for song, artist
        temp_dict = {}
        for alb in self.art_dict.keys():
            if numpy.isnan(alb):
                continue
            print('Alb:', alb)
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
            self.art_dict[alb]['Song Count'] = len(songs)
            self.art_dict[alb]['Ave'] = sum(cnt_ls) / len(songs)
            if sum(cnt_ls) > 0:
                self.plot_in(cnt_ls, self.art_dict[alb])  # one box
                self.plot_songs(songs)
            temp_dict[str(alb)] = self.art_dict[alb]  # only correct get passed

        self.art_dict = temp_dict
        total_cnt = [self.art_dict[x]['Total'] for x in self.art_dict.keys()]
        if len(total_cnt) > 0:
            self.art_dict['Total'] = sum(total_cnt)
            self.art_dict['Ave'] = numpy.average(total_cnt)
            self.plot_in(total_cnt, self.art_dict)
        else:
            print(self.phrase, ' returned none')
            self.plot_artist()

    def plot_in(self, ls, var):  # todo one box
        for x, y in zip(self.stats_ls, stats_alb(ls)):
            var[x] = y

    def plot_artist(self):
        names = [a[0:2] for a in self.art_dict.keys()]
        tot_ls = ['Total', 'Ave', 'Song Count']  # todo if in
        plt_info = {x: self.art_dict.pop(x) for x in tot_ls}
        plt.figure(self.plt_num)
        for num, v in enumerate(self.art_dict, start=311):

            plt.subplot(num).bar(names, [self.art_dict[x][v] for x in self.art_dict.keys()])  # lists to plot
            # subplot.tit = f'{v} vs. alb'
        plot_form(plt_info)
        self.plt_num += 1

    def plot_songs(self, songs):  # subplots
        plt.figure(self.plt_num)
        song_d = {s['Title']: s['Count']for s in songs}
        plt.bar([s[0:2] for s in song_d], list(song_d.values()))
        self.plt_num += 1


def stats_alb(ls):
    mode = stats.mode(ls)
    sd = numpy.std(ls)
    sem = stats.sem(ls)
    return [mode, sd, sem]


def plot_form(info): # , titles, vs):
    # subplot tites, in top
    # todo titiles
    string = 'Stats:\n'
    for x, y in info.items():
        string += f'{x}: {y}\n'
    plt.figtext(0.5, 0, string)


art = ReadArtist('Skillet')
art.test_csv()
# art.search_art()  # test if up
# art.write_csv()
a_d = art.artist_dict


lst = ['Year']
ret_num = 1
for li in lst:
    print('\n\n')
    alb_s = ArtistAn(a_d, li, ret_num)
    alb_s.song_2_alb(li)
    alb_s.save_me()
    ret_num = alb_s.plt_num

plt.show()
