import smtplib
import random
import logging
import sys
import os
import re

# email
import ssl
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

# Pandas
import pandas as pd
from GrabLyr import soup_lyrics
from datetime import date, datetime
from lyricsgenius import Genius

# save dir
os.chdir(os.path.dirname(sys.argv[0]))
path = os.getcwd()

# logging
log_name = 'log.log'
logging.basicConfig(filename=log_name, level=logging.INFO)


# tokens
with open('pass.txt', 'r') as f:
    file = f.readlines()
    token = file[1].strip()
    usr = file[3].strip()
    password = file[5].strip()
    receivers = file[7].strip().split(',')  # list of all receivers
genius = Genius(token, timeout=10)

# sets day of week to run on sunday, and timing
start_time = datetime.now()
day = date.today()
weekday = day.weekday()

year = start_time.year  # so gets correct chart
years_80 = list(range(1980, 1990))
years = list(range(year - 5, year + 1))
year_range = [years_80, years]

# genius formatting
genius.remove_section_headers = True
genius.skip_non_songs = True
genius.excluded_terms = ["(Remix)"]
file_pre = ' Songs.csv'
csv_f = 'Time' + file_pre

# list of artist to search
artist_ls = ["Skillet", "LEDGER", "Icon for Hire", "Lacey Sturm"]
time_dict = {}  # initial dict to save info about artists
tot_songs = 0


def collect_song_data(art_dic, artist_dict):  # maybe add more info
    title = art_dic.title  # song title
    art = art_dic.artist
    lyrics = art_dic.lyrics  # song lyrics
    album = art_dic.album

    # assign list to song dictionary entry named after song title
    artist_dict[title] = {'Title': title, 'Artist': art, 'Lyrics': lyrics, 'Album': album}


def write_csv(art, art_dic):  # writes all songs for an artist
    df = pd.DataFrame.from_dict(art_dic, orient='index')
    df.to_csv(art + file_pre, header=True, index=True)


def random_song(art, csv=True):  # returns song with tile artist and lyrics
    try:
        if csv:
            artist_c = pd.read_csv(art + file_pre, index_col=0)  # reads jason of rand artist
            artist = artist_c.to_dict(orient='index')
        else:
            artist = art
        song = random.choice(list(artist.values()))
        print('Random Song: ', song['Title'])
        return song  # returns dict of song
    except (KeyError, FileNotFoundError) as e:
        er_str = 'Error reading {} file; Error: {}'.format(art, e)
        print(er_str)
        logging.error(er_str)
        raise Exception


def random_sub_song(song):  # grabs lines in song
    try:
        max_lines = 5  # max length of lines to send
        lines = re.sub(song['Title'], '***', song['Lyrics'], flags=re.IGNORECASE).splitlines()
    except KeyError:
        er_str = 'Error getting sub-lyrics from: ', song['Title']
        print(er_str)
        logging.error(er_str)

    else:
        # lines are range, thus if les than max, send all
        if len(lines) <= max_lines:
            return song['Lyrics']

        rand_l = random.randint(0, len(lines) - max_lines)
        sub_line = '\n'.join(lines[rand_l:rand_l + max_lines])
        return sub_line


def rand_song_lyrics():  # runs module to scrape soup
    artist_dict = {}
    soup_st = datetime.now()
    song = soup_lyrics(year_range)  # gets random song per chart
    soup_time = datetime.now()
    soup_song = genius.search_song(song['song'], song['artist'], get_full_info=False)

    print('Got Billboard Song in: {}, Genies search in: {}'.format(soup_time - soup_st, datetime.now() - soup_time))
    collect_song_data(soup_song, artist_dict)
    artist_dict = artist_dict[soup_song.title]  # could use song, but want to avoid err

    try:  # adds extra info for random songs
        artist_dict['Genre'],  artist_dict['Rank'], artist_dict['Year'] = song['name'], song['rank'], song['year']
    except Exception as e:
        print(e)
        logging.error(e)
        raise KeyError(e)

    print('Random Song: ', artist_dict['Title'])
    return artist_dict


def log_clear():  # sends mail with logfile, then removes it
    if os.path.exists(log_name):
        SendEmail(file_attach=log_name)
        with open(log_name, 'w') as log:
            log.truncate(0)


def grab_artist(art, ret=False):
    # grabs songs from artist if update needed
    global tot_songs
    artist_dict = {}
    r_time = datetime.now()
    art_obj = genius.search_artist(art, get_full_info=True)  # max songs for debug

    for songs in art_obj.songs:  # loops though for each song
        collect_song_data(songs, artist_dict)

    write_csv(art, artist_dict)
    art_time = datetime.now() - r_time
    per_song = art_time / len(artist_dict)
    tot_songs += len(artist_dict)
    print("{} took: {} seconds; {} songs at: {} per song".format(art, art_time, len(artist_dict), per_song))
    time_dict[art] = {'Time': art_time, 'Songs': len(artist_dict), ' Time per Song': per_song}
    if ret:
        return artist_dict  # so don't have to read csv


def search_csv(art_li):
    # checks to see if csv exists or if update needed
    if os.path.exists(rand_art + file_pre):  # for rand song if in dir
        out_song = random_song(rand_art)
    else:
        art_dict = grab_artist(rand_art, ret=True)
        out_song = random_song(art_dict, csv=False)

    for art in art_li:  # loop though all see if in dir and not one before
        a_file = art + file_pre
        if not os.path.exists(a_file) and art != rand_art:
            grab_artist(art)
    return out_song


# Email Output
class SendEmail:
    def __init__(self, sub_lyr='', s_info=None, file_attach=''):
        if s_info is None:
            s_info = {}
        self.sub_lyr = sub_lyr
        self.s_info = s_info

        self.file = file_attach

        # Google location
        self.host_server = "smtp.gmail.com"
        self.port = 465
        self.msg = MIMEMultipart('alternative')
        self.num = 0

        # what to send
        self.msg['From'] = usr
        self.hint_ls = ['Album', 'Rank', 'Genre']

        if len(self.file) > 0:  # if to send file, will send to first inbox else run normal
            self.attach_email()
            self.receivers = [receivers[0]]

        else:
            self.receivers = receivers
            self.html()
        self.msg['To'] = ', '.join(self.receivers)  # to get string
        self.email_base()

    def hints(self):  # adds to lyrics so hint can be displayed
        hint_tot = """"""

        for hint in self.hint_ls:
            self.num += 1
            if hint in self.s_info.keys():
                hint_box = """
                        <tr>
                        <td>
                        <input type="checkbox" id="handle{num}" />
                        <label for="handle{num}">
                        {hint}
                        </label>

                      <div class="content">
                        <p> {hint}: {h_val}</p>
                      </div>
                      </td>
                      </tr>""".format(num=self.num, hint=hint, h_val=self.s_info[hint])
                hint_tot += ' \n' + hint_box
        return hint_tot

    def attach_email(self):  # adds attachments to email if needed
        if os.path.exists(self.file):
            self.msg['Subject'] = 'Lyrics Data Attachment'
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(open(self.file, 'rb').read())

            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment', filename=self.file)
            self.msg.attach(part)

    def html(self):  # formats the message
        self.msg['Subject'] = 'Lyrics'
        message_con = "Lyrics:\n {}".format(self.sub_lyr)  # if format won't load

        self.msg.attach(MIMEText(message_con, 'plain'))
        print('opening html')
        try:
            with open('LyEmail.html', 'r') as h_file:
                # replaces items so html works on qwn, but can format
                html = h_file.read().replace('{', '{{').replace('}', '}}').replace('%#', '{').replace('#%', '}')
                html = html.replace('<!--{', '{').replace('}-->', '}')
            self.num = html.count('handle')  # counts instances already

            html_ex = self.hints()
            form_html = html.format(lyrics=self.sub_lyr, title=self.s_info['Title'], artist=self.s_info['Artist'],
                                    full_lyrics=self.s_info['Lyrics'], extra_info=html_ex)

            self.msg.attach(MIMEText(form_html, 'html'))
        except KeyError as e:
            print('Error Formatting HTML: ', e)

    def email_base(self):  # sends message

        ctx = ssl.create_default_context()
        print('Sending Email')

        with smtplib.SMTP_SSL(self.host_server, self.port, context=ctx) as server:
            server.login(usr, password)

            for receiver in self.receivers:
                e_time = datetime.now()
                server.sendmail(usr, receiver, self.msg.as_string())
                print('Time for Email: {}, {}'.format(receiver, datetime.now() - e_time))


rand_art = random.choice(artist_ls)  # index columns so dict is correct
if weekday == 6:
    SendEmail(file_attach=csv_f)  # runs csv email
    log_clear()  # runs log email
    try:
        rand_out = rand_song_lyrics()  # runs module to check songs, then gets sub song
    except KeyError as er:
        print('Error loading song, KeyError: ', er)
        fail = True
        grab_artist(rand_art, ret=True)
        rand_out = random_song(rand_art)
    else:
        grab_artist(rand_art)
        # run to grab on sat
    for artists in artist_ls:
        if artists != rand_art:
            grab_artist(artists)
else:
    SendEmail(file_attach=csv_f)  # runs csv email
    log_clear()
    rand_out = search_csv(artist_ls)

sub_lines = random_sub_song(rand_out)  # gets sub_lyrics
SendEmail(sub_lines, rand_out)
tot_time = datetime.now() - start_time

try:
    tps = tot_time / tot_songs
except ZeroDivisionError:
    tps = 0
time_dict['Total'] = {'Time': tot_time, 'Songs': tot_songs, 'Time per Song': tps}
if tot_songs > 0:
    write_csv('Time', time_dict)  # since index is run by dict and 'art' is name

print("Total time:",  tot_time)
print("{} Songs, at: {} per song".format(tot_songs, tps))
