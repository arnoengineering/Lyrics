import smtplib
import random
from datetime import date, datetime
import ssl
from lyricsgenius import Genius
import os
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from GrabLyr import soup_lyrics
import re

# todo
"""todo add different years
return e when error"""
# save dir
path = os.getcwd()

# tokens
with open('pass.txt', 'r') as f:
    file = f.readlines()
    token = file[1]
    usr = file[3]
    password = file[5]
    receivers = file[7].split(',')  # list of all receivers
genius = Genius(token)

# sets day of week to run on sunday, and timing
start_time = datetime.now()
day = date.today()
weekday = day.weekday()
year = start_time.year  # so gets correct chart
tot_songs = 0

# genius formatting
genius.remove_section_headers = True
genius.skip_non_songs = True
genius.excluded_terms = ["(Remix)"]
file_pre = ' Songs.csv'

# list of artist to search
artist_ls = ["Skillet", "LEDGER", "Icon for Hire", "Lacey Sturm"]
time_dict = {}  # initial dict to save info about artists


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
        print('Error reading {} file; Error: {}'.format(art, e))
        raise Exception


def random_sub_song(song):  # grabs lines in song
    try:  # {'Ti': t, 'lyr', artist}
        max_lines = 5  # max length of lines to send
        lines = re.sub(song['Title'], '***', song['Lyrics'], flags=re.IGNORECASE).splitlines()
    except KeyError:
        print('Error getting sub-lyrics from: ', song['Title'])
        pass
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
    song = soup_lyrics(year)  # gets random song per chart
    soup_time = datetime.now()
    soup_song = genius.search_song(song['song'], song['artist'], get_full_info=False)

    print('Got Billboard Song in: {}, Genies search in: {}'.format(soup_time - soup_st, datetime.now() - soup_time))
    collect_song_data(soup_song, artist_dict)
    artist_dict = artist_dict[soup_song.title]  # could use song, but want to avoid err

    try:  # adds extra info for random songs
        artist_dict['Genre'],  artist_dict['Rank'] = song['name'], song['rank']
    except KeyError:
        print('Error loading extra hints: Soup')

    print('Random Song: ', artist_dict['Title'])
    return artist_dict


def grab_artist(art, ret=False):
    # grabs songs from artist if update needed
    global tot_songs
    artist_dict = {}
    r_time = datetime.now()
    art_obj = genius.search_artist(art, get_full_info=False)  # max songs for debug

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


def hints(lyr, hint_ls, num):  # adds to lyrics so hint can be displayed
    hint_tot = """"""
    # loops through hints then appends
    # form_html = form_html.replace('</body>', '').replace('</html>', '')
    for hint in hint_ls:
        num += 1
        if hint in lyr.keys():
            hint_box = """
                    <tr>
                    <td>
                    <input type="checkbox" id="handle{num}" />
                    <label for="handle{num}">
                    Title
                    </label>
    
                  <div class="content">
                    <p> '{hint}: {h_val}</p>
                  </div>
                  </td>
                  </tr>""".format(num=num, hint=hint, h_val=lyr[hint])
            hint_tot += ' \n' + hint_box
    return hint_tot


def email(sub_lyr, s_info):  # todo add hints in header, check album
    # Email Output
    # Google location
    host_server = "smtp.gmail.com"
    port = 465
    msg = MIMEMultipart('alternative')
    # what to send
    msg['From'] = usr
    msg['To'] = ', '.join(receivers)  # to get string
    msg['Subject'] = 'Lyrics '

    # get html
    message_con = "Lyrics:\n {}".format(sub_lyr)  # if format won't load

    msg.attach(MIMEText(message_con, 'plain'))
    print('opening html')
    try:
        with open('LyEmail.html', 'r') as h_file:
            # replaces items so html works on qwn, but can format
            html = h_file.read().replace('{', '{{').replace('}', '}}').replace('%#', '{').replace('#%', '}')
            html = html.replace('<!--{', '{').replace('}-->', '}')
        num = html.count('handle')  # counts instances already

        h_ls = ['Album', 'Rank', 'Genre']
        html_ex = hints(s_info, h_ls, num)
        form_html = html.format(lyrics=sub_lyr, title=s_info['Title'], artist=s_info['Artist'],
                                full_lyrics=s_info['Lyrics'], extra_info=html_ex)

        msg.attach(MIMEText(form_html, 'html'))

    except FileNotFoundError as e:
        print('Error Loading HTML: ', e)
    except KeyError as e:
        print('Error Formatting HTML: ', e)

    ctx = ssl.create_default_context()
    print('Sending Email')

    with smtplib.SMTP_SSL(host_server, port, context=ctx) as server:
        server.login(usr, password)

        for receiver in receivers:
            e_time = datetime.now()
            server.sendmail(usr, receiver, msg.as_string())
            print('Time for Email: {}, {}'.format(receiver, datetime.now() - e_time))


rand_art = random.choice(artist_ls)  # index columns so dict is correct
if weekday == 6:
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
    rand_out = search_csv(artist_ls)

sub_lines = random_sub_song(rand_out)  # gets sub_lyrics
email(sub_lines, rand_out)
tot_time = datetime.now() - start_time

try:
    tps = tot_time / tot_songs
except ZeroDivisionError:
    tps = 0
time_dict['Total'] = {'Time': tot_time, 'Songs': tot_songs, 'Time per Song': tps}
write_csv('Time', time_dict)  # since index is run by dict and 'art' is name

print("Total time:",  tot_time)
print("{} Songs, at: {} per song".format(tot_songs, tps))
