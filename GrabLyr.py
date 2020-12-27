import random

import requests
from bs4 import BeautifulSoup as bs


def soup_lyrics(years):

    def get_chart_entries(url):
        """
        Returns a list of dictionaries with the rank, title and artist of each song
        from the chart on the passed url page
        """

        r = requests.get(url)
        soup = bs(r.content, "lxml")
        chart_entries = soup.find_all("div", attrs={"class": "ye-chart-item__primary-row"})

        chart = []
        for entry in chart_entries:
            chart.append({'rank': int(entry.find("div", attrs={"class": "ye-chart-item__rank"}).text),
                          'song': entry.find("div", attrs={"class": "ye-chart-item__title"}).text.strip(),

                          # replacing 'x' and 'X' with '&' as that's how genius.com has the names
                          # need to match so the lyrics be looked up later
                          'artist': entry.find("div",
                                               attrs={"class": "ye-chart-item__artist"}).text.strip() \
                         .replace(' x ', ' & ').replace(' X ', ' & ')})

        return chart

    charts = [{'name': 'Hot100', 'urlTag': 'hot-100-songs'},
              {'name': 'Rock', 'urlTag': 'hot-rock-songs'},
              {'name': 'Pop', 'urlTag': 'pop-songs'},
              {'name': 'Christian', 'urlTag': 'hot-christian-songs'}]

    rand_chart = random.choice(charts)
    if type(years) == list:
        year = random.choice(years)
    else:
        year = years
    rand_chart['url'] = ("https://www.billboard.com/charts/year-end/" + str(year) + '/' + rand_chart['urlTag'])

    rand_chart['entries'] = get_chart_entries(rand_chart['url'])
    rand_song = random.choice(rand_chart['entries'])
    rand_song['year'] = year
    rand_song['genre'] = rand_chart['name']
    return rand_song
