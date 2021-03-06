# Lyrics
## Info
This repo contains scrips to get lyrics from genius and do various things with them.

### Dependancies
- Pandas
- Beautiful Soup
    - lxml
- Lyrics Genius

These can be installed by:
```
conda install pandas
pip install beautifulsoup4
pip install lxml
pip install lyricsgenius
```


### Required End-User Edits
- **Google api:**
To send the email, I used the *smtplib* module with google api. Thus, the sending email works better with 2 factor authentication (and an api key).
[Create App Key](https://support.google.com/accounts/answer/185833?hl=en&authuser=0)

- **Pass.txt:**
copy file (in *MiscFiles*): remove'.example' from file name and replace all non comments with your respective usernames and passwords. 
The email passwords is the api *app password* in the above step.

- **Artists:**
Replace the list of artists in *Lyrics.py* to the list of artists you want to be searched

### References
I used the package [Lyrics Genius](https://github.com/johnwmillr/LyricsGenius) by [John W. Miller](https://github.com/johnwmillr).

The code for *GrabLyr.py* is based of code from the repo [music_by_genre_analysis](https://github.com/MarkMacArdle/music_by_genre_analysis) 
by [Mark MacArdle](https://github.com/MarkMacArdle)

Thank you for your Code.


## Scripts
### Creds
Used by scripts to grab password info and stores global variables.

If there is a cleaner way of doing this please let me know.


### GrabArtist.py
Used by most Scripts. The main script. Runs to grab data about songs then saves them to a csv (so it doesn't need to grab each run). 
The scrapping from Genius takes a while. Upon startup it will check if a csv file exists for each artist.

It will then search for artists that aren't saved. 


### EmailLyrics.py 
Uses *GrabArtist.py* to update songs. It will then chose a random song from a random artist, 
and a random 5 lines from the song. It will then email the song to the receiving emails.

uses *html* for formatting the email.

On sundays, it will update all artists and will get a random song from the Billboard-Top-Charts.


### LyrEmail.html
*Html* file: opened by python; to format the email.

Python replaces *{}* when formatting, thus I have *%#* to be replaced in python. This allows the file to be able to be 
interpreted in html before formatting, and after python can insert variables correctly.


### GrabSoupLyr.py
Based on the code by Mark MacArdle. It chooses a random chart from billboard from the (inputted year/years). 
then uses Beautiful Soup to scrap the data. returns the song info.
This can then be searched in *EmailLyrics.py*


### LyricsAnalysis.py
Uses *GrabArtist.py* to get csv for particular artist.
Then uses the info to plot data relating to each album using *matplotlib*. Will display plots between albums
and for each album individually. Then saves data.


## Cron(optional)
I have this running on cron so it emails every morning

Example cron Entry:
```
# For Lyrics.py
30 7 * * * /path_to_annaconda_python /path_to_dir/EmailLyrics.py
```
