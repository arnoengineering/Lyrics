# Lyrics
## Info
This repo contains scrips to get lyrics from genius and do verious thing with them.
### Dependancies
1. Beautiful Soup
  1.lxml
2. Lyrics Genius
### References
I used the package [Lyrics Genius](https://github.com/johnwmillr/LyricsGenius) by [John W. Miller](https://github.com/johnwmillr).
The code for *GrabLyr.py* is based of code from the repo [music_by_genre_analysis](https://github.com/MarkMacArdle/music_by_genre_analysis) by [Mark MacArdle](https://github.com/MarkMacArdle)
Thank You for your Code.

## Scripts
### Lyrics.py 
The main script. Runs to grab data about songs then saves them to a csv (so it doesn't need to grab each run). The scrapping from Genius takes a while. Apon startup it will check if a csv file exists for each artist.
It will then search for artists that arn't saved. It will then chose a random song from a random artist, and a random 5 lines from the song. It will then email the song to the receiving emails.
uses *html* for formatting the email.

On sundays, it will update all atrists and will get a random song from the Billboard-Top-Charts.

### Html
Formats the email,
used some weird symbols, so before running script, I can look at the base html, but after python can insert variables correctly.

### GrabLyr.py
Based on the code by Mark MacArdle. It choused a random chart from bilbord from the (inputed year/years). then uses Beautiful Soup to scrap the data. returns the song info.
This can then be searched in *Lyrics.py*

### LyrAnalisis.py
Gets csv for particular artist then uses the info to plot data relating to each album using *mpltlib* 
*still in progress*
