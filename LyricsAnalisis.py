import numpy
import collections
import matplotlib.pyplot as plt
from scipy import stats
from GrabArtist import ReadArtist


class ArtistAn:
    def __init__(self, artist, sort, num=1):
        self.artist = artist
        self.art_dict = {}
        self.sort = sort

        self.phrase = 'Save Me'
        self.plt_num = num

    def song_2_alb(self, sort):
        temp_dict = collections.defaultdict(list)
        for song in self.artist.values():
            try:
                song_sort = song.pop(sort)
            except KeyError:
                pass
            else:
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
            if type(alb) == float:
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
            self.art_dict[alb]['Mode'], self.art_dict[alb]['Sd'], self.art_dict[alb]['St Er'] = stats_alb(cnt_ls)

            plot_songs(songs, self.plt_num)
            temp_dict[alb] = self.art_dict[alb]  # only correct get passed

        self.art_dict = temp_dict
        total_cnt = [self.art_dict[x]['Total'] for x in self.art_dict.keys()]
        if len(total_cnt) > 0:
            plot_artist(self.art_dict, self.plt_num)
            self.art_dict['Total'] = sum(total_cnt)
            self.art_dict['Ave'] = numpy.average(total_cnt)
            self.art_dict['Mode'], self.art_dict['Sd'], self.art_dict['Se'] = stats_alb(total_cnt)
        else:
            print(self.phrase, ' returned none')


def plot_artist(artist, num):
    names = [a[0:2] for a in artist.keys()]
    plt.figure(num)
    plt.subplot(311).bar(names, [artist[x]['Total'] for x in artist.keys()])  # lists to plot
    plt.subplot(312).bar(names, [artist[x]['Ave'] for x in artist.keys()])  # lists to plot
    plt.subplot(313).bar(names, [artist[x]['Song Count'] for x in artist.keys()])
    num += 1


def plot_songs(songs, fig):  # subplots
    plt.figure(fig)
    song_d = {s['Title']: s['Count']for s in songs}
    plt.bar([s[0:2] for s in song_d], list(song_d.values()))
    fig += 1


def stats_alb(ls):
    mode = stats.mode(ls)
    sd = numpy.std(ls)
    sem = stats.sem(ls)
    return mode, sd, sem


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
