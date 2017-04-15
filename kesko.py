"""
kesko.py

Find the opening and closing times of any Kesko grocery store.

Created by:
    - Marcus Leivo

License:
    GNU General Public License (Version 3)
"""
import json
import requests

from cloudbot import hook


@hook.command('kesko')
def keskoHaku(text):
    if not text:
        return("Tarvin jonkun paikanki!")

    args = text.split(",")
    url = "http://www.k-market.fi/api/stores/searchStores?query=%s" % (args[0].strip())
    kaupat = json.loads(requests.get(url).text)

    if len(kaupat) <= 0:
        return(u"Kauppa ei löytynyt. Keskon haku on kyllä sen verran syvältä että suosittelen hakemaan manuaalisesti " \
                + "kauppaa vaikkapa täältä: http://www.k-market.fi/kaupat/ Postinumero toimii parhaiten.")

    num = 1
    if len(args) > 1:
        try:
            num = int(args[1].strip())
            num = min(max(1, num), len(kaupat))
        except ValueError:
            pass

    kauppa = kaupat[num-1]
    output = "%s/%s %s" % (num, len(kaupat), kauppa["Name"])
    output += ", " + kauppa["StreetAddress"]
    output += ", " + kauppa["PostalCode"]
    output += "; " + kauppa["OpenToday"]
    output += "; Huomenna auki " + kauppa["OpenTomorrow"]
    return(output)
