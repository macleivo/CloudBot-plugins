"""
almanakka.py

Outputs whose name day it is in the Finnish, Swedish, Orthodox or Sámi calendar.

Created By:
    - Marcus Leivo

License:
    GNU General Public License (Version 3)
"""

from urllib.request import urlopen
from bs4 import BeautifulSoup as BS4

from cloudbot import hook


def almanakka_get_info():
    url = "http://almanakka.helsinki.fi/fi/"
    soossi = BS4(urlopen(url).read().decode())
    nimet = soossi.find("div", attrs={"id": "rt-sidebar-a"})
    nimet = nimet.find_all("div", attrs={"class": "module-content"})
    nimet = nimet[1]

    erikoispaiva = str(nimet.find_all("p")[0].text)
    nimet = str(nimet.find_all("p")[1])

    nimet = BS4(str(nimet).replace("<br></br>", "").replace(")", ");"))
    nimet = str(nimet.text.split(": ")[1][:-1])
    output = ""
    if erikoispaiva != "":
        output = "%s - Nimipäivää tänään viettävät: %s" % (erikoispaiva, nimet)
    else:
        output = "Nimipäivää tänään viettävät: " + nimet
    return output

@hook.command("almanakka", "tänään", "nimipäivät")
def almanakka(text):
    output = almanakka_get_info()
    return output
