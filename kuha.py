# coding: utf8
"""
kuha.py

Output a random quote from Lannistajakuha.

Created by:
    - Marcus Leivo

License:
    GNU General Public License (Version 3)
"""
from urllib.request import urlopen
from bs4 import BeautifulSoup

from cloudbot import hook


@hook.command('kuha')
def lannistaja_kuha(text):
    number = ""
    if text:
        try:
            number = str(int(text.split(" ")[0]))
        except:
            pass
    if len(number) > 0:
        url = urlopen("http://lannistajakuha.com/" + number).read().decode()
    else:
        url = urlopen("http://lannistajakuha.com/random").read().decode()
    soup = BeautifulSoup(url)
    result = (soup.find("p", attrs={"class": "teksti"}))
    result = result.text.strip()
    return(result)
