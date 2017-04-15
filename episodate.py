"""
episodate.py

Fetch information on a tv-show from episodate.com.

Created by:
    - Marcus Leivo

License:
    GNU General Public License (Version 3)
"""
import re
import requests

from bs4 import BeautifulSoup
from urllib.parse import quote

from datetime import datetime
import pytz

from cloudbot import hook


def __is_int(n):
    try:
        int(n)
        return True
    except ValueError:
        return False


def episodate_mimic_autocomplete(search_string):
    url = "https://www.episodate.com/api/search-suggestions?query="
    url += quote(search_string)
    request = requests.get(url)
    resp = request.json()

    if 'error' in resp:
        return None

    search_string = resp[0]
    return search_string


def episodate_find_show(search_string, suggestion_num):
    url = "https://www.episodate.com/search?q="
    url += quote(search_string)
    soup = BeautifulSoup(requests.get(url).text)

    x = soup.find("meta", attrs={"property": "og:url"})
    # Only one result found -> the site redirects directly to the found show.
    if x and x['content'].find("/tv-show/") != -1:
        show_name = "/tv-show/" + x['content'].split("/")[-1]
        return show_name, (0, 1)

    # Got more than one result.
    shows = soup.find_all("a", attrs={"class": "list-element", "href": True})
    found_shows = len(shows)
    if not found_shows:
        return None
    n = max(0, min(found_shows - 1, suggestion_num))

    show = shows[n]
    show_title = show['href']

    return show_title, (n, found_shows)


def episodate_calculate_time_left(seconds):
    days = int(seconds / 24 / 60 / 60)
    hours = int((seconds - days * 24 * 60 * 60) / 60 / 60)
    mins = int((seconds - days * 24 * 60 * 60 - hours * 60 * 60) / 60)
    secs = int((seconds - days * 24 * 60 * 60 - hours * 60 * 60 - mins * 60))

    output = ""
    if days > 0:
        output += "%sdays " % (days)
    if hours > 0:
        output += "%shours " % (hours)
    if mins > 0:
        output += "%smins " % (mins)
    if secs > 0:
        output += "%ssec" % (secs)

    return output


def episodate_time_left(soup):
    airtime_data = soup.find_all("span", attrs={"class": "episode-datetime-convert"})
    if not airtime_data:
        return None

    airtime_data = airtime_data[-1]
    airtime_data = airtime_data['data-datetime'][::-1].replace(":", "", 1)
    airtime_data = airtime_data[::-1]
    airtime = datetime.strptime(airtime_data, "%Y-%m-%dT%H:%M:%S%z")
    curtime = datetime.now()

    tz = pytz.timezone('Europe/Helsinki')
    utc_offset = int(tz.utcoffset(curtime).total_seconds())

    seconds_left = int(airtime.strftime('%s')) - int(curtime.strftime('%s'))
    seconds_left += utc_offset

    time_left = episodate_calculate_time_left(seconds_left)

    return time_left


def episodate_parse_misc_data(soup):
    data_1 = soup.find("div", attrs={"class": "ten wide column"})
    data_2 = soup.find("div", attrs={"class": "six wide column"})

    genres = re.sub(r'<.*?>', ' ', re.sub(r'<br.*?>', '|', str(data_1)))
    status = re.sub(r'<.*?>', ' ', re.sub(r'<br.*?>', '|', str(data_2)))

    data = "%s | %s" % (status, genres)
    data = data.split("|")

    output = ""
    for i in data:
        lol = i.split(" ")
        relevant = []
        for j in lol:
            if len(j.strip()) > 0:
                relevant.append(j.strip())
        if len(relevant) > 0:
            output += " ".join(relevant) + " | "

    return output[:-2]


def episodate_gen_output(show_url, found_show_num):
    url = "https://www.episodate.com" + show_url

    soup = BeautifulSoup(requests.get(url).text)

    show_title = soup.find("h1", attrs={"class": "title"}).text.strip()
    next_ep_in = episodate_time_left(soup)
    if not next_ep_in:
        next_ep_in = "Next air date unknown"
    else:
        next_ep_in = "Next episode in: " + next_ep_in
    misc_data = episodate_parse_misc_data(soup)

    n = found_show_num[0] + 1
    t = found_show_num[1]

    output = "%s/%s: %s | %s | %s" % (n, t, show_title, next_ep_in, misc_data)
    return output


@hook.command('episodate', 'ed')
def episodate(text):
    if not text:
        return("You need to give me a tv-show to look up!")

    args = text.split(",")
    show = args[0].strip()
    sugg_num = 0

    if len(args) >= 2 and __is_int(args[1]):
        sugg_num = int(args[1]) - 1

    found_show = episodate_find_show(show, sugg_num)
    if not found_show:
        return("No show found.")
    found_show_url = found_show[0]
    found_show_num = found_show[1]
    output = episodate_gen_output(found_show_url, found_show_num)

    return(output)
