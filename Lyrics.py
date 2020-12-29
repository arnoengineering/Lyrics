import random
import logging
import sys
import os
import re

# email
import smtplib
import ssl
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

# Pandas
from Creds import *
import GrabArtist
from GrabLyr import soup_lyrics
from datetime import date, datetime


# save dir
os.chdir(os.path.dirname(sys.argv[0]))
path = os.getcwd()

# logging
log_name = 'log.log'
logging.basicConfig(filename=log_name, level=logging.INFO)


# sets day of week to run on sunday, and timing
start_time = datetime.now()
day = date.today()
weekday = day.weekday()

year = start_time.year  # so gets correct chart
years_80 = list(range(1980, 1990))
years = list(range(year - 5, year + 1))
year_range = years_80 + years

file_pre = ' Songs.csv'
csv_f = 'Time' + file_pre

# list of artist to search
artist_ls = ["Skillet", "LEDGER", "Icon for Hire", "Lacey Sturm"]
time_dict = {}  # initial dict to save info about artists
tot_songs = 0
files = [csv_f]  # list top send
rand_art = random.choice(artist_ls)  # index columns so dict is correct


def random_song(artist):  # returns song with tile artist and lyrics
    try:
        song = random.choice(list(artist.values()))
        print('Random Song: ', song['Title'])
        return song  # returns dict of song
    except KeyError as e:
        print(e)
        logging.error(e)
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


def rand_soup_lyrics():  # runs module to scrape soup,
    soup_st = datetime.now()
    song = soup_lyrics(year_range)  # gets random song per chart
    soup_time = datetime.now()
    artist_dict = GrabArtist.genius_find(song['song'], song['artist'])

    print('Got Billboard Song in: {}, Genies search in: {}'.format(soup_time - soup_st, datetime.now() - soup_time))
    artist_dict = artist_dict[song['song']]

    try:  # adds extra info for random songs
        artist_dict['Genre'], artist_dict['Rank'] = song['genre'], song['rank']
    except Exception as e:
        print(e)
        logging.error(e)
        raise KeyError(e)

    print('Random Song: ', artist_dict['Title'])
    return artist_dict


def log_clear():  # sends mail with logfile, then removes it
    if os.path.exists(os.path.join(path, log_name)):
        with open(log_name, 'r') as log:
            lines = len(log.readlines())
        if lines > 0:
            files.append(log_name)
        SendEmail(file_attach=files)
        with open(log_name, 'w') as log:
            log.truncate(0)
    else:
        SendEmail(file_attach=files)


# Email Output
class SendEmail:
    def __init__(self, sub_lyr='', info=None, file_attach=None):
        if file_attach is None:
            file_attach = []
        if info is None:
            info = {}
        self.sub_lyr = sub_lyr
        self.s_info = info

        self.files = file_attach

        # Google location
        self.host_server = "smtp.gmail.com"
        self.port = 465
        self.msg = MIMEMultipart('alternative')
        self.num = 0

        # what to send
        self.msg['From'] = usr
        self.hint_ls = ['Album', 'Rank', 'Genre', 'Year']

        if len(self.files) > 0:  # if to send file, will send to first inbox else run normal
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
        self.msg['Subject'] = 'Lyrics Data Attachment'
        message_con = 'Lyrics Data Attachment\n'
        for fi in self.files:
            fi_path = os.path.join(path, fi)

            if os.path.exists(fi_path):
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(open(fi, 'rb').read())

                encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment', filename=fi)
                self.msg.attach(part)
            else:
                message_con += f'Error finding: {fi}\n'
            self.msg.attach(MIMEText(message_con, 'plain'))

    def html(self):  # formats the message
        self.msg['Subject'] = 'Lyrics'
        message_con = "Lyrics:\n {}".format(self.sub_lyr)  # if format won't load

        self.msg.attach(MIMEText(message_con, 'plain'))
        print('opening html')
        try:
            with open('LyrEmail.html', 'r') as h_file:
                # replaces items so html works on qwn, but can format
                html = h_file.read().replace('{', '{{').replace('}', '}}').replace('%#', '{').replace('#%', '}')
                html = html.replace('<!--{', '{').replace('}-->', '}')
            self.num = html.count('handle')  # counts instances already

            html_ex = self.hints()
            form_html = html.format(lyrics=self.sub_lyr, title=self.s_info['Title'], artist=self.s_info['Artist'],
                                    full_lyrics=self.s_info['Lyrics'], extra_info=html_ex)

            self.msg.attach(MIMEText(form_html, 'html'))
        except (KeyError, FileNotFoundError) as e:
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


def loop_artists(do_all=False):
    a_dict = {}  # returns dict at end only if required
    for art in artist_ls:
        a = GrabArtist.ReadArtist(art)
        if do_all:
            a.search_art()
            time_dict[art] = a.artist_time
        else:
            a.test_csv()
        if art == rand_art:
            a_dict = a.artist_dict
    return a_dict


if weekday == 6:
    log_clear()  # runs log email
    try:
        rand_out = rand_soup_lyrics()  # runs module to check songs, then gets sub song
    except KeyError as er:
        print('Error loading song, KeyError: ', er)
        fail = True
        art_dict = loop_artists(True)
        rand_out = random_song(art_dict)
    else:
        loop_artists(True)
        # run to grab on sat
else:
    art_dict = loop_artists()
    rand_out = random_song(art_dict)

sub_lines = random_sub_song(rand_out)  # gets sub_lyrics
SendEmail(sub_lines, rand_out)
tot_time = datetime.now() - start_time

tot_songs = sum([art['Songs'] for art in time_dict])
try:
    tps = tot_time / tot_songs
except ZeroDivisionError:
    tps = 0
time_dict['Total'] = {'Time': tot_time, 'Songs': tot_songs, 'Time per Song': tps}
if tot_songs > 0:
    t_obj = GrabArtist.ReadArtist('Time')
    t_obj.write_csv()

print("Total time:",  tot_time)
print("{} Songs, at: {} per song".format(tot_songs, tps))
